from skill_erosion.contracts.models import TrendReport


def score_divergence(student_id: str, skill_id: str) -> TrendReport:
    """Use matched task sets and a versioned ensemble; require 3 paired checkpoints."""
    raise NotImplementedError("Phase 2: implement auditable divergence and sparse-history handling.")
