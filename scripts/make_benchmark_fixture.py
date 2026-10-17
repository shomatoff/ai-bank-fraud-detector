"""Create a tiny, clearly synthetic ULB-schema fixture for loader smoke tests."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from fraud_detector.public_benchmark import ULB_COLUMNS, sha256_file


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/tiny-ulb-schema-fixture.csv"))
    args = parser.parse_args()
    rng = np.random.default_rng(273)
    rows = []
    for index in range(300):
        label = int(index % 10 == 0 or index % 29 == 0)
        row = {name: float(rng.normal()) for name in ULB_COLUMNS[1:-2]}
        row.update(Time=float(index), Amount=float(rng.uniform(1, 900)), Class=label)
        row["V1"] = float(label * .8 + rng.normal(0, 1.2))
        rows.append(row)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=ULB_COLUMNS).to_csv(args.output, index=False)
    print(f"{args.output} SHA256={sha256_file(args.output)} SYNTHETIC_FIXTURE_ONLY")


if __name__ == "__main__":
    main()
