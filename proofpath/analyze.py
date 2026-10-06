"""Generate descriptive ProofPath summaries from immutable raw run records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from proofpath.evaluation.metrics import summarize_records
from proofpath.evaluation.statistics import fit_primary_model
from proofpath.experiments import load_records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-directory", type=Path, required=True)
    parser.add_argument("--allow-nonempirical", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--confirmatory-output", type=Path)
    args = parser.parse_args()
    records_path = args.run_directory.resolve() / "records.jsonl"
    records = load_records(records_path)
    summary = summarize_records(records, allow_nonempirical=args.allow_nonempirical)
    payload = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.output:
        if args.output.exists():
            parser.error(f"refusing to overwrite existing output: {args.output}")
        args.output.write_text(payload, encoding="utf-8")
    if args.confirmatory_output:
        if args.confirmatory_output.exists():
            parser.error(
                f"refusing to overwrite existing output: {args.confirmatory_output}"
            )
        confirmatory = fit_primary_model(records)
        args.confirmatory_output.write_text(
            json.dumps(confirmatory, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(payload, end="")


if __name__ == "__main__":
    main()
