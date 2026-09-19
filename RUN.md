# How to run

Python 3.11+. All commands run from this folder. The core pipeline (ingestion,
scoring, clustering, remediation, demo, tests) has **zero third-party
dependencies**; Streamlit and FastMCP are only needed for the UI and MCP server.

## 1. Install

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

macOS / Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

Below, `python` means your virtual environment's interpreter.

## 2. Run the end-to-end demo (no extra installs)

```bash
python -m skill_erosion
```

This seeds the synthetic fixtures into `data/processed/traces.sqlite3`
(idempotently), then runs collect -> score -> cluster -> remediate for all four
scenarios and prints the trend, gap per checkpoint, cluster, and remediation
plan. Expected output statuses: `demo-widening` widening, `demo-narrowing`
narrowing, `demo-stable` stable, `demo-sparse` insufficient_data.

## 3. Verify

```bash
python -m compileall -q src apps scripts
python scripts/check_scaffold.py
python -m unittest discover -s tests/unit -v
```

`check_scaffold.py` validates fixtures plus behavior: journey statuses match
`expected_trends.json`, reimport is a no-op, conflicting versions are rejected,
and the widening scenario yields a ready remediation plan.

## 4. Dashboards (optional)

```bash
python -m pip install -e ".[ui]"
python -m streamlit run apps/teacher_dashboard/app.py --server.port 8501 --server.address 127.0.0.1
python -m streamlit run apps/student_portal/app.py --server.port 8502 --server.address 127.0.0.1
```

Open http://localhost:8501 (teacher: trends, gap chart, evidence, intervention)
and http://localhost:8502 (student: targeted exercise and resource). In each,
click **Load / refresh synthetic data** once, pick a demo learner, run.

## 5. MCP server (optional)

```bash
python -m pip install -e ".[mcp]"
python -m skill_erosion.mcp_server
```

Four tools at `http://127.0.0.1:8000/mcp`: `collect_traces`, `score_divergence`,
`cluster_misconceptions`, `recommend_remediation`. This is an MCP endpoint, not
a REST API or browser page.

## Configuration

| Env var | Default | Purpose |
|---|---|---|
| `SKILL_EROSION_DB` | `data/processed/traces.sqlite3` | Trace store location (tests override it) |
| `SKILL_EROSION_ROOT` | repo root | Fixture/config/resource lookup |

## Notes and limits

- Deterministic heuristic scorer (`gap-ensemble-v1`) and hashed n-gram encoder
  (`hash-ngram-v1`) keep the pilot reproducible without model downloads; both
  are versioned and replaceable via the `scoring/` and `embeddings/` ports.
- All data is synthetic. Raw response text is stored but never included in
  outputs or logs.
