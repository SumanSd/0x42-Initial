"""FastMCP tool boundary: four independently callable agent tools."""

from dataclasses import asdict

from fastmcp import FastMCP

from skill_erosion.agents.trace_collector.agent import collect_traces as _collect
from skill_erosion.agents.divergence_scoring.agent import score_divergence as _score
from skill_erosion.agents.misconception_clustering.agent import (
    cluster_misconceptions as _cluster,
)
from skill_erosion.agents.remediation.agent import recommend_remediation as _remediate

mcp = FastMCP("Skill Erosion Tracker")


@mcp.tool(name="collect_traces")
def collect_traces(attempts: list[dict]) -> dict:
    """Validate and persist versioned attempts, then index embeddings."""
    return asdict(_collect(attempts))


@mcp.tool(name="score_divergence")
def score_divergence(student_id: str, skill_id: str) -> dict:
    """Score the assisted/unassisted gap across matched checkpoints."""
    return asdict(_score(student_id, skill_id))


@mcp.tool(name="cluster_misconceptions")
def cluster_misconceptions(student_id: str, skill_id: str) -> list[dict]:
    """Group weak unassisted attempts into evidence-backed clusters."""
    return [asdict(c) for c in _cluster(student_id, skill_id)]


@mcp.tool(name="recommend_remediation")
def recommend_remediation(cluster: dict, trend: dict) -> dict:
    """Retrieve a curated resource and produce teacher/student outputs."""
    return asdict(_remediate(cluster, trend))


def main() -> None:
    """Local-only HTTP endpoint: http://127.0.0.1:8000/mcp."""
    mcp.run(transport="http", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
