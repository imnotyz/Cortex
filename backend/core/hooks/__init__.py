"""Action hooks — the fourth layer of the Agent architecture.

Pre-action and post-action hooks that enforce mandatory constraints
before/after tool execution. Unlike event hooks (which only observe),
action hooks can BLOCK execution when constraints are violated.
"""

from .action_hooks import (
    HookEvent,
    HookResult,
    HookAction,
    HookContext,
    ActionHookManager,
    DangerousCommandHook,
    FileSafetyHook,
    TokenBudgetHook,
)

__all__ = [
    "HookEvent",
    "HookResult",
    "HookAction",
    "HookContext",
    "ActionHookManager",
    "DangerousCommandHook",
    "FileSafetyHook",
    "TokenBudgetHook",
]
