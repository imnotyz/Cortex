"""
Error Recovery Manager: Automatic retry, graceful degradation, and user notification.

When an agent task fails, this module provides a structured recovery flow:

1. Retry with exponential backoff (configurable max retries)
2. If retry exhausted, try model degradation (switch to cheaper/faster model)
3. If degradation fails, try context simplification (compress context and retry)
4. If all automated recovery fails, send user notification with actionable info

The recovery flow is designed to be:
- Transparent: All recovery actions are logged and visible to the user
- Non-destructive: Never modifies user data or session state permanently
- Configurable: Each stage can be enabled/disabled via config
"""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from loguru import logger


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class RecoveryAction(str, Enum):
    """Types of recovery actions."""

    RETRY = "retry"  # Retry same provider/model
    MODEL_FALLBACK = "model_fallback"  # Switch to fallback model
    CONTEXT_COMPRESS = "context_compress"  # Compress context and retry
    USER_NOTIFY = "user_notify"  # Notify user of failure
    GIVE_UP = "give_up"  # All recovery exhausted


class ErrorSeverity(str, Enum):
    """Error severity levels for notification."""

    INFO = "info"  # Recovered automatically, user informed
    WARNING = "warning"  # Degraded performance, user should know
    ERROR = "error"  # Task failed, user needs to take action
    CRITICAL = "critical"  # System-level failure, user must intervene


class TaskStatus(str, Enum):
    """Status of a task being processed with recovery."""

    RUNNING = "running"
    RETRYING = "retrying"
    DEGRADED = "degraded"  # Running on fallback model
    RECOVERED = "recovered"  # Succeeded after recovery
    FAILED = "failed"  # All recovery exhausted
    NOTIFIED = "notified"  # User has been notified


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class ErrorEvent:
    """A single error event in the recovery chain."""

    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    error_type: str = ""
    error_message: str = ""
    provider_name: str = ""
    model_id: str = ""
    action_taken: RecoveryAction = RecoveryAction.RETRY
    retry_attempt: int = 0
    context_tokens_at_failure: int = 0


@dataclass
class RecoveryConfig:
    """Configuration for error recovery behavior.

    Attributes:
        max_retries: Maximum retry attempts before trying fallback (default: 3)
        retry_base_delay: Base delay in seconds for exponential backoff
        retry_max_delay: Maximum delay between retries
        enable_model_fallback: If True, try switching models when retries exhausted
        enable_context_compression: If True, try compressing context as last resort
        enable_user_notification: If True, notify user on unrecoverable failures
        notification_cooldown_seconds: Minimum seconds between notifications for same error type
    """

    max_retries: int = 3
    retry_base_delay: float = 1.0
    retry_max_delay: float = 30.0
    enable_model_fallback: bool = True
    enable_context_compression: bool = True
    enable_user_notification: bool = True
    notification_cooldown_seconds: float = 300.0  # 5 minutes


@dataclass
class RecoveryResult:
    """Result of a recovery attempt."""

    success: bool
    action: RecoveryAction
    error_events: list[ErrorEvent] = field(default_factory=list)
    final_provider: str = ""
    final_model: str = ""
    total_attempts: int = 0
    total_time_seconds: float = 0.0
    context_was_compressed: bool = False
    user_notification_sent: bool = False
    message: str = ""


# ---------------------------------------------------------------------------
# Error Recovery Manager
# ---------------------------------------------------------------------------


class ErrorRecoveryManager:
    """Manages error recovery for agent task execution.

    Provides a structured retry-and-degrade flow that ensures tasks
    complete reliably, with transparent logging and user notification.

    Usage:
        manager = ErrorRecoveryManager(config)
        result = await manager.execute_with_recovery(
            task_func=my_async_task,
            provider_name="openai",
            model_id="gpt-4o",
            context={"messages": [...], "tools": [...]},
            on_model_fallback=switch_model_callback,
        )
    """

    def __init__(self, config: RecoveryConfig | None = None):
        self._config = config or RecoveryConfig()
        self._error_history: list[ErrorEvent] = []
        self._notification_log: dict[str, float] = {}  # error_key -> last_notified_ts
        self._recovery_stats: dict[str, int] = defaultdict(int)
        self._max_history = 500

    async def execute_with_recovery(
        self,
        task_func: Callable,
        provider_name: str,
        model_id: str,
        context: dict[str, Any] | None = None,
        on_model_fallback: Callable[[str, str], tuple[str, str]] | None = None,
        on_context_compression: Callable[[dict], dict] | None = None,
        on_user_notify: Callable[[str, ErrorSeverity, str], None] | None = None,
    ) -> RecoveryResult:
        """Execute a task with automatic error recovery.

        Args:
            task_func: Async callable that performs the actual LLM call.
                       Should raise on failure, return result on success.
            provider_name: Initial provider name.
            model_id: Initial model ID.
            context: Task context (messages, tools, etc.) — may be modified by compression.
            on_model_fallback: Callback that receives (provider, model) and returns
                               a new (provider, model) pair to try.
            on_context_compression: Callback that receives context dict and returns
                                    a compressed version.
            on_user_notify: Callback to send user notifications.
                            Receives (message, severity, details).

        Returns:
            RecoveryResult with success/failure status and full error chain.
        """
        start_time = time.time()
        context = context or {}
        current_provider = provider_name
        current_model = model_id
        error_events: list[ErrorEvent] = []
        attempt = 0
        context_was_compressed = False
        notification_sent = False

        while True:
            attempt += 1

            # 1. Try executing the task
            try:
                logger.info(f"Recovery: attempt {attempt} with {current_provider}/{current_model}")
                await task_func()
                # Success!
                elapsed = time.time() - start_time
                if attempt > 1:
                    # Recovered after retries
                    self._recovery_stats["recovered"] += 1
                    if on_user_notify and self._config.enable_user_notification:
                        msg = (
                            f"Task recovered after {attempt - 1} retry attempt(s). "
                            f"Provider: {current_provider}, Model: {current_model}"
                        )
                        on_user_notify(msg, ErrorSeverity.INFO, "recovery_success")
                        notification_sent = True

                    return RecoveryResult(
                        success=True,
                        action=RecoveryAction.RETRY
                        if current_provider == provider_name
                        else RecoveryAction.MODEL_FALLBACK,
                        error_events=error_events,
                        final_provider=current_provider,
                        final_model=current_model,
                        total_attempts=attempt,
                        total_time_seconds=elapsed,
                        context_was_compressed=context_was_compressed,
                        user_notification_sent=notification_sent,
                        message=f"Task succeeded after {attempt - 1} recovery attempt(s)",
                    )
                else:
                    return RecoveryResult(
                        success=True,
                        action=RecoveryAction.RETRY,
                        error_events=error_events,
                        final_provider=current_provider,
                        final_model=current_model,
                        total_attempts=attempt,
                        total_time_seconds=elapsed,
                        context_was_compressed=False,
                        user_notification_sent=False,
                        message="Task succeeded on first attempt",
                    )

            except Exception as e:
                error_event = ErrorEvent(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    provider_name=current_provider,
                    model_id=current_model,
                    action_taken=RecoveryAction.RETRY,
                    retry_attempt=attempt,
                    context_tokens_at_failure=context.get("estimated_tokens", 0),
                )
                error_events.append(error_event)
                self._record_error(error_event)

                logger.warning(f"Recovery: attempt {attempt} failed: {type(e).__name__}: {e}")

                # 2. Check if we should retry (same provider/model)
                if attempt <= self._config.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    error_event.action_taken = RecoveryAction.RETRY
                    logger.info(f"Recovery: retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)
                    continue

                # 3. Try model fallback
                if (
                    self._config.enable_model_fallback
                    and on_model_fallback
                    and error_events[-1].action_taken != RecoveryAction.MODEL_FALLBACK
                ):
                    new_provider, new_model = on_model_fallback(current_provider, current_model)
                    if new_provider and new_model and new_provider != current_provider:
                        error_events[-1].action_taken = RecoveryAction.MODEL_FALLBACK
                        current_provider = new_provider
                        current_model = new_model
                        attempt = 0  # Reset retry counter for new model
                        self._recovery_stats["model_fallback"] += 1
                        logger.info(
                            f"Recovery: switching to fallback model "
                            f"{current_provider}/{current_model}"
                        )
                        continue

                # 4. Try context compression
                if (
                    self._config.enable_context_compression
                    and on_context_compression
                    and not context_was_compressed
                ):
                    error_events[-1].action_taken = RecoveryAction.CONTEXT_COMPRESS
                    context = on_context_compression(context)
                    context_was_compressed = True
                    attempt = 0  # Reset retry counter after compression
                    self._recovery_stats["context_compressed"] += 1
                    logger.info("Recovery: context compressed, retrying...")
                    continue

                # 5. All recovery exhausted — notify user
                elapsed = time.time() - start_time
                self._recovery_stats["failed"] += 1

                if self._config.enable_user_notification and on_user_notify:
                    error_key = f"{error_events[-1].error_type}:{current_provider}"
                    if self._should_notify(error_key):
                        msg = self._build_notification(
                            error_events, current_provider, current_model
                        )
                        on_user_notify(msg, ErrorSeverity.ERROR, "recovery_exhausted")
                        notification_sent = True

                return RecoveryResult(
                    success=False,
                    action=RecoveryAction.GIVE_UP,
                    error_events=error_events,
                    final_provider=current_provider,
                    final_model=current_model,
                    total_attempts=attempt,
                    total_time_seconds=elapsed,
                    context_was_compressed=context_was_compressed,
                    user_notification_sent=notification_sent,
                    message=f"Task failed after {attempt} attempts and all recovery strategies exhausted",
                )

    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter."""
        import random

        delay = min(
            self._config.retry_base_delay * (2 ** (attempt - 1)),
            self._config.retry_max_delay,
        )
        jitter = random.uniform(0, 0.1 * delay)
        return delay + jitter

    def _should_notify(self, error_key: str) -> bool:
        """Check if we should send a notification (respects cooldown)."""
        last_notified = self._notification_log.get(error_key, 0)
        if time.time() - last_notified >= self._config.notification_cooldown_seconds:
            self._notification_log[error_key] = time.time()
            return True
        return False

    def _build_notification(self, events: list[ErrorEvent], provider: str, model: str) -> str:
        """Build a user-friendly error notification message."""
        last_error = events[-1]
        return (
            f"Task failed after {len(events)} attempt(s). "
            f"Last error: {last_error.error_type}: {last_error.error_message[:200]}. "
            f"Provider: {provider}, Model: {model}. "
            f"Actions tried: retry({sum(1 for e in events if e.action_taken == RecoveryAction.RETRY)}), "
            f"model_fallback({sum(1 for e in events if e.action_taken == RecoveryAction.MODEL_FALLBACK)}), "
            f"context_compress({sum(1 for e in events if e.action_taken == RecoveryAction.CONTEXT_COMPRESS)}). "
            f"Please check your provider configuration or try again later."
        )

    def _record_error(self, event: ErrorEvent) -> None:
        """Record an error event."""
        self._error_history.append(event)
        if len(self._error_history) > self._max_history:
            self._error_history = self._error_history[-self._max_history :]

    # ----- Public analytics -----

    def get_error_history(self, limit: int = 50) -> list[ErrorEvent]:
        """Get recent error events."""
        return list(reversed(self._error_history))[:limit]

    def get_recovery_stats(self) -> dict[str, Any]:
        """Get recovery statistics for monitoring."""
        total = sum(self._recovery_stats.values())
        if total == 0:
            return {
                "total_tasks": 0,
                "recovered": 0,
                "failed": 0,
                "recovery_rate": 0.0,
                "by_action": {},
            }

        return {
            "total_tasks": total,
            "recovered": self._recovery_stats.get("recovered", 0),
            "failed": self._recovery_stats.get("failed", 0),
            "model_fallbacks": self._recovery_stats.get("model_fallback", 0),
            "context_compressions": self._recovery_stats.get("context_compressed", 0),
            "recovery_rate": (
                self._recovery_stats.get("recovered", 0) / total * 100 if total > 0 else 0
            ),
            "by_action": dict(self._recovery_stats),
        }

    def get_error_summary(self) -> dict[str, Any]:
        """Get summary of errors by type for debugging."""
        if not self._error_history:
            return {"total_errors": 0, "by_type": {}, "by_provider": {}}

        by_type: dict[str, int] = defaultdict(int)
        by_provider: dict[str, int] = defaultdict(int)

        for event in self._error_history:
            by_type[event.error_type] += 1
            by_provider[event.provider_name] += 1

        return {
            "total_errors": len(self._error_history),
            "by_type": dict(by_type),
            "by_provider": dict(by_provider),
        }
