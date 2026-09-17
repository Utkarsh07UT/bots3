#!/usr/bin/env python3
"""Validate the supplied lightweight model bundle used by the demo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


THREATS = ("ddos", "c2_beacon", "dga_dns", "encrypted_malware", "scanning", "exfiltration")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path, default=Path("data/models"))
    args = parser.parse_args()
    missing = []
    for threat in THREATS:
        model = args.model_dir / f"random_forest_{threat}" / "model.pkl"
        metadata = model.with_name("metadata.json")
        if not model.is_file() or not metadata.is_file():
            missing.append(threat)
            continue
        metrics = json.loads(metadata.read_text(encoding="utf-8")).get("metrics", {})
        print(f"{threat:20} ready  f1={metrics.get('val_f1_macro', 'n/a')}")
    if missing:
        raise SystemExit(f"Missing supplied model artifacts for: {', '.join(missing)}")
    print("All six pre-trained CPU model artifacts are ready for demo inference.")


if __name__ == "__main__":
    main()
