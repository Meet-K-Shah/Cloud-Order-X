"""Reporting Microservice — PDF & Excel report generation via FastAPI."""
import logging
import os

import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response as StarletteResponse

from report_generator import ReportGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")
logger = logging.getLogger("reporting-service")

SOURCE_API = os.getenv("SOURCE_API_URL", "http://backend:8080/api/v1")

generator = ReportGenerator()
reports_generated = Counter("reports_generated_total", "Total reports generated", ["format"])

app = FastAPI(title="CloudOrderX Reporting Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def fetch_data():
    orders_resp  = requests.get(f"{SOURCE_API}/orders", timeout=10)
    summary_resp = requests.get(f"{SOURCE_API}/orders/reports/summary", timeout=10)
    orders_resp.raise_for_status()
    summary_resp.raise_for_status()
    return orders_resp.json()["data"], summary_resp.json()["data"]


@app.get("/health")
def health():
    return {"status": "up", "service": "reporting-service"}


@app.get("/report/pdf", summary="Download PDF order report")
def pdf_report():
    try:
        orders, summary = fetch_data()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Cannot reach backend: {exc}")

    pdf_bytes = generator.generate_pdf(orders, summary)
    reports_generated.labels(format="pdf").inc()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=cloudorderx-report.pdf"},
    )


@app.get("/report/excel", summary="Download Excel order report")
def excel_report():
    try:
        orders, summary = fetch_data()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Cannot reach backend: {exc}")

    xlsx_bytes = generator.generate_excel(orders, summary)
    reports_generated.labels(format="excel").inc()
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=cloudorderx-report.xlsx"},
    )


@app.get("/metrics", include_in_schema=False)
def metrics():
    return StarletteResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=False)
