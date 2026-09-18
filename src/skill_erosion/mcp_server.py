"""Tool registration only. Calling an agent reports an unimplemented error."""

from fastmcp import FastMCP

from skill_erosion.agents.trace_collector.agent import collect_traces
from skill_erosion.agents.divergence_scoring.agent import score_divergence
from skill_erosion.agents.misconception_clustering.agent import cluster_misconceptions
from skill_erosion.agents.remediation.agent import recommend_remediation

mcp = FastMCP("Skill Erosion Tracker")
mcp.tool(collect_traces)
mcp.tool(score_divergence)
mcp.tool(cluster_misconceptions)
mcp.tool(recommend_remediation)


def main() -> None:
    """Local-only HTTP endpoint: http://127.0.0.1:8000/mcp."""
    mcp.run(transport="http", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
