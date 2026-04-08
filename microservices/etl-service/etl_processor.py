"""ETL Processor — extract orders from source API, transform, load to analytics DB."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

import pandas as pd
import requests
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)


class ETLProcessor:
    def __init__(self, source_api_url: str, db_url: str):
        self.source_api_url = source_api_url
        self.engine = create_engine(db_url, echo=False)
        self._ensure_schema()

    # ── Schema ────────────────────────────────────────────────────────────────
    def _ensure_schema(self) -> None:
        with self.engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS orders_analytics (
                    id               BIGINT PRIMARY KEY,
                    order_number     TEXT,
                    customer_name    TEXT,
                    customer_email   TEXT,
                    status           TEXT,
                    payment_status   TEXT,
                    total_amount     NUMERIC(10,2),
                    item_count       INT,
                    shipping_address TEXT,
                    created_at       TIMESTAMP,
                    processed_at     TIMESTAMP DEFAULT now()
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS etl_runs (
                    id           SERIAL PRIMARY KEY,
                    run_at       TIMESTAMP DEFAULT now(),
                    records_in   INT,
                    records_out  INT,
                    duration_ms  INT,
                    status       TEXT,
                    error_msg    TEXT
                )
            """))
        logger.info("Analytics schema ensured.")

    # ── Extract ───────────────────────────────────────────────────────────────
    def extract(self, since_hours: int = 24) -> List[Dict[str, Any]]:
        """Fetch orders from the Spring Boot API."""
        try:
            resp = requests.get(f"{self.source_api_url}/orders", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            orders = data.get("data", [])
            logger.info("Extracted %d orders from source.", len(orders))
            return orders
        except Exception as exc:
            logger.error("Extract failed: %s", exc)
            raise

    # ── Transform ─────────────────────────────────────────────────────────────
    def transform(self, raw_orders: List[Dict[str, Any]]) -> pd.DataFrame:
        """Normalize, clean, and enrich order data."""
        if not raw_orders:
            return pd.DataFrame()

        rows = []
        for o in raw_orders:
            rows.append({
                "id":               o["id"],
                "order_number":     o["orderNumber"],
                "customer_name":    o["customer"]["name"],
                "customer_email":   o["customer"]["email"],
                "status":           o["status"],
                "payment_status":   o["paymentStatus"],
                "total_amount":     float(o.get("totalAmount") or 0),
                "item_count":       len(o.get("items", [])),
                "shipping_address": o.get("shippingAddress", ""),
                "created_at":       pd.to_datetime(o.get("createdAt")),
            })

        df = pd.DataFrame(rows)

        # Validations
        df = df[df["total_amount"] >= 0]
        df = df.drop_duplicates(subset=["id"])
        df["customer_email"] = df["customer_email"].str.lower().str.strip()
        df["status"] = df["status"].str.upper()

        # Derived columns
        df["order_age_days"] = (datetime.utcnow() - df["created_at"].dt.tz_localize(None)).dt.days

        logger.info("Transformed to %d records.", len(df))
        return df

    # ── Load ──────────────────────────────────────────────────────────────────
    def load(self, df: pd.DataFrame) -> int:
        """Upsert transformed records into analytics table."""
        if df.empty:
            return 0

        load_df = df[["id","order_number","customer_name","customer_email",
                       "status","payment_status","total_amount","item_count",
                       "shipping_address","created_at"]].copy()

        with self.engine.begin() as conn:
            for _, row in load_df.iterrows():
                conn.execute(text("""
                    INSERT INTO orders_analytics
                        (id, order_number, customer_name, customer_email,
                         status, payment_status, total_amount, item_count,
                         shipping_address, created_at)
                    VALUES
                        (:id, :order_number, :customer_name, :customer_email,
                         :status, :payment_status, :total_amount, :item_count,
                         :shipping_address, :created_at)
                    ON CONFLICT (id) DO UPDATE SET
                        status         = EXCLUDED.status,
                        payment_status = EXCLUDED.payment_status,
                        total_amount   = EXCLUDED.total_amount,
                        processed_at   = now()
                """), row.to_dict())

        logger.info("Loaded %d records into analytics.", len(load_df))
        return len(load_df)

    # ── Run Pipeline ──────────────────────────────────────────────────────────
    def run(self) -> Dict[str, Any]:
        start = datetime.utcnow()
        run_log = {"status": "success", "records_in": 0, "records_out": 0, "error_msg": None}
        try:
            raw     = self.extract()
            df      = self.transform(raw)
            loaded  = self.load(df)
            run_log.update(records_in=len(raw), records_out=loaded)
        except Exception as exc:
            run_log.update(status="error", error_msg=str(exc))
            logger.error("ETL pipeline failed: %s", exc)

        duration_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
        run_log["duration_ms"] = duration_ms

        with self.engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO etl_runs (records_in, records_out, duration_ms, status, error_msg)
                VALUES (:records_in, :records_out, :duration_ms, :status, :error_msg)
            """), run_log)

        logger.info("ETL run complete in %dms — %s", duration_ms, run_log["status"])
        return run_log
