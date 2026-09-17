#!/usr/bin/env python3
"""Build a labeled Zeek dataset from UniThreat's normal and threat captures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


THREATS = ("ddos", "c2_beacon", "dga_dns", "encrypted_malware", "scanning", "exfiltration")
LOGS = ("conn.log", "dns.log", "ssl.log")


def records(path: Path):
    """Yield Zeek header lines separately from tab-delimited records."""
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            yield line


def copy_log(sources: list[Path], target: Path, ddos_limit: int) -> dict[str, int]:
    target.parent.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    seen_header = False
    with target.open("w", encoding="utf-8") as output:
        for source in sources:
            label = "benign" if source.parent.name == "normal" else source.parent.name
            allowed = ddos_limit if label == "ddos" else None
            for line in records(source):
                if line.startswith("#"):
                    if not seen_header:
                        output.write(line)
                    continue
                if allowed is not None and counts.get(label, 0) >= allowed:
                    continue
                output.write(line)
                counts[label] = counts.get(label, 0) + 1
            seen_header = True
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/mixed"))
    parser.add_argument("--ddos-max-records", type=int, default=25_000)
    args = parser.parse_args()

    source_dirs = [args.raw_dir / "normal"] + [args.raw_dir / "threats" / name for name in THREATS]
    missing = [str(directory) for directory in source_dirs if not directory.is_dir()]
    if missing:
        raise SystemExit(f"Missing source dataset directories: {', '.join(missing)}")

    all_counts: dict[str, dict[str, int]] = {}
    for log_name in LOGS:
        paths = [directory / log_name for directory in source_dirs]
        missing_logs = [str(path) for path in paths if not path.is_file()]
        if missing_logs:
            raise SystemExit(f"Missing Zeek logs: {', '.join(missing_logs)}")
        all_counts[log_name] = copy_log(paths, args.output_dir / log_name, args.ddos_max_records)

    manifest = {
        "dataset": str(args.output_dir),
        "normal_dir": str(args.raw_dir / "normal"),
        "threats": [str(args.raw_dir / "threats" / name) for name in THREATS],
        "ddos_max_records": args.ddos_max_records,
        "files": [str(args.output_dir / name) for name in LOGS],
        "record_counts": all_counts,
    }
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Mixed dataset written to {args.output_dir}")
    for log_name, counts in all_counts.items():
        print(f"  {log_name}: {sum(counts.values()):,} records ({counts})")


if __name__ == "__main__":
    main()
