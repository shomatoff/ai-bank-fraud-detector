import hashlib

import numpy as np
import pandas as pd
import pytest

from fraud_detector.public_benchmark import (
    ULB_COLUMNS,
    benchmark,
    load_ulb_csv,
    time_split,
)
from scripts.v5_evaluation import bootstrap_interval


def fixture_frame():
    rng = np.random.default_rng(273)
    rows = []
    for index in range(300):
        is_fraud = int(index % 10 == 0 or index % 29 == 0)
        row = {name: float(rng.normal()) for name in ULB_COLUMNS[1:-2]}
        row.update(Time=float(index), Amount=float(rng.uniform(1, 900)), Class=is_fraud)
        row["V1"] = float(is_fraud * .8 + rng.normal(0, 1.2))
        rows.append(row)
    return pd.DataFrame(rows, columns=ULB_COLUMNS)


def test_ulb_loader_checksum_schema_and_temporal_split(tmp_path):
    path = tmp_path / "tiny-synthetic-fixture.csv"
    fixture_frame().to_csv(path, index=False)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    frame = load_ulb_csv(path, digest)
    fit, validation, test = time_split(frame)
    assert len(fit) == 180 and len(validation) == 60 and len(test) == 60
    assert fit.Time.max() < validation.Time.min() < test.Time.min()
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        load_ulb_csv(path, "0" * 64)
    with pytest.raises(ValueError, match="expected SHA256"):
        load_ulb_csv(path, "none")


def test_benchmark_fixture_not_public_dataset():
    result = benchmark(fixture_frame(), seed=42)
    assert result["selected_on_validation"] in result["validation_pr_auc"]
    assert result["models"]["always_normal"]["alerts"] == 0
    for name in ("logistic", "hist_gradient_boosting", "fixed_amount_rule"):
        assert result["models"][name]["exact_top_k"]["0.05"]["alerts"] == 3
    assert result["feedback_demo"]["status"] != "not evaluable"


def test_seed_bootstrap_is_reproducible():
    a = bootstrap_interval([.1, .2, .3, .4], seed=518, replicates=1000)
    assert a == bootstrap_interval([.1, .2, .3, .4], seed=518, replicates=1000)
    assert a["ci95_percentile"][0] <= a["mean"] <= a["ci95_percentile"][1]
    with pytest.raises(ValueError, match="two independent"):
        bootstrap_interval([.5])
