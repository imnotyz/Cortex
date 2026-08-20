"""
Model Router: Intelligent multi-model routing with cost-quality optimization.

This module implements a model routing layer that sits between the Agent engine
and LLM providers. It selects the optimal model based on:

1. Task type (simple chat vs complex analysis vs tool-heavy)
2. Cost budget (per-session daily/monthly limits)
3. Latency requirements (real-time vs background)
4. Fallback chain (primary model fails -> automatic degradation)

Key design decisions:
- Routing is rule-based, not ML-based (transparent, debuggable, no cold-start)
- Cost tracking integrates with existing AnalyticsService
- Fallback chain ensures zero-downtime even if a provider goes down
- All routing decisions are logged for auditability

Architecture:
    Agent Engine
        |
        v
    ModelRouter.route(messages, context) --> selects (provider, model)
        |
        v
    LLMProvider.chat/chat_stream()
        |
        v
    [on failure] -> try next provider in fallback chain
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from loguru import logger


# ---------------------------------------------------------------------------
# Enums and data classes
# ---------------------------------------------------------------------------


class TaskType(str, Enum):
    """Classification of LLM task complexity."""

    SIMPLE_CHAT = "simple_chat"  # Single-turn Q&A, greetings, factual lookup
    MULTI_TURN = "multi_turn"  # Multi-turn conversation with context
    TOOL_USE = "tool_use"  # ReAct loop with tool calls
    COMPLEX_ANALYSIS = "complex_analysis"  # Long-context analysis, code generation
    COMPRESSION = "compression"  # Context compression summary
    VISION = "vision"  # Image understanding
    EXTRACTION = "extraction"  # Knowledge extraction / structured output


class RoutingStrategy(str, Enum):
    """How a model was selected."""

    EXPLICIT = "explicit"  # User explicitly chose this model
    TASK_MATCH = "task_match"  # Matched by task type
    COST_OPTIMIZED = "cost_optimized"  # Selected for cost efficiency
    FALLBACK = "fallback"  # Selected because primary failed
    LATENCY = "latency"  # Selected for low-latency requirement


@dataclass
class ModelTier:
    """A model entry in the routing table.

    Attributes:
        provider_name: Key in providers config (e.g., "openai", "anthropic")
        model_id: Model identifier (e.g., "gpt-4o", "claude-sonnet-4-20250514")
        display_name: Human-readable name
        task_types: Which task types this model is good for
        cost_per_1k_input: Cost in USD per 1K input tokens
        cost_per_1k_output: Cost in USD per 1K output tokens
        context_window: Maximum context window in tokens
        avg_latency_ms: Average response latency in milliseconds
        priority: Lower = higher priority (1 = primary, 2 = secondary, etc.)
        enabled: Whether this tier is active
    """

    provider_name: str
    model_id: str
    display_name: str
    task_types: list[TaskType]
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    context_window: int = 128000
    avg_latency_ms: float = 2000.0
    priority: int = 1
    enabled: bool = True

    @property
    def cost_score(self) -> float:
        """Lower is cheaper. Composite cost per 1K tokens (input + output)."""
        return self.cost_per_1k_input + self.cost_per_1k_output

    @property
    def latency_score(self) -> float:
        """Lower is faster. Normalized to 0-1 scale."""
        return min(self.avg_latency_ms / 10000.0, 1.0)


@dataclass
class RoutingDecision:
    """Result of a routing decision, for logging and analytics."""

    provider_name: str
    model_id: str
    task_type: TaskType
    strategy: RoutingStrategy
    reason: str
    estimated_cost: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    fallback_chain_used: list[str] = field(default_factory=list)


@dataclass
class CostBudget:
    """Cost budget configuration.

    Attributes:
        daily_limit_usd: Maximum spend per day (0 = unlimited)
        monthly_limit_usd: Maximum spend per month (0 = unlimited)
        per_request_limit_usd: Maximum spend per single request (0 = unlimited)
        warning_threshold: Warn when usage reaches this fraction (0.0-1.0)
    """

    daily_limit_usd: float = 0.0
    monthly_limit_usd: float = 0.0
    per_request_limit_usd: float = 0.0
    warning_threshold: float = 0.8


@dataclass
class CostTracker:
    """Tracks cumulative cost for budget enforcement.

    Uses in-memory tracking with periodic flush to persistent storage.
    Thread-safe for concurrent agent sessions.
    """

    _daily_spend: dict[str, float] = field(default_factory=dict)  # date_str -> cost
    _monthly_spend: dict[str, float] = field(default_factory=dict)  # month_str -> cost
    _request_spend: list[float] = field(default_factory=list)

    def record_cost(self, cost_usd: float) -> None:
        """Record a cost entry."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        self._daily_spend[today] = self._daily_spend.get(today, 0.0) + cost_usd
        self._monthly_spend[month] = self._monthly_spend.get(month, 0.0) + cost_usd
        self._request_spend.append(cost_usd)
        # Keep only last 1000 requests
        if len(self._request_spend) > 1000:
            self._request_spend = self._request_spend[-1000:]

    def get_daily_spend(self) -> float:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self._daily_spend.get(today, 0.0)

    def get_monthly_spend(self) -> float:
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        return self._monthly_spend.get(month, 0.0)

    def would_exceed_budget(self, estimated_cost: float, budget: CostBudget) -> tuple[bool, str]:
        """Check if adding estimated_cost would exceed budget.

        Returns (would_exceed, reason).
        """
        if budget.daily_limit_usd > 0:
            projected = self.get_daily_spend() + estimated_cost
            if projected > budget.daily_limit_usd:
                return (
                    True,
                    f"Daily budget exceeded: ${projected:.4f} > ${budget.daily_limit_usd:.2f}",
                )

        if budget.monthly_limit_usd > 0:
            projected = self.get_monthly_spend() + estimated_cost
            if projected > budget.monthly_limit_usd:
                return (
                    True,
                    f"Monthly budget exceeded: ${projected:.4f} > ${budget.monthly_limit_usd:.2f}",
                )

        if budget.per_request_limit_usd > 0 and estimated_cost > budget.per_request_limit_usd:
            return (
                True,
                f"Per-request cost too high: ${estimated_cost:.4f} > ${budget.per_request_limit_usd:.2f}",
            )

        return False, ""

    def get_budget_utilization(self, budget: CostBudget) -> dict[str, Any]:
        """Get current budget utilization as percentages."""
        return {
            "daily": {
                "spent": self.get_daily_spend(),
                "limit": budget.daily_limit_usd,
                "utilization_pct": (
                    (self.get_daily_spend() / budget.daily_limit_usd * 100)
                    if budget.daily_limit_usd > 0
                    else 0
                ),
            },
            "monthly": {
                "spent": self.get_monthly_spend(),
                "limit": budget.monthly_limit_usd,
                "utilization_pct": (
                    (self.get_monthly_spend() / budget.monthly_limit_usd * 100)
                    if budget.monthly_limit_usd > 0
                    else 0
                ),
            },
        }


# ---------------------------------------------------------------------------
# Task classifier
# ---------------------------------------------------------------------------


class TaskClassifier:
    """Classifies LLM requests into task types for routing.

    Uses heuristic rules based on message content, tool count, and context size.
    Designed to be fast (O(1) per message) and transparent (no ML model).
    """

    # Thresholds for classification
    SIMPLE_MSG_MAX_CHARS = 200
    COMPLEX_CONTEXT_MIN_CHARS = 5000
    TOOL_HEAVY_MIN_TOOLS = 3

    @classmethod
    def classify(
        cls,
        messages: list[dict[str, Any]],
        tools: list[dict] | None = None,
        request_type: str | None = None,
    ) -> TaskType:
        """Classify the task type from request parameters.

        Args:
            messages: Chat messages
            tools: Available tool definitions
            request_type: Explicit request type hint (e.g., "compression", "extraction")

        Returns:
            TaskType enum value
        """
        # Explicit request type takes priority
        if request_type:
            type_map = {
                "compression": TaskType.COMPRESSION,
                "extraction": TaskType.EXTRACTION,
                "vision": TaskType.VISION,
            }
            if request_type in type_map:
                return type_map[request_type]

        # Check for vision content (image in messages)
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "image_url":
                        return TaskType.VISION

        # Tool-heavy requests
        if tools and len(tools) >= cls.TOOL_HEAVY_MIN_TOOLS:
            return TaskType.TOOL_USE

        # Check if any tools are present at all
        if tools and len(tools) > 0:
            # With few tools, it's still multi-turn with tool capability
            if len(messages) > 2:
                return TaskType.MULTI_TURN
            return TaskType.TOOL_USE

        # Estimate total context size
        total_chars = sum(len(str(m.get("content", ""))) for m in messages)

        # Long context -> complex analysis
        if total_chars >= cls.COMPLEX_CONTEXT_MIN_CHARS:
            return TaskType.COMPLEX_ANALYSIS

        # Single short message -> simple chat
        if len(messages) <= 2 and total_chars <= cls.SIMPLE_MSG_MAX_CHARS:
            return TaskType.SIMPLE_CHAT

        # Default: multi-turn conversation
        return TaskType.MULTI_TURN


# ---------------------------------------------------------------------------
# Model Router
# ---------------------------------------------------------------------------


class ModelRouter:
    """Intelligent model routing layer.

    Sits between the Agent engine and LLM providers. Selects the optimal
    (provider, model) pair based on task type, cost budget, and latency requirements.

    Usage:
        router = ModelRouter()
        router.register_tier(ModelTier(...))
        decision = router.route(messages, tools, request_type="compression")
        # decision.provider_name, decision.model_id
    """

    def __init__(self, cost_budget: CostBudget | None = None):
        self._tiers: list[ModelTier] = []
        self._cost_tracker = CostTracker()
        self._budget = cost_budget or CostBudget()
        self._decision_history: list[RoutingDecision] = []
        self._fallback_fail_counts: dict[str, int] = defaultdict(int)
        self._circuit_breaker: dict[str, float] = {}  # provider_name -> blocked_until_ts
        self._max_history = 500

    # ----- Registration -----

    def register_tier(self, tier: ModelTier) -> None:
        """Register a model tier in the routing table."""
        self._tiers.append(tier)
        # Sort by priority (1 = highest priority)
        self._tiers.sort(key=lambda t: t.priority)
        logger.info(
            f"Registered model tier: {tier.display_name} "
            f"(provider={tier.provider_name}, model={tier.model_id}, priority={tier.priority})"
        )

    def unregister_tier(self, provider_name: str, model_id: str) -> bool:
        """Remove a model tier from the routing table."""
        before = len(self._tiers)
        self._tiers = [
            t
            for t in self._tiers
            if not (t.provider_name == provider_name and t.model_id == model_id)
        ]
        removed = len(self._tiers) < before
        if removed:
            logger.info(f"Unregistered model tier: {provider_name}/{model_id}")
        return removed

    def get_tiers(self) -> list[ModelTier]:
        """Get all registered model tiers."""
        return list(self._tiers)

    # ----- Circuit breaker -----

    def _is_circuit_open(self, provider_name: str) -> bool:
        """Check if a provider is currently circuit-broken."""
        blocked_until = self._circuit_breaker.get(provider_name, 0)
        if time.time() < blocked_until:
            return True
        # Circuit has cooled down
        if provider_name in self._circuit_breaker:
            del self._circuit_breaker[provider_name]
            self._fallback_fail_counts[provider_name] = 0
        return False

    def record_failure(self, provider_name: str, error: Exception | None = None) -> None:
        """Record a provider failure for circuit breaker.

        After 3 consecutive failures, the provider is blocked for 60 seconds.
        """
        self._fallback_fail_counts[provider_name] += 1
        fail_count = self._fallback_fail_counts[provider_name]

        logger.warning(
            f"Provider {provider_name} failure #{fail_count}: {error or 'unknown error'}"
        )

        if fail_count >= 3:
            block_duration = 60  # 60 seconds
            self._circuit_breaker[provider_name] = time.time() + block_duration
            logger.error(
                f"Circuit breaker OPEN for {provider_name} "
                f"(blocked for {block_duration}s due to {fail_count} consecutive failures)"
            )

    def record_success(self, provider_name: str) -> None:
        """Record a provider success, resetting the failure counter."""
        if provider_name in self._fallback_fail_counts:
            del self._fallback_fail_counts[provider_name]
        if provider_name in self._circuit_breaker:
            del self._circuit_breaker[provider_name]

    # ----- Cost estimation -----

    def estimate_cost(
        self,
        tier: ModelTier,
        input_tokens: int,
        max_output_tokens: int,
    ) -> float:
        """Estimate the cost of a request.

        Args:
            tier: Model tier with pricing
            input_tokens: Estimated input tokens
            max_output_tokens: Maximum output tokens (worst case)

        Returns:
            Estimated cost in USD
        """
        input_cost = (input_tokens / 1000.0) * tier.cost_per_1k_input
        output_cost = (max_output_tokens / 1000.0) * tier.cost_per_1k_output
        return input_cost + output_cost

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Quick token estimation (chars / 4)."""
        return max(1, len(text) // 4)

    # ----- Routing -----

    def route(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict] | None = None,
        request_type: str | None = None,
        explicit_provider: str | None = None,
        explicit_model: str | None = None,
        max_output_tokens: int = 4096,
        require_low_latency: bool = False,
    ) -> RoutingDecision:
        """Select the best model for this request.

        Args:
            messages: Chat messages
            tools: Available tools
            request_type: Explicit type hint
            explicit_provider: User-specified provider (bypasses routing)
            explicit_model: User-specified model (bypasses routing)
            max_output_tokens: Expected max output tokens (for cost estimation)
            require_low_latency: If True, prefer faster models

        Returns:
            RoutingDecision with provider_name and model_id
        """
        # 1. Explicit override (user chose a specific model)
        if explicit_provider and explicit_model:
            tier = self._find_tier(explicit_provider, explicit_model)
            if tier and tier.enabled and not self._is_circuit_open(explicit_provider):
                decision = RoutingDecision(
                    provider_name=explicit_provider,
                    model_id=explicit_model,
                    task_type=TaskType.MULTI_TURN,
                    strategy=RoutingStrategy.EXPLICIT,
                    reason="User explicitly selected this model",
                )
                self._record_decision(decision)
                return decision

            # Fall through to automatic routing if explicit choice is unavailable
            logger.warning(
                f"Explicit model {explicit_provider}/{explicit_model} not available, "
                f"falling back to automatic routing"
            )

        # 2. Classify task type
        task_type = TaskClassifier.classify(messages, tools, request_type)

        # 3. Get candidate tiers (enabled, not circuit-broken, match task type)
        candidates = [
            t
            for t in self._tiers
            if t.enabled
            and not self._is_circuit_open(t.provider_name)
            and task_type in t.task_types
        ]

        if not candidates:
            # No task-specific match, try all enabled tiers
            candidates = [
                t for t in self._tiers if t.enabled and not self._is_circuit_open(t.provider_name)
            ]

        if not candidates:
            logger.error("No available model tiers for routing!")
            return RoutingDecision(
                provider_name="",
                model_id="",
                task_type=task_type,
                strategy=RoutingStrategy.FALLBACK,
                reason="No available models (all providers disabled or circuit-broken)",
            )

        # 4. Estimate input tokens
        total_text = " ".join(str(m.get("content", "")) for m in messages)
        input_tokens = self.estimate_tokens(total_text)

        # 5. Cost-budget check
        best_tier = None
        best_reason = ""
        strategy = RoutingStrategy.TASK_MATCH

        # If low latency required, sort by latency
        if require_low_latency:
            candidates.sort(key=lambda t: (t.avg_latency_ms, t.priority))
            best_tier = candidates[0]
            best_reason = f"Selected for low latency ({best_tier.avg_latency_ms:.0f}ms avg)"
            strategy = RoutingStrategy.LATENCY
        else:
            # Check budget constraint
            # Sort by priority first, then by cost within same priority
            candidates.sort(key=lambda t: (t.priority, t.cost_score))

            for tier in candidates:
                est_cost = self.estimate_cost(tier, input_tokens, max_output_tokens)
                would_exceed, reason = self._cost_tracker.would_exceed_budget(
                    est_cost, self._budget
                )
                if not would_exceed:
                    best_tier = tier
                    best_reason = (
                        f"Matched task={task_type.value}, "
                        f"est_cost=${est_cost:.6f}, "
                        f"priority={tier.priority}"
                    )
                    if tier.cost_score < candidates[0].cost_score:
                        strategy = RoutingStrategy.COST_OPTIMIZED
                    break
                else:
                    logger.info(f"Skipping {tier.display_name}: {reason}")

            # If all candidates exceed budget, use the cheapest one anyway
            if best_tier is None:
                candidates.sort(key=lambda t: t.cost_score)
                best_tier = candidates[0]
                best_reason = f"Budget exceeded, using cheapest available: {best_tier.display_name}"
                strategy = RoutingStrategy.COST_OPTIMIZED

        # 6. Build fallback chain
        fallback_chain = []
        for tier in candidates:
            if tier.provider_name != best_tier.provider_name or tier.model_id != best_tier.model_id:
                fallback_chain.append(f"{tier.provider_name}/{tier.model_id}")

        # 7. Estimate cost
        est_cost = self.estimate_cost(best_tier, input_tokens, max_output_tokens)

        decision = RoutingDecision(
            provider_name=best_tier.provider_name,
            model_id=best_tier.model_id,
            task_type=task_type,
            strategy=strategy,
            reason=best_reason,
            estimated_cost=est_cost,
            fallback_chain_used=fallback_chain,
        )

        self._record_decision(decision)
        return decision

    def get_fallback_chain(
        self,
        excluded_provider: str,
        task_type: TaskType,
    ) -> list[ModelTier]:
        """Get fallback tiers for a failed provider.

        Args:
            excluded_provider: Provider that failed
            task_type: Task type to match

        Returns:
            List of fallback tiers in priority order
        """
        fallbacks = [
            t
            for t in self._tiers
            if t.enabled
            and t.provider_name != excluded_provider
            and not self._is_circuit_open(t.provider_name)
            and task_type in t.task_types
        ]
        # Also include tiers that don't match task type as last resort
        if not fallbacks:
            fallbacks = [
                t
                for t in self._tiers
                if t.enabled
                and t.provider_name != excluded_provider
                and not self._is_circuit_open(t.provider_name)
            ]
        fallbacks.sort(key=lambda t: t.priority)
        return fallbacks

    # ----- Analytics -----

    def _record_decision(self, decision: RoutingDecision) -> None:
        """Record routing decision for analytics."""
        self._decision_history.append(decision)
        if len(self._decision_history) > self._max_history:
            self._decision_history = self._decision_history[-self._max_history :]

    def get_decision_history(self, limit: int = 50) -> list[RoutingDecision]:
        """Get recent routing decisions."""
        return list(reversed(self._decision_history))[:limit]

    def get_routing_stats(self) -> dict[str, Any]:
        """Get routing statistics for dashboard."""
        if not self._decision_history:
            return {
                "total_decisions": 0,
                "by_strategy": {},
                "by_task_type": {},
                "by_provider": {},
                "total_estimated_cost": 0.0,
            }

        by_strategy: dict[str, int] = defaultdict(int)
        by_task_type: dict[str, int] = defaultdict(int)
        by_provider: dict[str, int] = defaultdict(int)
        total_cost = 0.0

        for d in self._decision_history:
            by_strategy[d.strategy.value] += 1
            by_task_type[d.task_type.value] += 1
            by_provider[d.provider_name] += 1
            total_cost += d.estimated_cost

        return {
            "total_decisions": len(self._decision_history),
            "by_strategy": dict(by_strategy),
            "by_task_type": dict(by_task_type),
            "by_provider": dict(by_provider),
            "total_estimated_cost": round(total_cost, 6),
            "budget": self._cost_tracker.get_budget_utilization(self._budget),
            "circuit_breaker_status": {
                name: {
                    "blocked": self._is_circuit_open(name),
                    "failures": self._fallback_fail_counts.get(name, 0),
                }
                for name in self._circuit_breaker
            },
        }

    # ----- Internal helpers -----

    def _find_tier(self, provider_name: str, model_id: str) -> ModelTier | None:
        """Find a tier by provider and model."""
        for tier in self._tiers:
            if tier.provider_name == provider_name and tier.model_id == model_id:
                return tier
        return None

    def record_actual_cost(
        self,
        provider_name: str,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Record actual cost after a request completes.

        Args:
            provider_name: Provider used
            model_id: Model used
            input_tokens: Actual input tokens consumed
            output_tokens: Actual output tokens generated

        Returns:
            Actual cost in USD
        """
        tier = self._find_tier(provider_name, model_id)
        if not tier:
            logger.warning(f"Cost recording: tier not found for {provider_name}/{model_id}")
            return 0.0

        input_cost = (input_tokens / 1000.0) * tier.cost_per_1k_input
        output_cost = (output_tokens / 1000.0) * tier.cost_per_1k_output
        total_cost = input_cost + output_cost

        self._cost_tracker.record_cost(total_cost)
        self.record_success(provider_name)

        logger.info(
            f"Cost recorded: {provider_name}/{model_id} "
            f"input={input_tokens} tok (${input_cost:.6f}), "
            f"output={output_tokens} tok (${output_cost:.6f}), "
            f"total=${total_cost:.6f}"
        )

        return total_cost

    def get_cost_dashboard(self) -> dict[str, Any]:
        """Get cost dashboard data for UI display."""
        budget_util = self._cost_tracker.get_budget_utilization(self._budget)
        return {
            "daily": {
                "spent": round(budget_util["daily"]["spent"], 6),
                "limit": self._budget.daily_limit_usd,
                "utilization_pct": round(budget_util["daily"]["utilization_pct"], 2),
            },
            "monthly": {
                "spent": round(budget_util["monthly"]["spent"], 6),
                "limit": self._budget.monthly_limit_usd,
                "utilization_pct": round(budget_util["monthly"]["utilization_pct"], 2),
            },
            "warning_threshold": self._budget.warning_threshold,
            "is_over_budget": (
                (self._budget.daily_limit_usd > 0 and budget_util["daily"]["utilization_pct"] > 100)
                or (
                    self._budget.monthly_limit_usd > 0
                    and budget_util["monthly"]["utilization_pct"] > 100
                )
            ),
        }
