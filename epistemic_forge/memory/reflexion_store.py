"""L5 verbal memory — Reflexion-style."""

from __future__ import annotations

from epistemic_forge.models import Reflection


class ReflexionStore:
    def __init__(self, window: int = 3):
        self.window = window
        self._items: list[Reflection] = []

    def add(self, reflection: Reflection) -> None:
        self._items.append(reflection)
        self._items = self._items[-self.window :]

    def as_prompt_block(self) -> str:
        if not self._items:
            return "No prior trial lessons."
        lines = []
        for r in self._items:
            lines.append(
                f"Trial {r.trial}: failed because {r.failure_summary}. "
                f"Lesson: {r.lesson}. Next: {r.next_action}"
            )
        return "\n".join(lines)

    def all(self) -> list[Reflection]:
        return list(self._items)

    def reflect_on_failure(self, trial: int, score: float, notes: str) -> Reflection:
        r = Reflection(
            trial=trial,
            failure_summary=notes or f"score={score:.2f} below threshold",
            lesson="Increase structure, epistemic humility, and domain-specific acceptance checks.",
            next_action="Re-run L3 with broader framings and force L4 limit/action sections.",
        )
        self.add(r)
        return r
