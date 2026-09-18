from skill_erosion.contracts.models import Attempt, JourneyResult


async def run_journey(
    attempts: list[Attempt], student_id: str, skill_id: str
) -> JourneyResult:
    """Target: collect -> score -> cluster -> remediate via an MCP client.

    Reuse history for the student/skill; validate scope before ingesting.
    Keep scoring results when retrieval fails. Do not turn sparse evidence
    or empty clusters into a fabricated diagnosis. See docs/architecture.md.
    """
    raise NotImplementedError("Phase 2: connect the four tools with FastMCP Client.")
