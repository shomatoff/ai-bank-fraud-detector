"""Opt-in command-line public benchmark; never downloads or stores data itself."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from fraud_detector.public_benchmark import benchmark, load_ulb_csv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--sha256", required=True, help="Expected SHA256 from your own trusted download")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/public_benchmark_results.json"))
    args = parser.parse_args()
    result = benchmark(load_ulb_csv(args.csv, args.sha256), seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
