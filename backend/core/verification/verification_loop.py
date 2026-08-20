"""Verification Loop — Agent self-verification before task completion.

This module implements the sixth architectural layer: an in-agent verification
step that runs *before* the Agent declares a task complete. It prevents the
common failure mode where the LLM says "done" but the output is wrong,
incomplete, or contains hallucinated content.

Design principles (inspired by Claude Code's verification loop):
1. Never trust LLM self-reporting — verify with concrete checks
2. Different task types need different verification strategies
3. Verification should be cheap (local checks) before expensive (LLM judge)
4. Failed verification sends the Agent back for another iteration

Verification chain (ordered by cost):
  1. Structural check   — file exists? output format correct?
  2. Completeness check  — all required sections present?
  3. Constraint check    — within token limit? no forbidden content?
  4. LLM judge           — quality assessment (most expensive, last resort)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from loguru import logger


# ---------------------------------------------------------------------------
# Enums and dataclasses
# ---------------------------------------------------------------------------


class TaskType(Enum):
    """Classifies the task to select appropriate verification strategies."""

    CODE = "code"
    DOCUMENT = "document"
    DATA = "data"
    RESEARCH = "research"
    GENERAL = "general"


class CheckStatus(Enum):
    """Result status of a single verification check."""

    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"  # Check not applicable to this task


@dataclass
class CheckResult:
    """Result of a single verification check."""

    name: str
    status: CheckStatus
    detail: str = ""
    severity: str = "info"  # info, warning, error


@dataclass
class VerificationResult:
    """Aggregated result of all verification checks for a task."""

    passed: bool
    task_type: TaskType
    checks: list[CheckResult] = field(default_factory=list)
    iteration: int = 0
    feedback: str = ""
    max_retries: int = 2

    @property
    def should_retry(self) -> bool:
        """Whether the Agent should retry the task after failed verification."""
        return not self.passed and self.iteration < self.max_retries

    @property
    def failed_checks(self) -> list[CheckResult]:
        """Only the checks that failed."""
        return [c for c in self.checks if c.status == CheckStatus.FAIL]

    def add_feedback(self, message: str) -> None:
        """Append feedback for the retry iteration."""
        if self.feedback:
            self.feedback += "\n"
        self.feedback += f"[{self.iteration}] {message}"


# ---------------------------------------------------------------------------
# Verification strategies (each is a callable check)
# ---------------------------------------------------------------------------


class VerificationStrategy:
    """Base class for verification strategies.

    A strategy is a single check that inspects the Agent's output
    and returns a CheckResult. Strategies are composed into a chain
    by VerificationLoop.
    """

    name: str = "base"

    def check(
        self,
        output: str,
        task_type: TaskType,
        context: dict[str, Any] | None = None,
    ) -> CheckResult:
        """Run the check and return result.

        Args:
            output: The Agent's final output text.
            task_type: The classified task type.
            context: Optional context (files_modified, tool_results, etc.)

        Returns:
            CheckResult with status PASS/FAIL/SKIP.
        """
        raise NotImplementedError


# --- Concrete strategies --------------------------------------------------


class StructuralCheck(VerificationStrategy):
    """Verifies output is structurally valid (not empty, not error text)."""

    name = "structural"

    ERROR_PATTERNS = [
        r"^(Error|Traceback|Exception):",
        r"^(I cannot|I can't|I am unable to)",
        r"^(Sorry|Apolog)",
        r"^(未知|无法|抱歉|出错)",
    ]

    def check(self, output: str, task_type: TaskType, context=None) -> CheckResult:
        if not output or not output.strip():
            return CheckResult(self.name, CheckStatus.FAIL, "Output is empty", "error")

        for pattern in self.ERROR_PATTERNS:
            if re.match(pattern, output.strip(), re.IGNORECASE):
                return CheckResult(
                    self.name,
                    CheckStatus.FAIL,
                    f"Output looks like an error/apology: matches '{pattern}'",
                    "error",
                )

        return CheckResult(self.name, CheckStatus.PASS, "Output is structurally valid")


class CompletenessCheck(VerificationStrategy):
    """Verifies output contains expected sections based on task type."""

    name = "completeness"

    EXPECTED_SECTIONS = {
        TaskType.CODE: ["explanation", "code"],
        TaskType.DOCUMENT: ["summary", "detail"],
        TaskType.DATA: ["data", "analysis"],
        TaskType.RESEARCH: ["findings", "source"],
        TaskType.GENERAL: [],
    }

    # Heuristic markers (lowercase substrings to look for)
    SECTION_MARKERS = {
        "explanation": ["explanation", "说明", "原理", "思路", "实现"],
        "code": ["```", "def ", "class ", "function ", "import "],
        "summary": ["summary", "总结", "概述", "摘要", "结论"],
        "detail": ["detail", "详细", "具体", "步骤"],
        "data": ["|", "table", "表格", "数据", "result"],
        "analysis": ["analysis", "分析", "趋势", "洞察", "建议"],
        "findings": ["finding", "发现", "结果", "调研"],
        "source": ["source", "来源", "参考", "引用", "http"],
    }

    def check(self, output: str, task_type: TaskType, context=None) -> CheckResult:
        expected = self.EXPECTED_SECTIONS.get(task_type, [])
        if not expected:
            return CheckResult(
                self.name, CheckStatus.SKIP, "No expected sections for general tasks"
            )

        output_lower = output.lower()
        missing = []
        for section in expected:
            markers = self.SECTION_MARKERS.get(section, [])
            if not any(m in output_lower for m in markers):
                missing.append(section)

        if missing:
            return CheckResult(
                self.name,
                CheckStatus.FAIL,
                f"Missing expected sections: {', '.join(missing)}",
                "warning",
            )

        return CheckResult(
            self.name, CheckStatus.PASS, f"All {len(expected)} expected sections present"
        )


class ConstraintCheck(VerificationStrategy):
    """Verifies output meets constraints (length, forbidden content)."""

    name = "constraint"

    FORBIDDEN_PATTERNS = [
        r"\[PLACEHOLDER\]",
        r"\[TODO\]",
        r"\[INSERT.*HERE\]",
        r"<your-.*>",
        r"Lorem ipsum",
    ]

    MAX_OUTPUT_LENGTH = 50000  # 50K chars sanity limit

    def __init__(self, max_length: int | None = None, forbidden: list[str] | None = None):
        self.max_length = max_length or self.MAX_OUTPUT_LENGTH
        if forbidden:
            self.FORBIDDEN_PATTERNS = forbidden

    def check(self, output: str, task_type: TaskType, context=None) -> CheckResult:
        # Length check
        if len(output) > self.max_length:
            return CheckResult(
                self.name,
                CheckStatus.FAIL,
                f"Output exceeds max length: {len(output)} > {self.max_length}",
                "warning",
            )

        # Forbidden content check
        for pattern in self.FORBIDDEN_PATTERNS:
            matches = re.findall(pattern, output, re.IGNORECASE)
            if matches:
                return CheckResult(
                    self.name,
                    CheckStatus.FAIL,
                    f"Contains forbidden pattern '{pattern}': {len(matches)} matches",
                    "error",
                )

        return CheckResult(self.name, CheckStatus.PASS, "No constraint violations")


class FileIntegrityCheck(VerificationStrategy):
    """If files were modified, verify they actually exist and are non-empty."""

    name = "file_integrity"

    def check(self, output: str, task_type: TaskType, context=None) -> CheckResult:
        if not context:
            return CheckResult(self.name, CheckStatus.SKIP, "No context provided")

        files_modified = context.get("files_modified", [])
        if not files_modified:
            return CheckResult(self.name, CheckStatus.SKIP, "No files were modified")

        issues = []
        for file_path in files_modified:
            path = Path(file_path)
            if not path.exists():
                issues.append(f"File does not exist: {file_path}")
            elif path.stat().st_size == 0:
                issues.append(f"File is empty: {file_path}")

        if issues:
            return CheckResult(
                self.name,
                CheckStatus.FAIL,
                f"File integrity issues: {'; '.join(issues)}",
                "error",
            )

        return CheckResult(
            self.name,
            CheckStatus.PASS,
            f"All {len(files_modified)} modified files verified",
        )


class TaskClassifier:
    """Classifies the task type from the user's request and Agent output.

    This is a lightweight heuristic classifier — not an LLM call.
    It inspects keywords in the input/output to determine task type.
    """

    KEYWORDS = {
        TaskType.CODE: [
            "code",
            "function",
            "bug",
            "fix",
            "implement",
            "refactor",
            "代码",
            "函数",
            "bug",
            "修复",
            "实现",
            "重构",
        ],
        TaskType.DOCUMENT: [
            "write",
            "document",
            "report",
            "summary",
            "draft",
            "写",
            "文档",
            "报告",
            "总结",
            "草稿",
        ],
        TaskType.DATA: [
            "data",
            "csv",
            "excel",
            "analyze",
            "chart",
            "statistics",
            "数据",
            "分析",
            "图表",
            "统计",
        ],
        TaskType.RESEARCH: [
            "research",
            "investigate",
            "compare",
            "survey",
            "study",
            "调研",
            "研究",
            "对比",
            "调查",
        ],
    }

    @classmethod
    def classify(cls, user_request: str, agent_output: str = "") -> TaskType:
        """Classify the task type from keywords.

        Args:
            user_request: The original user request.
            agent_output: The Agent's output (optional, for refinement).

        Returns:
            The most likely TaskType. Defaults to GENERAL.
        """
        combined = f"{user_request} {agent_output}".lower()

        scores: dict[TaskType, int] = {t: 0 for t in TaskType}
        for task_type, keywords in cls.KEYWORDS.items():
            for kw in keywords:
                if kw in combined:
                    scores[task_type] += 1

        best_type = max(scores, key=scores.get)
        if scores[best_type] == 0:
            return TaskType.GENERAL
        return best_type


# ---------------------------------------------------------------------------
# The verification loop
# ---------------------------------------------------------------------------


class VerificationLoop:
    """Orchestrates the verification chain before task completion.

    Usage:
        loop = VerificationLoop()
        result = loop.verify(output, user_request, context)
        if result.should_retry:
            # Send feedback back to Agent for another iteration
            agent.retry(result.feedback)
        else:
            # Task is complete (either passed or exhausted retries)
            agent.finish()

    The verification loop runs checks in order of cost:
    1. Structural (O(1) regex)
    2. Completeness (O(n) keyword scan)
    3. Constraint (O(n) regex)
    4. File integrity (filesystem stat)
    5. LLM judge (optional, external — not run by default)

    If any check fails, the loop short-circuits and returns feedback
    for the retry iteration.
    """

    def __init__(
        self,
        strategies: list[VerificationStrategy] | None = None,
        max_retries: int = 2,
    ):
        self.strategies = strategies or self._default_strategies()
        self.max_retries = max_retries

    @staticmethod
    def _default_strategies() -> list[VerificationStrategy]:
        """Default verification chain, ordered by cost."""
        return [
            StructuralCheck(),
            CompletenessCheck(),
            ConstraintCheck(),
            FileIntegrityCheck(),
        ]

    def verify(
        self,
        output: str,
        user_request: str = "",
        context: dict[str, Any] | None = None,
        task_type: TaskType | None = None,
        iteration: int = 0,
    ) -> VerificationResult:
        """Run all verification checks on the Agent's output.

        Args:
            output: The Agent's final output text.
            user_request: The original user request (for task classification).
            context: Optional dict with keys like 'files_modified', 'tool_results'.
            task_type: Override task classification if known.
            iteration: Current retry iteration (0 = first attempt).

        Returns:
            VerificationResult with aggregated check results and feedback.
        """
        if task_type is None:
            task_type = TaskClassifier.classify(user_request, output)

        result = VerificationResult(
            passed=True,
            task_type=task_type,
            iteration=iteration,
            max_retries=self.max_retries,
        )

        for strategy in self.strategies:
            try:
                check_result = strategy.check(output, task_type, context)
                result.checks.append(check_result)

                if check_result.status == CheckStatus.FAIL:
                    result.passed = False
                    result.add_feedback(
                        f"Check '{check_result.name}' failed: {check_result.detail}"
                    )
                    logger.warning(
                        f"Verification check '{check_result.name}' failed: {check_result.detail}"
                    )
                    # Short-circuit on error severity (but not warning)
                    if check_result.severity == "error":
                        break

            except Exception as e:
                logger.error(f"Verification strategy '{strategy.name}' raised: {e}")
                result.checks.append(
                    CheckResult(
                        strategy.name,
                        CheckStatus.FAIL,
                        f"Strategy error: {e}",
                        "error",
                    )
                )
                result.passed = False
                break

        if result.passed:
            logger.info(
                f"Verification passed (task_type={task_type.value}, "
                f"checks={len(result.checks)}, iteration={iteration})"
            )
        else:
            logger.warning(
                f"Verification failed (task_type={task_type.value}, "
                f"iteration={iteration}, retries_left={self.max_retries - iteration})"
            )

        return result

    def build_retry_prompt(self, result: VerificationResult) -> str:
        """Build a feedback prompt for the Agent's retry iteration.

        This prompt is injected into the Agent's context to guide
        the next attempt.

        Args:
            result: The failed VerificationResult.

        Returns:
            A feedback string to append to the Agent's messages.
        """
        if result.passed:
            return ""

        lines = [
            "[VERIFICATION FEEDBACK]",
            f"Task type: {result.task_type.value}",
            f"Iteration: {result.iteration}/{result.max_retries}",
            "",
            "The following checks failed:",
        ]

        for check in result.failed_checks:
            lines.append(f"  - {check.name}: {check.detail}")

        lines.extend(
            [
                "",
                "Please address these issues and provide a corrected response.",
            ]
        )

        return "\n".join(lines)
