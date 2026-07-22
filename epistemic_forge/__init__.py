"""Epistemic Forge — ARSENAL-powered research & writing kit."""

from .models import Claim, ForgeResult, ProjectSpec
from .pipeline.arsenal_run import ArsenalRun, run_pipeline

__version__ = "0.1.0"
__all__ = [
    "ArsenalRun",
    "run_pipeline",
    "Claim",
    "ForgeResult",
    "ProjectSpec",
    "__version__",
]
