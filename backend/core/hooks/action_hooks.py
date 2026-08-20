"""Action Hooks — mandatory constraints before/after tool execution.

This module implements the fourth architectural layer: intercepting tool
execution with pre/post hooks that can BLOCK, MODIFY, or LOG actions.

Unlike event hooks (which only observe and emit events), action hooks
return a HookResult that the Agent loop must respect:

  - ALLOW: proceed with execution
  - BLOCK: refuse execution, return error message to LLM
  - MODIFY: alter tool arguments before execution
  - WARN: proceed but log a warning

Built-in hooks:
  1. DangerousCommandHook — blocks rm -rf, format, dd, etc.
  2. FileSafetyHook   — blocks writing outside workspace, blocks overwriting critical files
  3. TokenBudgetHook   — blocks LLM calls that would exceed budget

Design:
  - Hooks are registered per tool name (or "*" for all tools)
  - Pre-hooks run before tool.execute(), post-hooks run after
  - First BLOCK wins; subsequent hooks are skipped
  - All hooks are synchronous for predictable ordering
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from loguru import logger


# ---------------------------------------------------------------------------
# Enums and dataclasses
# ---------------------------------------------------------------------------


class HookEvent(Enum):
    """When the hook fires relative to tool execution."""

    PRE = "pre"  # Before tool execution (can block)
    POST = "post"  # After tool execution (can modify result)


class HookAction(Enum):
    """What the hook manager should do with the result."""

    ALLOW = "allow"  # Proceed normally
    BLOCK = "block"  # Stop execution, return error to LLM
    MODIFY = "modify"  # Replace tool arguments
    WARN = "warn"  # Proceed but log warning


@dataclass
class HookContext:
    """Context passed to every hook invocation.

    Contains everything a hook needs to make a decision.
    """

    tool_name: str
    arguments: dict[str, Any]
    event: HookEvent
    workspace: str = ""
    result: Any = None  # Only for POST hooks
    session_id: str = ""
    user_message: str = ""


@dataclass
class HookResult:
    """Result of a single hook execution."""

    action: HookAction
    message: str = ""
    modified_arguments: dict[str, Any] | None = None
    hook_name: str = ""

    @property
    def should_block(self) -> bool:
        return self.action == HookAction.BLOCK

    @property
    def should_modify(self) -> bool:
        return self.action == HookAction.MODIFY

    @property
    def allowed(self) -> bool:
        return self.action in (HookAction.ALLOW, HookAction.WARN, HookAction.MODIFY)


# ---------------------------------------------------------------------------
# Hook base class
# ---------------------------------------------------------------------------


class ActionHook:
    """Base class for action hooks.

    Subclasses implement either or both of:
      - pre_execute(ctx) -> HookResult
      - post_execute(ctx) -> HookResult

    If pre_execute returns BLOCK, the tool is not executed.
    If pre_execute returns MODIFY, the arguments are replaced.
    """

    name: str = "base"
    applies_to: tuple[str, ...] = ("*",)  # Tool names this hook applies to

    def pre_execute(self, ctx: HookContext) -> HookResult:
        """Run before tool execution. Can block or modify."""
        return HookResult(HookAction.ALLOW, hook_name=self.name)

    def post_execute(self, ctx: HookContext) -> HookResult:
        """Run after tool execution. Can warn or log."""
        return HookResult(HookAction.ALLOW, hook_name=self.name)

    def matches(self, tool_name: str) -> bool:
        """Check if this hook applies to the given tool."""
        return "*" in self.applies_to or tool_name in self.applies_to


# ---------------------------------------------------------------------------
# Built-in hooks
# ---------------------------------------------------------------------------


class DangerousCommandHook(ActionHook):
    """Blocks dangerous shell commands before execution.

    Pattern-based detection of commands that could cause irreversible damage:
    - rm -rf / rm -rf /
    - format / fdisk / dd
    - mkfs
    - chmod 777 on system dirs
    - curl/wget piped to sh
    """

    name = "dangerous_command"
    applies_to = ("shell", "exec", "execute_command", "run_command")

    # Patterns that are ALWAYS blocked (severity=error)
    BLOCKED_PATTERNS = [
        (r"rm\s+-rf\s+/(?!tmp)", "rm -rf on root filesystem"),
        (r"rm\s+-rf\s+~", "rm -rf on home directory"),
        (r"rm\s+-rf\s+\*", "rm -rf with wildcard"),
        (r"mkfs\.\w+", "Filesystem format command"),
        (r"dd\s+.*of=/dev/[sh]d", "dd writing to disk device"),
        (r"fdisk\s+/dev/[sh]d", "fdisk on disk device"),
        (r"format\s+[A-Z]:", "Windows format command"),
        (r":\(\)\{.*\|.*&.*\};", "Fork bomb"),
        (r"curl\s+.*\|\s*(sh|bash|zsh)", "Piping remote script to shell"),
        (r"wget\s+.*\|\s*(sh|bash|zsh)", "Piping remote script to shell"),
        (r"chmod\s+-R\s+777\s+/(?!tmp)", "Recursive 777 on root"),
        (r">\s*/dev/[sh]d", "Redirecting to disk device"),
        (r"shutdown|reboot|halt|poweroff", "System power control"),
    ]

    def pre_execute(self, ctx: HookContext) -> HookResult:
        command = ctx.arguments.get("command", "")
        if not command:
            return HookResult(HookAction.ALLOW, hook_name=self.name)

        for pattern, description in self.BLOCKED_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                logger.warning(f"Blocked dangerous command: {description} (pattern='{pattern}')")
                return HookResult(
                    HookAction.BLOCK,
                    message=(
                        f"Blocked by safety hook: {description}. "
                        f"This command is considered dangerous and was not executed. "
                        f"If you genuinely need to run this, ask the user to confirm."
                    ),
                    hook_name=self.name,
                )

        return HookResult(HookAction.ALLOW, hook_name=self.name)


class FileSafetyHook(ActionHook):
    """Prevents file operations outside the workspace boundary.

    Enforces:
    1. Writes must stay within workspace
    2. Critical config files (.env, credentials) cannot be overwritten
    3. Symlinks pointing outside workspace are blocked
    """

    name = "file_safety"
    applies_to = ("write_file", "edit_file", "write", "edit", "create_file")

    CRITICAL_FILES = [
        ".env",
        "credentials.json",
        ".ssh/id_rsa",
        ".aws/credentials",
        "secrets.json",
    ]

    CRITICAL_EXTENSIONS = [".pem", ".key", ".pfx"]

    def __init__(self, workspace: str = ""):
        self.workspace = Path(workspace).resolve() if workspace else Path.cwd()

    def pre_execute(self, ctx: HookContext) -> HookResult:
        file_path = ctx.arguments.get("path", "") or ctx.arguments.get("file_path", "")
        if not file_path:
            return HookResult(HookAction.ALLOW, hook_name=self.name)

        target = Path(file_path)

        # Check 1: Must be within workspace
        try:
            resolved = target.resolve()
            if not str(resolved).startswith(str(self.workspace)):
                # Allow /tmp for temporary files
                if not str(resolved).startswith("/tmp"):
                    return HookResult(
                        HookAction.BLOCK,
                        message=(
                            f"Blocked: path '{file_path}' is outside the workspace "
                            f"boundary ({self.workspace}). File operations must stay "
                            f"within the workspace."
                        ),
                        hook_name=self.name,
                    )
        except (OSError, RuntimeError):
            # Symlink resolution failure — block by default
            return HookResult(
                HookAction.BLOCK,
                message=f"Blocked: cannot resolve path '{file_path}' (possible symlink loop)",
                hook_name=self.name,
            )

        # Check 2: Critical files
        filename = target.name.lower()
        for critical in self.CRITICAL_FILES:
            if filename == critical.lower():
                return HookResult(
                    HookAction.BLOCK,
                    message=(
                        f"Blocked: '{filename}' is a critical credential file. "
                        f"Overwriting it could break authentication. "
                        f"If intentional, ask the user to confirm."
                    ),
                    hook_name=self.name,
                )

        for ext in self.CRITICAL_EXTENSIONS:
            if filename.endswith(ext):
                return HookResult(
                    HookAction.BLOCK,
                    message=(
                        f"Blocked: '{filename}' has a sensitive extension '{ext}'. "
                        f"This looks like a private key file."
                    ),
                    hook_name=self.name,
                )

        return HookResult(HookAction.ALLOW, hook_name=self.name)


class TokenBudgetHook(ActionHook):
    """Blocks LLM calls that would exceed the remaining token budget.

    This hook intercepts LLM tool calls and checks if the estimated
    token cost would exceed the session's remaining budget.
    """

    name = "token_budget"
    applies_to = ("llm", "chat", "call_llm", "ask")

    def __init__(self, budget: int = 0):
        """Initialize with total token budget.

        Args:
            budget: Maximum tokens for this session. 0 = unlimited.
        """
        self.budget = budget
        self.used = 0

    def pre_execute(self, ctx: HookContext) -> HookResult:
        if self.budget == 0:
            return HookResult(HookAction.ALLOW, hook_name=self.name)

        # Estimate token cost from messages
        messages = ctx.arguments.get("messages", [])
        estimated_tokens = sum(len(str(m.get("content", ""))) // 4 for m in messages)

        remaining = self.budget - self.used
        if estimated_tokens > remaining:
            return HookResult(
                HookAction.BLOCK,
                message=(
                    f"Blocked: estimated token cost ({estimated_tokens}) exceeds "
                    f"remaining budget ({remaining}). Used {self.used}/{self.budget}. "
                    f"Consider compressing context or reducing output length."
                ),
                hook_name=self.name,
            )

        return HookResult(HookAction.ALLOW, hook_name=self.name)

    def post_execute(self, ctx: HookContext) -> HookResult:
        if self.budget == 0:
            return HookResult(HookAction.ALLOW, hook_name=self.name)

        # Track actual usage from result
        result = ctx.result
        if isinstance(result, dict):
            usage = result.get("usage", {})
            self.used += usage.get("total_tokens", 0)

        return HookResult(HookAction.ALLOW, hook_name=self.name)


# ---------------------------------------------------------------------------
# Hook manager
# ---------------------------------------------------------------------------


class ActionHookManager:
    """Manages registration and execution of action hooks.

    The Agent loop calls this before/after every tool execution.
    First BLOCK wins; all hooks are checked in registration order.

    Usage:
        manager = ActionHookManager(workspace="/path/to/workspace")
        manager.register(DangerousCommandHook())
        manager.register(FileSafetyHook(workspace="/path/to/workspace"))

        # Before tool execution:
        pre_result = manager.run_pre("shell", {"command": "rm -rf /"})
        if pre_result.should_block:
            return error_to_llm(pre_result.message)

        # After tool execution:
        manager.run_post("shell", {"command": "..."}, result=tool_result)
    """

    def __init__(self, workspace: str = ""):
        self.workspace = workspace
        self.hooks: list[ActionHook] = []
        self.block_log: list[dict[str, Any]] = []

    def register(self, hook: ActionHook) -> None:
        """Register a hook. Hooks are executed in registration order."""
        self.hooks.append(hook)
        logger.info(f"Registered action hook: {hook.name}")

    def unregister(self, hook_name: str) -> None:
        """Remove a hook by name."""
        self.hooks = [h for h in self.hooks if h.name != hook_name]

    def run_pre(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        session_id: str = "",
        user_message: str = "",
    ) -> HookResult:
        """Run all matching pre-execution hooks.

        Args:
            tool_name: Name of the tool about to be executed.
            arguments: Tool arguments that will be passed to execute().
            session_id: Current session identifier.
            user_message: The user's original request.

        Returns:
            HookResult from the first BLOCK, or the last result.
            If any hook returns MODIFY, the arguments are updated
            in-place (caller should use modified_arguments).
        """
        ctx = HookContext(
            tool_name=tool_name,
            arguments=arguments,
            event=HookEvent.PRE,
            workspace=self.workspace,
            session_id=session_id,
            user_message=user_message,
        )

        current_args = arguments

        for hook in self.hooks:
            if not hook.matches(tool_name):
                continue

            result = hook.pre_execute(ctx)
            ctx.arguments = current_args  # Pass potentially modified args

            if result.should_block:
                self.block_log.append(
                    {
                        "hook": hook.name,
                        "tool": tool_name,
                        "arguments": arguments,
                        "reason": result.message,
                    }
                )
                logger.warning(
                    f"Pre-hook '{hook.name}' blocked tool '{tool_name}': {result.message}"
                )
                return result

            if result.should_modify and result.modified_arguments:
                current_args.update(result.modified_arguments)
                logger.info(f"Pre-hook '{hook.name}' modified arguments for '{tool_name}'")

            if result.action == HookAction.WARN:
                logger.warning(f"Pre-hook '{hook.name}' warned: {result.message}")

        return HookResult(HookAction.ALLOW, hook_name="manager")

    def run_post(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        result: Any,
        session_id: str = "",
    ) -> HookResult:
        """Run all matching post-execution hooks.

        Post-hooks cannot block (the tool already executed),
        but they can warn or log issues.
        """
        ctx = HookContext(
            tool_name=tool_name,
            arguments=arguments,
            event=HookEvent.POST,
            workspace=self.workspace,
            result=result,
            session_id=session_id,
        )

        for hook in self.hooks:
            if not hook.matches(tool_name):
                continue

            hook_result = hook.post_execute(ctx)
            if hook_result.action == HookAction.WARN:
                logger.warning(f"Post-hook '{hook.name}' warned: {hook_result.message}")

        return HookResult(HookAction.ALLOW, hook_name="manager")

    def get_block_log(self) -> list[dict[str, Any]]:
        """Return history of blocked actions for audit."""
        return self.block_log

    def clear_block_log(self) -> None:
        """Clear the block log."""
        self.block_log.clear()
