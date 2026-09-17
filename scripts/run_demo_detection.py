#!/usr/bin/env python3
"""Create deterministic demo alerts from labeled Zeek logs.

This is intentionally passive: it reads conn/dns/ssl telemetry only and never
decrypts traffic or performs a network action. Labels provide the ground truth
for the demo corpus; the generated evidence describes the detector family.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


REASONS = {
    "ddos": "High-volume connection burst exceeds the DDoS baseline.",
    "c2_beacon": "Regular low-jitter callback timing is consistent with C2 beaconing.",
    "dga_dns": "High-entropy generated DNS query detected.",
    "encrypted_malware": "Suspicious TLS fingerprint observed without decrypting payloads.",
    "scanning": "Many destination services were probed in a short observation window.",
    "exfiltration": "Unusual outbound volume or DNS channel is consistent with data exfiltration.",
}


def field_indexes(path: Path) -> dict[str, int]:
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.startswith("#fields"):
                return {name: index for index, name in enumerate(line.rstrip("\n").split("\t")[1:])}
    raise ValueError(f"No #fields header in {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/processed/mixed/conn.log"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/alerts/demo_alerts.json"))
    parser.add_argument("--per-threat", type=int, default=20, help="maximum alerts emitted for each threat family")
    args = parser.parse_args()
    indexes = field_indexes(args.input)
    required = ("ts", "id.orig_h", "id.resp_h", "label")
    absent = [name for name in required if name not in indexes]
    if absent:
        raise SystemExit(f"Input is missing required Zeek fields: {', '.join(absent)}")

    alerts, emitted, host_counts = [], defaultdict(int), defaultdict(int)
    with args.input.open(encoding="utf-8") as stream:
        for line in stream:
            if line.startswith("#"):
                continue
            row = line.rstrip("\n").split("\t")
            label = row[indexes["label"]]
            if label not in REASONS or emitted[label] >= args.per_threat:
                continue
            source = row[indexes["id.orig_h"]]
            destination = row[indexes["id.resp_h"]]
            host_counts[(label, source)] += 1
            # One alert for each first observed host keeps the output compact.
            if host_counts[(label, source)] != 1:
                continue
            emitted[label] += 1
            confidence = round(min(0.98, 0.72 + emitted[label] * 0.01), 2)
            alerts.append({
                "alert_id": f"demo-{label}-{emitted[label]:03d}",
                "observed_at": row[indexes["ts"]],
                "source_host": source,
                "destination_host": destination,
                "threat_type": label,
                "severity": "critical" if label == "ddos" else "high",
                "confidence": confidence,
                "reasons": [REASONS[label]],
                "signals": [{"name": "labeled_demo_record", "value": 1.0, "source": "zeek"}],
                "detectors": ["statistical_rule", "fusion"],
                "status": "new",
            })
    missing = sorted(set(REASONS) - set(emitted))
    if missing:
        raise SystemExit(f"No alerts generated for: {', '.join(missing)}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(alerts, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(alerts)} alerts to {args.output}: {dict(emitted)}")


if __name__ == "__main__":
    main()
