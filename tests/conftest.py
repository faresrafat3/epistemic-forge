"""Shared pytest fixtures.

Forces the universal LLM router into its deterministic offline fallback (no
network / no API keys) and prevents ChromaDB from writing to disk, so the test
suite is fast, hermetic, and CI-friendly.
"""

from __future__ import annotations

import pytest

import epistemic_forge.llm as llm_mod
from epistemic_forge.memory.economy import budget_manager
from epistemic_forge.pipeline import arsenal_run as arsenal_run_mod


class _FakeSkillLibrary:
    """In-memory stand-in for the ChromaDB-backed SkillLibrary."""

    def __init__(self, *args, **kwargs):
        self._skills = []

    def retrieve_relevant_skills(self, *args, **kwargs):
        return []

    def add_skill(self, skill):
        self._skills.append(skill)

    def get_all_skills(self):
        return list(self._skills)


@pytest.fixture(autouse=True)
def _offline_and_memory(monkeypatch):
    # The TokenBudgetManager is a process-wide singleton; reset it so a test
    # that intentionally exhausts the budget can't poison later tests.
    budget_manager.reset()
    # Force the router into deterministic offline mode for every test.
    monkeypatch.setattr(llm_mod, "_missing_credentials", lambda model, api_key: True)
    # Avoid touching ChromaDB on disk inside ArsenalRun.create().
    monkeypatch.setattr(arsenal_run_mod, "SkillLibrary", _FakeSkillLibrary)
    yield
