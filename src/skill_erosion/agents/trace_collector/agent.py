from skill_erosion.contracts.models import Attempt, IngestionResult


def collect_traces(attempts: list[Attempt]) -> IngestionResult:
    """Validate and persist versions, then index embeddings using stable version IDs."""
    raise NotImplementedError("Phase 1: implement validated, idempotent trace ingestion.")
