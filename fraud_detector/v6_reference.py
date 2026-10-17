"""Frozen display summary from the executed 10-seed v6 synthetic audit.

Reproduce with: python -m scripts.v6_evaluation --seeds 10 --rows 12000
The full per-seed output is preserved in verification_bundle/v6_evaluation.txt.
This is not a bank-performance estimate.
"""

V6_SUMMARY = {
    "status": "synthetic ten-seed audit, 95% seed-level percentile bootstrap",
    "seeds": 10,
    "test_seed_range": [400045, 400054],
    "pr_auc": {"mean": 0.7454806099550229,
               "ci95_percentile": [0.7218843696917352, 0.7656370539118877]},
    "exact_5pct": {
        "precision": {"mean": 0.8313333333333333,
                      "ci95_percentile": [0.8146666666666667, 0.8486666666666667]},
        "recall": {"mean": 0.6689221848974757,
                   "ci95_percentile": [0.6566202961334409, 0.6799257674484499]},
        "f1": {"mean": 0.7411289036125248,
               "ci95_percentile": [0.7292442554752004, 0.7526292261029801]},
    },
}
