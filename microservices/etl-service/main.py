"""ETL Microservice — FastAPI + scheduled pipeline."""
import logging
import os
import threading
import time
from contextlib import asynccontextmanager

import schedule
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from etl_processor import ETLProcessor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")
logger = logging.getLogger("etl-service")

SOURCE_API  = os.getenv("SOURCE_API_URL", "http://backend:8080/api/v1")
DB_URL      = os.getenv("DB_URL", "sqlite:///./analytics.db")
RUN_EVERY   = int(os.getenv("ETL_INTERVAL_MINUTES", "15"))

processor = ETLProcessor(source_api_url=SOURCE_API, db_url=DB_URL)

# Prometheus metrics
etl_runs_total    = Counter("etl_runs_total",    "Total ETL pipeline runs",  ["status"])
etl_records_out   = Counter("etl_records_out",   "Total records loaded")
etl_duration      = Histogram("etl_duration_seconds", "ETL run duration")

run_history: list = []


def run_etl_job():
    logger.info("Scheduled ETL run starting…")
    with etl_duration.time():
        result = processor.run()
    etl_runs_total.labels(status=result["status"]).inc()
    etl_records_out.inc(result.get("records_out", 0))
    run_history.append(result)
    if len(run_history) > 100:
        run_history.pop(0)


def scheduler_thread():
    schedule.every(RUN_EVERY).minutes.do(run_etl_job)
    while True:
        schedule.run_pending()
        time.sleep(10)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run immediately on startup
    run_etl_job()
    t = threading.Thread(target=scheduler_thread, daemon=True)
    t.start()
    logger.info("ETL scheduler started — runs every %d minutes.", RUN_EVERY)
    yield


app = FastAPI(title="CloudOrderX ETL Service", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "up", "service": "etl-service"}


@app.post("/run", summary="Trigger manual ETL run")
def trigger_run():
    result = processor.run()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result.get("error_msg"))
    return result


@app.get("/history", summary="Last 100 ETL run logs")
def history():
    return run_history


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
