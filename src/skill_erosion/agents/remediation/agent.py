"""Remediation agent: cluster-scoped retrieval over the curated catalog.

The cluster summary and its evidence text are embedded and matched against
embedded resource documents. With no confident match the plan is honestly
marked `no_matching_resource`; thin evidence yields `insufficient_evidence`.
"""

from typing import Mapping

from skill_erosion.contracts.models import (
    MisconceptionCluster,
    RemediationPlan,
    TrendReport,
)
from skill_erosion.data import load_resource_body, load_resource_catalog
from skill_erosion.embeddings.local import HashingTextEncoder, cosine
from skill_erosion.storage import default_repository

_MATCH_THRESHOLD = 0.10
_MIN_EVIDENCE = 2

_encoder = HashingTextEncoder()


def _coerce_cluster(raw: MisconceptionCluster | Mapping) -> MisconceptionCluster:
    return raw if isinstance(raw, MisconceptionCluster) else MisconceptionCluster(**dict(raw))


def _coerce_trend(raw: TrendReport | Mapping) -> TrendReport:
    return raw if isinstance(raw, TrendReport) else TrendReport(**dict(raw))


def _evidence_text(cluster: MisconceptionCluster) -> str:
    repo = default_repository()
    texts: list[str] = []
    for key in cluster.evidence_attempt_ids[:3]:
        attempt_id, _, version = key.rpartition(":v")
        attempt = repo.get(attempt_id, int(version)) if version.isdigit() else None
        if attempt is not None:
            texts.append(attempt.response_text)
    return " ".join(texts)


def _best_resource(query_vector: list[float], skill_id: str) -> tuple[dict | None, str, float]:
    best_resource, best_body, best_score = None, "", 0.0
    for resource in load_resource_catalog():
        if resource["skill_id"] != skill_id:
            continue
        body = load_resource_body(resource)
        score = cosine(query_vector, _encoder.encode([resource["misconception"] + " " + body])[0])
        if score > best_score:
            best_resource, best_body, best_score = resource, body, score
    return best_resource, best_body, best_score


def _extract_exercise(body: str) -> str:
    for paragraph in body.split("\n\n"):
        if paragraph.strip().lower().startswith("practice"):
            return " ".join(paragraph.split())
    return "Re-attempt the task without assistance and explain each step by hand."


def recommend_remediation(
    cluster: MisconceptionCluster | Mapping, trend: TrendReport | Mapping
) -> RemediationPlan:
    """Retrieve a curated resource for this cluster, carrying sources into both outputs."""
    cluster = _coerce_cluster(cluster)
    trend = _coerce_trend(trend)
    base = {
        "student_id": cluster.student_id,
        "skill_id": cluster.skill_id,
        "cluster_id": cluster.cluster_id,
    }
    if len(cluster.evidence_attempt_ids) < _MIN_EVIDENCE:
        return RemediationPlan(
            teacher_summary="Not enough evidence to characterize this misconception.",
            student_exercise="",
            resource_ids=[],
            status="insufficient_evidence",
            **base,
        )
    query = _encoder.encode([cluster.concept_summary + " " + _evidence_text(cluster)])[0]
    resource, body, score = _best_resource(query, cluster.skill_id)
    if resource is None or score < _MATCH_THRESHOLD:
        return RemediationPlan(
            teacher_summary=f"No curated resource matches: {cluster.concept_summary}.",
            student_exercise="",
            resource_ids=[],
            status="no_matching_resource",
            **base,
        )
    gaps = [c.gap for c in trend.checkpoints]
    span = f"gap {gaps[0]:+.2f} -> {gaps[-1]:+.2f}" if gaps else "no scored checkpoints"
    teacher_summary = (
        f"{cluster.concept_summary} ({len(cluster.evidence_attempt_ids)} attempts). "
        f"Trend {trend.status}, {span}. Assign {resource['resource_id']}."
    )
    return RemediationPlan(
        teacher_summary=teacher_summary,
        student_exercise=_extract_exercise(body),
        resource_ids=[resource["resource_id"]],
        status="ready",
        **base,
    )
