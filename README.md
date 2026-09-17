# UniThreat AI

UniThreat is a passive network-threat demo that reads labeled Zeek-style logs,
exports alerts for six threat families, and serves them through a FastAPI API
and Vite dashboard. It does not decrypt traffic or take active response actions.

## Demo

The supplied corpus is stored in `realdata/`. The `data/raw`,
`data/processed`, and `data/models` paths link to that corpus; do not remove
them.

```bash
make mix       # rebuild the mixed, labeled Zeek logs
make train     # validate supplied CPU model artifacts
make demo      # create data/processed/alerts/demo_alerts.json
make api       # serve API at http://localhost:8000
make dashboard # start the Vite dashboard
```

The API loads the demo alert export when started with `make api`. It exposes
`GET /api/alerts` and `POST /api/alerts/import` for the dashboard/demo feed.

## Layout

```text
backend/app/       FastAPI runtime
frontend/          Vite dashboard runtime
ai_models/         specialist model service code
scripts/           mix, model validation, and alert-export commands
realdata/          supplied raw logs, processed output, and model artifacts
data/              stable links to realdata/
infra/             optional container/Kubernetes deployment configuration
```

## Included detections

DDoS, C2 beaconing, DGA/DNS tunneling, encrypted malware, scanning, and data
exfiltration. The demo detector is label-backed and emits concise evidence for
each alert family; model artifacts are supplied for fast CPU demo validation.
