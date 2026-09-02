"""Simple Q&A baseline (no claim lattice / no ARSENAL pipeline)."""

from __future__ import annotations


def baseline_answer(title: str, question: str, domain: str, keywords: list[str]) -> str:
    """Produce a short unstructured answer — typical one-shot Q&A quality."""
    kw = ", ".join(keywords) if keywords else "the main themes"
    # Deliberately thin: claim-ish sentence, weak support, no rebuttal structure
    templates = {
        "philosophy": (
            f"{title}: On the question «{question}», a reasonable view is that "
            f"responsibility still applies when agents can track norms, even if "
            f"cognition is predictive. Keywords: {kw}. In short, keep blame practices "
            f"but update the metaphysics of agency."
        ),
        "kaggle": (
            f"{title}: For «{question}», start with a simple model and check the metric. "
            f"Look at the data, try gradient boosting, and submit. Keywords: {kw}. "
            f"Tune hyperparameters if you have time."
        ),
        "freelance": (
            f"{title}: Regarding «{question}», clarify the goal with the client, propose "
            f"a timeline, and deliver a document. Keywords: {kw}. Price based on effort "
            f"and send an invoice when done."
        ),
        "research": (
            f"{title}: The question «{question}» can be addressed by reviewing related work "
            f"and proposing a method. Keywords: {kw}. Then run an experiment and write results."
        ),
        "writing": (
            f"{title}: To answer «{question}», write a clear introduction, explain the idea, "
            f"and conclude. Keywords: {kw}. Keep the audience in mind."
        ),
        "hybrid": (
            f"{title}: «{question}» — provide an answer covering {kw}, keep it practical, "
            f"and move on to delivery."
        ),
    }
    return templates.get(domain, templates["hybrid"])
