"""Regression checks for master-prompt requirements that are easy to regress."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from fraud_detector.api import create_app
from fraud_detector.synthetic import generate_transactions

ROOT = Path(__file__).resolve().parents[1]


def _i18n_keys(source: str, locale: str) -> set[str]:
    base = re.search(rf"  {locale}: \{{(.*?)\n  \}}(?:,|\n\}};)", source, re.DOTALL)
    assert base, f"base locale {locale!r} is missing"
    overlays = re.findall(
        rf"Object\.assign\(i18n\.{locale}, \{{(.*?)\}}\);", source, re.DOTALL
    )
    blocks = [base.group(1), *overlays]
    return {
        key
        for block in blocks
        for key in re.findall(r"(?:^|,)\s*([A-Za-z][A-Za-z0-9_]*)\s*:", block)
    }


def test_i18n_has_the_same_effective_keys_in_all_locales():
    source = (ROOT / "web/app.js").read_text(encoding="utf-8")
    locales = {locale: _i18n_keys(source, locale) for locale in ("en", "uz", "ru")}
    assert locales["en"] == locales["uz"] == locales["ru"]


def test_production_sources_do_not_contain_hard_coded_secret_material():
    files = []
    for directory in ("fraud_detector", "web", "scripts"):
        for pattern in ("*.py", "*.js", "*.mjs", "*.html", "*.sh"):
            files.extend((ROOT / directory).rglob(pattern))
    files.append(ROOT / ".github/workflows/ci.yml")
    patterns = [
        re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----"),
        re.compile("" + r"(?:ghp|github_pat|sk)-[A-Za-z0-9_-]{20,}"),
        re.compile(r"AKIA[0-9A-Z]{16}"),
    ]
    findings = []
    for path in files:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(pattern.search(text) for pattern in patterns):
            findings.append(str(path.relative_to(ROOT)))
    assert not findings, f"possible hard-coded secret material in: {findings}"


def test_empty_dataset_and_unavailable_model_fail_visibly(tmp_path):
    with pytest.raises(ValueError, match="At least 100 rows"):
        generate_transactions(0)
    with pytest.raises(RuntimeError, match="Model artifacts unavailable"):
        create_app(tmp_path, auto_train=False)
