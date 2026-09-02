"""Tests for the memory layer: TokenBudgetManager and SkillLibrary."""

from epistemic_forge.memory.economy import TokenBudgetManager, budget_manager
from epistemic_forge.memory.skill_library import SkillLibrary
from epistemic_forge.models import Skill


class _FakeCollection:
    def __init__(self):
        self._store = {}

    def add(self, documents, metadatas, ids):
        for _id, doc, meta in zip(ids, documents, metadatas, strict=False):
            self._store[_id] = (doc, meta)

    def count(self):
        return len(self._store)

    def query(self, query_texts, n_results):
        ids = list(self._store.keys())[:n_results]
        return {
            "metadatas": [[self._store[i][1] for i in ids]],
            "documents": [[self._store[i][0] for i in ids]],
            "ids": [ids],
        }

    def get(self):
        ids = list(self._store.keys())
        return {
            "metadatas": [self._store[i][1] for i in ids],
            "documents": [self._store[i][0] for i in ids],
            "ids": ids,
        }


class _FakeClient:
    def get_or_create_collection(self, name):
        return _FakeCollection()

    def create_collection(self, name):
        return _FakeCollection()


def test_budget_reset_and_set():
    mgr = TokenBudgetManager()
    mgr.reset()
    mgr.set_budget(100)
    assert mgr.budget_limit == 100
    assert not mgr.is_budget_exceeded()


def test_budget_exceeded(mocker):
    mgr = TokenBudgetManager()
    mgr.reset()
    mgr.set_budget(100)

    class MockResponse:
        class Usage:
            total_tokens = 150

        usage = Usage()

    mgr.add_usage(MockResponse(), "mock-model")
    assert mgr.is_budget_exceeded() is True


def test_budget_add_usage_no_usage(mocker):
    mgr = TokenBudgetManager()
    mgr.reset()
    mgr.set_budget(1000)
    # Object without .usage should not raise
    mgr.add_usage(object(), "mock-model")
    assert mgr.total_tokens == 0


def test_singleton_identity():
    assert TokenBudgetManager() is TokenBudgetManager()
    assert budget_manager is TokenBudgetManager()


def test_skill_library_add_and_retrieve():
    lib = SkillLibrary(client=_FakeClient())
    lib.add_skill(
        Skill(name="baseline", description="use a baseline", code="x", tags=["ml"])
    )
    skills = lib.retrieve_relevant_skills("training", n_results=1)
    assert len(skills) == 1
    assert skills[0].name == "baseline"


def test_skill_library_empty_retrieve():
    lib = SkillLibrary(client=_FakeClient())
    assert lib.retrieve_relevant_skills("anything") == []


def test_skill_library_get_all():
    lib = SkillLibrary(client=_FakeClient())
    lib.add_skill(Skill(name="a", description="da", code="ca"))
    lib.add_skill(Skill(name="b", description="db", code="cb"))
    all_skills = lib.get_all_skills()
    assert {s.name for s in all_skills} == {"a", "b"}


def test_skill_library_accepts_ephemeral(monkeypatch):
    # persist_dir=None must not touch disk and must work.
    lib = SkillLibrary(persist_dir=None)
    assert lib.collection is not None
