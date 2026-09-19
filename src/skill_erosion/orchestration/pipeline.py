"""End-to-end journey: collect -> score -> cluster -> remediate.

Sequential over the shared local adapters; each agent also stays independently
callable via the MCP tools. Partial evidence produces honest partial results:
no clusters means no remediation plans, never a fabricated diagnosis.
"""

from collections.abc import Sequence
from typing import Mapping

from skill_erosion.agents.misconception_clustering.agent import cluster_misconceptions
from skill_erosion.agents.remediation.agent import recommend_remediation
from skill_erosion.agents.divergence_scoring.agent import score_divergence
from skill_erosion.agents.trace_collector.agent import collect_traces
from skill_erosion.contracts.models import Attempt, JourneyResult


async def run_journey(
    attempts: Sequence[Attempt | Mapping] | None,
    student_id: str,
    skill_id: str,
) -> JourneyResult:
    if attempts:
        collect_traces(attempts)
    trend = score_divergence(student_id, skill_id)
    clusters = cluster_misconceptions(student_id, skill_id)
    remediation = [recommend_remediation(cluster, trend) for cluster in clusters]
    return JourneyResult(trend=trend, clusters=clusters, remediation=remediation)
