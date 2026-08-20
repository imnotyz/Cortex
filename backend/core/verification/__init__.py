"""Verification loop — the sixth layer of the Agent architecture.

Ensures the Agent validates its own output before marking a task complete,
rather than blindly trusting LLM self-reporting.
"""

from .verification_loop import (
    VerificationResult,
    VerificationStrategy,
    CheckResult,
    VerificationLoop,
)

__all__ = [
    "VerificationResult",
    "VerificationStrategy",
    "CheckResult",
    "VerificationLoop",
]
