"""Local-only FastAPI app: synthetic scoring and human-reviewed reports."""
from __future__ import annotations

import csv
import io
import json
import secrets
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import joblib
import numpy as np
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from .evaluation import select_cost_threshold, threshold_metrics
from .features import FEATURES, Transaction
from .reporting import report_html, report_pdf, reports_csv
from .synthetic import generate_transactions
from .training import (
    ARTIFACT_DIR,
    ARTIFACT_VERSION,
    METRICS_PATH,
    MODEL_PATH,
    VALIDATION_PATH,
    explain,
    file_sha256,
    score,
    train,
)

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "web"
MAX_CSV_BYTES = 1_000_000
MAX_CSV_ROWS = 1000


class ReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction: Transaction
    note: str = Field(default="", max_length=300)


class ReviewUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["new", "in_review", "confirmed_fraud", "false_positive"]
    note: str = Field(default="", max_length=300)


class ThresholdRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    threshold: float | None = Field(default=None, ge=0, le=1)
    false_positive_cost: float = Field(default=1, ge=0, le=100000)
    false_negative_cost: float = Field(default=10, ge=0, le=100000)
    review_budget: float = Field(default=.10, gt=0, le=1)


def connect(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def create_app(artifact_dir: Path = ARTIFACT_DIR) -> FastAPI:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    model_path = artifact_dir / MODEL_PATH.name
    metrics_path = artifact_dir / METRICS_PATH.name
    validation_path = artifact_dir / VALIDATION_PATH.name
    if (not model_path.exists() or not metrics_path.exists() or not validation_path.exists()
            or json.loads(metrics_path.read_text()).get("artifact_version") != ARTIFACT_VERSION):
        train(output_dir=artifact_dir)
    metrics = json.loads(metrics_path.read_text())
    if file_sha256(model_path) != metrics["model_sha256"]:
        raise RuntimeError("Local model artifact hash mismatch; do not load it")
    if file_sha256(validation_path) != metrics["validation_sha256"]:
        raise RuntimeError("Validation artifact hash mismatch; do not load it")
    model = joblib.load(model_path)  # Hash is an integrity check, not a signature or trust boundary.
    with np.load(validation_path, allow_pickle=False) as stored:
        val_scores = stored["scores"].copy()
        val_labels = stored["labels"].copy()
    db_path = artifact_dir / "reports.sqlite3"
    if not db_path.exists():
        db_path.touch(mode=0o600)
    db_path.chmod(0o600)
    with connect(db_path) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            probability REAL NOT NULL,
            level TEXT NOT NULL,
            transaction_json TEXT NOT NULL,
            note TEXT NOT NULL,
            model_name TEXT NOT NULL DEFAULT 'legacy',
            threshold REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'new',
            updated_at TEXT
        )""")
        columns = {row[1] for row in db.execute("PRAGMA table_info(reports)")}
        for name, definition in (
            ("model_name", "TEXT NOT NULL DEFAULT 'legacy'"),
            ("threshold", "REAL NOT NULL DEFAULT 0"),
            ("status", "TEXT NOT NULL DEFAULT 'new'"),
            ("updated_at", "TEXT"),
        ):
            if name not in columns:
                db.execute(f"ALTER TABLE reports ADD COLUMN {name} {definition}")
        db.execute("""CREATE TABLE IF NOT EXISTS report_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            action TEXT NOT NULL,
            old_status TEXT,
            new_status TEXT NOT NULL,
            note TEXT NOT NULL,
            FOREIGN KEY(report_id) REFERENCES reports(id)
        )""")
    demo = generate_transactions(1000, 2026)
    app = FastAPI(title="AI Bank Fraud Detector — synthetic local lab", version="2.0.0")
    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    csrf_token = secrets.token_urlsafe(32)

    @app.middleware("http")
    async def local_only(request: Request, call_next):
        host = request.headers.get("host", "").split(":")[0]
        if host not in {"127.0.0.1", "localhost", "testserver"}:
            return JSONResponse({"detail": "Local access only"}, status_code=403)
        origin = request.headers.get("origin")
        if origin and origin != f"{request.url.scheme}://{request.headers['host']}":
            return JSONResponse({"detail": "Invalid origin"}, status_code=403)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        if request.url.path == "/" or request.url.path.startswith("/static/"):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
                "frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
            )
        return response

    def require_csrf(token: str):
        if not secrets.compare_digest(token, csrf_token):
            raise HTTPException(403, "Invalid CSRF token")

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(STATIC / "index.html")

    @app.get("/api/config")
    def config():
        return {"csrf_token": csrf_token, "version": app.version}

    @app.get("/api/health")
    def health():
        return {"status": "ok", "data_source": "synthetic"}

    @app.get("/api/metrics")
    def get_metrics():
        return metrics

    @app.get("/api/overview")
    def overview():
        by_hour = demo.groupby("hour", observed=True).agg(
            transactions=("is_fraud", "size"), fraud=("is_fraud", "sum"))
        by_category = demo.groupby("merchant_category", observed=True).agg(
            transactions=("is_fraud", "size"), fraud=("is_fraud", "sum"))
        return {
            "transactions": len(demo), "flagged": int(demo.is_fraud.sum()),
            "fraud_rate": round(float(demo.is_fraud.mean()), 4),
            "total_amount": round(float(demo.amount.sum()), 2),
            "hourly": [{"hour": int(hour), "transactions": int(row.transactions),
                        "fraud": int(row.fraud)} for hour, row in by_hour.iterrows()],
            "categories": [{"category": category, "transactions": int(row.transactions),
                            "fraud": int(row.fraud)} for category, row in by_category.iterrows()],
        }

    @app.get("/api/transactions")
    def transactions(limit: int = 20):
        if not 1 <= limit <= 100:
            raise HTTPException(422, "limit must be 1..100")
        rows = demo.head(limit).copy()
        rows.insert(0, "id", [f"SYN-{i:05d}" for i in range(1, len(rows) + 1)])
        return rows.to_dict(orient="records")

    @app.post("/api/score")
    def risk_score(transaction: Transaction):
        data = transaction.model_dump()
        probability = score(model, data)
        threshold = metrics["threshold"]
        level = "high" if probability >= 2 * threshold else "medium" if probability >= threshold else "low"
        signals = []
        if transaction.is_new_device:
            signals.append("new_device")
        if transaction.velocity_1h >= 4:
            signals.append("high_velocity")
        if transaction.country_risk >= 1:
            signals.append("country_risk")
        if transaction.prior_declines_24h >= 1:
            signals.append("prior_declines")
        if transaction.amount >= 1000:
            signals.append("large_amount")
        model_reasons = explain(model, data)
        model_reasons.pop("all_contributions")
        return {
            "probability": round(probability, 4), "level": level,
            "threshold": threshold, "review_recommended": probability >= threshold,
            "signals": signals, "signals_type": "hand_written_descriptive_rules",
            "model_explanation": model_reasons,
            "disclaimer": "Synthetic score; linear explanation is not causal. Human review only.",
        }

    @app.post("/api/score/batch")
    async def batch_score(request: Request):
        if not request.headers.get("content-type", "").startswith("text/csv"):
            raise HTTPException(415, "Use text/csv")
        chunks = bytearray()
        async for chunk in request.stream():
            chunks.extend(chunk)
            if len(chunks) > MAX_CSV_BYTES:
                raise HTTPException(413, "CSV must be at most 1,000,000 bytes")
        raw = bytes(chunks)
        if not raw or len(raw) > MAX_CSV_BYTES:
            raise HTTPException(413, "CSV must be nonempty and at most 1,000,000 bytes")
        try:
            source = io.StringIO(raw.decode("utf-8-sig", errors="strict"))
            reader = csv.DictReader(source, strict=True)
            if reader.fieldnames is None or list(reader.fieldnames) != FEATURES:
                raise HTTPException(422, f"CSV header must exactly match: {','.join(FEATURES)}")
            rows = []
            for number, row in enumerate(reader, start=2):
                if number > MAX_CSV_ROWS + 1:
                    raise HTTPException(413, "At most 1,000 data rows")
                if None in row or any(value is None for value in row.values()):
                    raise HTTPException(422, f"Malformed CSV row {number}")
                if row["is_new_device"].lower() not in {"true", "false"}:
                    raise HTTPException(422, f"Invalid boolean in CSV row {number}")
                try:
                    item = Transaction.model_validate(row)
                except ValueError as exc:
                    raise HTTPException(422, f"Invalid CSV row {number}: {exc}") from exc
                result = risk_score(item)
                rows.append({**item.model_dump(), "probability": result["probability"],
                             "review_recommended": result["review_recommended"]})
        except UnicodeError as exc:
            raise HTTPException(422, "CSV must be UTF-8") from exc
        except csv.Error as exc:
            raise HTTPException(422, "Malformed CSV") from exc
        if not rows:
            raise HTTPException(422, "CSV has no data rows")
        target = io.StringIO()
        writer = csv.DictWriter(target, fieldnames=FEATURES + ["probability", "review_recommended"])
        writer.writeheader()
        writer.writerows(rows)
        return Response(target.getvalue(), media_type="text/csv", headers={
            "Content-Disposition": 'attachment; filename="synthetic-batch-scores.csv"'
        })

    @app.post("/api/threshold/preview")
    def preview_threshold(settings: ThresholdRequest):
        if settings.threshold is None:
            chosen = select_cost_threshold(
                val_labels, val_scores, settings.false_positive_cost,
                settings.false_negative_cost, settings.review_budget,
            )
        else:
            chosen = threshold_metrics(val_labels, val_scores, settings.threshold)
            matrix = chosen["confusion_matrix"]
            chosen["estimated_cost"] = (
                settings.false_positive_cost * matrix["fp"]
                + settings.false_negative_cost * matrix["fn"]
            )
        return {
            **chosen, "source": "validation synthetic labels only",
            "validation_rows": len(val_labels),
            "cost_matrix": {"false_positive": settings.false_positive_cost,
                            "false_negative": settings.false_negative_cost},
            "not_a_test_or_live_performance_estimate": True,
        }

    @app.post("/api/reports", status_code=201)
    def save_report(report: ReportRequest, x_csrf_token: str = Header(default="")):
        require_csrf(x_csrf_token)
        result = risk_score(report.transaction)
        safe_transaction = {key: report.transaction.model_dump()[key] for key in FEATURES}
        now = datetime.now(UTC).isoformat()
        with connect(db_path) as db:
            cursor = db.execute(
                "INSERT INTO reports (created_at, probability, level, transaction_json, note, "
                "model_name, threshold, status, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, 'new', ?)",
                (now, result["probability"], result["level"], json.dumps(safe_transaction),
                 report.note, metrics["selected_model"], metrics["threshold"], now),
            )
            report_id = cursor.lastrowid
            db.execute(
                "INSERT INTO report_audit (report_id, created_at, action, old_status, new_status, note) "
                "VALUES (?, ?, 'created', NULL, 'new', ?)",
                (report_id, now, report.note),
            )
        return {"id": report_id, "status": "new", **result}

    @app.get("/api/reports")
    def list_reports():
        with connect(db_path) as db:
            rows = db.execute(
                "SELECT id, created_at, probability, level, note, status "
                "FROM reports ORDER BY id DESC LIMIT 100"
            ).fetchall()
            return [dict(row) for row in rows]

    @app.get("/api/reports/export.csv")
    def export_reports_csv():
        with connect(db_path) as db:
            rows = db.execute(
                "SELECT id, created_at, status, probability, level, model_name, threshold, note "
                "FROM reports ORDER BY id DESC LIMIT 1000"
            ).fetchall()
        content = reports_csv([dict(row) for row in rows])
        return Response(content, media_type="text/csv", headers={
            "Content-Disposition": 'attachment; filename="sentinel-reports.csv"'
        })

    @app.get("/api/reports/{report_id}")
    def get_report(report_id: int):
        with connect(db_path) as db:
            row = db.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "Report not found")
        result = dict(row)
        result["transaction"] = json.loads(result.pop("transaction_json"))
        result["data_source"] = "synthetic"
        result["human_review_required"] = True
        return result

    @app.patch("/api/reports/{report_id}")
    def update_review(report_id: int, update: ReviewUpdate, x_csrf_token: str = Header(default="")):
        require_csrf(x_csrf_token)
        allowed = {
            "new": {"in_review"},
            "in_review": {"confirmed_fraud", "false_positive"},
            "confirmed_fraud": {"in_review"},
            "false_positive": {"in_review"},
        }
        now = datetime.now(UTC).isoformat()
        with connect(db_path) as db:
            row = db.execute("SELECT status, note FROM reports WHERE id = ?", (report_id,)).fetchone()
            if row is None:
                raise HTTPException(404, "Report not found")
            old = row["status"]
            if update.status == old and update.note == row["note"]:
                raise HTTPException(409, "No review changes were supplied")
            if update.status != old and update.status not in allowed[old]:
                raise HTTPException(409, f"Transition {old} -> {update.status} is not allowed")
            action = "status_change" if update.status != old else "note_change"
            db.execute(
                "UPDATE reports SET status = ?, note = ?, updated_at = ? WHERE id = ?",
                (update.status, update.note, now, report_id),
            )
            db.execute(
                "INSERT INTO report_audit (report_id, created_at, action, old_status, new_status, note) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (report_id, now, action, old, update.status, update.note),
            )
        return get_report(report_id)

    @app.get("/api/reports/{report_id}/audit")
    def report_audit(report_id: int):
        get_report(report_id)
        with connect(db_path) as db:
            rows = db.execute(
                "SELECT id, created_at, action, old_status, new_status, note "
                "FROM report_audit WHERE report_id = ? ORDER BY id", (report_id,)
            ).fetchall()
            return [dict(row) for row in rows]

    @app.get("/api/reports/{report_id}/export")
    def export_report(report_id: int):
        return JSONResponse(get_report(report_id), headers={
            "Content-Disposition": f'attachment; filename="sentinel-report-{report_id}.json"'
        })

    @app.get("/api/reports/{report_id}/export.html")
    def export_report_html(report_id: int):
        return HTMLResponse(report_html(get_report(report_id)), headers={
            "Content-Disposition": f'attachment; filename="sentinel-report-{report_id}.html"',
            "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'",
        })

    @app.get("/api/reports/{report_id}/export.pdf")
    def export_report_pdf(report_id: int):
        return Response(report_pdf(get_report(report_id)), media_type="application/pdf", headers={
            "Content-Disposition": f'attachment; filename="sentinel-report-{report_id}.pdf"'
        })

    return app


app = create_app()
