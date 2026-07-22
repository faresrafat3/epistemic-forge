"""Public error types for Epistemic Forge.

Library code must never call ``sys.exit`` / ``SystemExit``. Callers (CLI,
notebooks, servers) decide how to surface failures; the library only raises
typed exceptions that are safe to catch.
"""

from __future__ import annotations


class EpistemicForgeError(Exception):
    """Base class for all library errors."""


class PipelineError(EpistemicForgeError):
    """Raised when the L0–L6 pipeline cannot complete.

    Wraps the underlying cause so callers can introspect ``__cause__``.
    """

    def __init__(self, message: str, *, stage: str | None = None) -> None:
        self.stage = stage
        super().__init__(message)


class BudgetExceededError(EpistemicForgeError):
    """Raised when the cognitive economy budget is exhausted."""

    def __init__(self, used: int, limit: int) -> None:
        self.used = used
        self.limit = limit
        super().__init__(
            f"Cognitive budget exceeded: {used} tokens used (limit {limit})."
        )


class LLMDispatchError(EpistemicForgeError):
    """Raised when the universal LLM router cannot fulfil a request."""


class InvalidInputError(EpistemicForgeError):
    """Raised when user-supplied input fails validation."""
