from skill_erosion.contracts.models import MisconceptionCluster, RemediationPlan, TrendReport


def recommend_remediation(
    cluster: MisconceptionCluster, trend: TrendReport
) -> RemediationPlan:
    """Retrieve a curated resource for this cluster, carrying sources into both outputs."""
    raise NotImplementedError("Phase 2: implement cluster-specific RAG and no-match fallback.")
