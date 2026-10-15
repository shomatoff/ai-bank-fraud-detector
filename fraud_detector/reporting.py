"""Escaped local HTML, PDF and CSV exports for synthetic-only reports."""
from __future__ import annotations

import csv
import html
import io
import json
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .features import FEATURES

FONT_PATH = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")


def _safe(value) -> str:
    return html.escape(str(value), quote=True)


def report_html(report: dict) -> str:
    """A self-contained document with escaped user note and feature values."""
    rows = [
        ("Report ID", report["id"]),
        ("Created UTC", report["created_at"]),
        ("Analyst status", report["status"]),
        ("Synthetic model probability", f'{report["probability"]:.4f}'),
        ("Risk level", report["level"]),
        ("Model", report["model_name"]),
        ("Threshold", report["threshold"]),
        ("Note", report["note"]),
        *[(key, report["transaction"][key]) for key in FEATURES],
    ]
    body = "\n".join(
        f"<tr><th scope='row'>{_safe(key)}</th><td>{_safe(value)}</td></tr>"
        for key, value in rows
    )
    return (
        "<!doctype html><html lang='en'><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>SentinelAI synthetic report</title>"
        "<style>body{font:16px system-ui;max-width:850px;margin:3rem auto;color:#172033}"
        "table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd;padding:.5rem;"
        "text-align:left}th{width:40%;background:#eef}p{color:#8a2323}</style>"
        "<h1>SentinelAI synthetic assessment</h1>"
        "<p>Synthetic data only. Human review; no bank action or card blocking.</p>"
        f"<table>{body}</table></html>"
    )


def report_pdf(report: dict) -> bytes:
    """Create a genuine local PDF; use DejaVu for Unicode notes when present."""
    if FONT_PATH.exists() and "SentinelUnicode" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("SentinelUnicode", str(FONT_PATH)))
    font = "SentinelUnicode" if "SentinelUnicode" in pdfmetrics.getRegisteredFontNames() else "Helvetica"
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle("SentinelAI synthetic assessment")
    width, height = A4
    pdf.setFont(font, 16)
    pdf.drawString(42, height - 48, "SentinelAI synthetic assessment")
    pdf.setFont(font, 9)
    pdf.drawString(42, height - 68, "Synthetic demo only. Human review; no bank action.")
    data = [
        ("Report ID", report["id"]),
        ("Created UTC", report["created_at"]),
        ("Status", report["status"]),
        ("Probability", f'{report["probability"]:.4f}'),
        ("Level", report["level"]),
        ("Model", report["model_name"]),
        ("Threshold", report["threshold"]),
        ("Note", report["note"]),
        *[(key, report["transaction"][key]) for key in FEATURES],
    ]
    y = height - 100
    for key, value in data:
        if y < 60:
            pdf.showPage()
            y = height - 48
        pdf.setFont(font, 9)
        pdf.drawString(42, y, str(key))
        # Wrap by glyph width so long unbroken Unicode text is preserved.
        lines = []
        current = ""
        for char in str(value):
            if char == "\n":
                lines.append(current)
                current = ""
                continue
            if pdfmetrics.stringWidth(current + char, font, 9) > width - 230 and current:
                lines.append(current)
                current = ""
            current += char
        lines.append(current)
        for line in lines:
            if y < 60:
                pdf.showPage()
                y = height - 48
                pdf.setFont(font, 9)
            pdf.drawString(215, y, line)
            y -= 13
        y -= 7
    pdf.save()
    return buffer.getvalue()


def reports_csv(reports: list[dict]) -> str:
    output = io.StringIO()
    fields = ["id", "created_at", "status", "probability", "level",
              "model_name", "threshold", "note"]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for report in reports:
        # Prevent spreadsheet formula execution in the only user-editable field.
        row = {field: report.get(field, "") for field in fields}
        note = str(row["note"])
        unsafe_start = note.lstrip(" \t\r\n").startswith(("=", "+", "-", "@"))
        row["note"] = "'" + note if unsafe_start else note
        writer.writerow(row)
    return output.getvalue()


def report_json(report: dict) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2)
