"""L5 Procedural Memory — SOTA Vector Database (ChromaDB) Skill Library.

Replaces hardcoded lists with a persistent semantic memory store.
The system learns over time by saving successful cognitive strategies and
retrieving them dynamically for future similar inquiries (Voyager-style).
"""
from typing import Any, Optional, cast

import chromadb
from loguru import logger

from epistemic_forge.models import Skill


class SkillLibrary:
    """Persistent Vector Memory for Procedural Skills.

    Accepts an optional ``client`` (a ``chromadb.Client`` / ``PersistentClient``)
    so tests can inject an in-memory or fake client. When ``persist_dir`` is
    ``None`` an ephemeral in-memory client is used (no disk writes).
    """

    def __init__(
        self,
        persist_dir: str | None = ".forge_memory",
        client: Optional["chromadb.api.ClientAPI"] = None,
    ):
        self.persist_dir = persist_dir
        # Initialize ChromaDB client (local persistent storage)
        try:
            if client is not None:
                self.client = client
            elif persist_dir is None:
                self.client = chromadb.Client()
            else:
                self.client = chromadb.PersistentClient(path=persist_dir)
            self.collection = self.client.get_or_create_collection(
                name="epistemic_skills"
            )
            logger.info("🧠 L5 Vector Memory (ChromaDB) successfully initialized.")
        except Exception as e:
            logger.warning(
                f"ChromaDB initialization failed: {e}. Running with ephemeral memory."
            )
            self.client = chromadb.Client()
            self.collection = self.client.create_collection(name="epistemic_skills")

    def add_skill(self, skill: Skill):
        """Saves a new cognitive skill to the vector database."""
        try:
            self.collection.add(
                documents=[skill.description],
                metadatas=[{"code": skill.code, "name": skill.name, "tags": ",".join(skill.tags)}],
                ids=[skill.name]
            )
            logger.debug(f"Skill '{skill.name}' committed to long-term memory.")
        except Exception as e:
            logger.debug(f"Failed to commit skill: {e}")

    def retrieve_relevant_skills(self, query: str, n_results: int = 2) -> list[Skill]:
        """Performs semantic search to find skills relevant to the current inquiry."""
        try:
            if self.collection.count() == 0:
                return []

            results = cast(dict[str, Any], self.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.collection.count()),
            ))

            skills: list[Skill] = []
            metadatas = results.get("metadatas") or []
            if metadatas and metadatas[0]:
                for meta in metadatas[0]:
                    meta = cast(dict[str, Any], meta)
                    skills.append(Skill(
                        name=str(meta.get("name", "unknown")),
                        description="",  # Recovered from doc if needed
                        code=str(meta.get("code", "")),
                        tags=str(meta.get("tags", "")).split(","),
                    ))
            return skills
        except Exception as e:
            logger.warning(f"L5 Retrieval failed: {e}")
            return []

    def get_all_skills(self) -> list[Skill]:
        """Returns all skills (for debugging or exact matching)."""
        try:
            results = cast(dict[str, Any], self.collection.get())
            skills: list[Skill] = []
            metadatas = results.get("metadatas") or []
            if metadatas:
                for meta in metadatas:
                    meta = cast(dict[str, Any], meta)
                    skills.append(Skill(
                        name=str(meta.get("name", "unknown")),
                        description="",
                        code=str(meta.get("code", "")),
                        tags=str(meta.get("tags", "")).split(","),
                    ))
            return skills
        except Exception as e:
            logger.warning(f"L5 get_all_skills failed: {e}")
            return []
