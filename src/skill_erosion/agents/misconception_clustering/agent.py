from skill_erosion.contracts.models import MisconceptionCluster


def cluster_misconceptions(student_id: str, skill_id: str) -> list[MisconceptionCluster]:
    """Embed weak attempts and cluster semantically; never substitute keyword matching."""
    raise NotImplementedError("Phase 2: implement evidence-backed semantic clustering.")
