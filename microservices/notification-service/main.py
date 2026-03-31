"""Notification Microservice — receives order events and dispatches alerts."""
import logging
import os
from datetime import datetime
from typing import List, Optional

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel
from starlette.responses import Response

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")
logger = logging.getLogger("notification-service")

notifications_sent    = Counter("notifications_sent_total", "Total notifications dispatched", ["channel"])
notifications_inbox: list = []   # In-memory inbox (use Redis/DB in prod)


class OrderEvent(BaseModel):
    orderId:     int
    orderNumber: str
    status:      str
    customerName: str
    customerEmail: str
    totalAmount: float
    eventTime:   Optional[str] = None


class Notification(BaseModel):
    id:          int
    orderNumber: str
    message:     str
    channel:     str
    sentAt:      str
    read:        bool = False


app = FastAPI(title="CloudOrderX Notification Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_message(event: OrderEvent) -> str:
    messages = {
        "PENDING":    f"Order {event.orderNumber} received from {event.customerName}.",
        "CONFIRMED":  f"Order {event.orderNumber} confirmed — ${event.totalAmount:,.2f}.",
        "PROCESSING": f"Order {event.orderNumber} is now being processed.",
        "SHIPPED":    f"Order {event.orderNumber} has been shipped to {event.customerName}!",
        "DELIVERED":  f"Order {event.orderNumber} delivered successfully to {event.customerName}.",
        "CANCELLED":  f"Order {event.orderNumber} was cancelled.",
    }
    return messages.get(event.status, f"Order {event.orderNumber} updated to {event.status}.")


@app.get("/health")
def health():
    return {"status": "up", "service": "notification-service"}


@app.post("/notify/order-event", summary="Handle an order status event")
def notify_order_event(event: OrderEvent):
    message = build_message(event)
    sent_at = event.eventTime or datetime.utcnow().isoformat()

    notification = {
        "id":          len(notifications_inbox) + 1,
        "orderNumber": event.orderNumber,
        "message":     message,
        "channel":     "email",
        "sentAt":      sent_at,
        "read":        False,
    }

    # Simulate email dispatch
    logger.info("[EMAIL] → %s <%s>: %s", event.customerName, event.customerEmail, message)
    notifications_sent.labels(channel="email").inc()

    # Simulate in-app notification
    notifications_inbox.append(notification)
    notifications_sent.labels(channel="in-app").inc()

    if len(notifications_inbox) > 500:
        notifications_inbox.pop(0)

    return {"dispatched": True, "message": message}


@app.get("/notifications", summary="Get in-app notifications")
def get_notifications(unread_only: bool = False) -> List[dict]:
    if unread_only:
        return [n for n in notifications_inbox if not n["read"]]
    return notifications_inbox[-50:]


@app.patch("/notifications/{notification_id}/read")
def mark_read(notification_id: int):
    for n in notifications_inbox:
        if n["id"] == notification_id:
            n["read"] = True
            return {"updated": True}
    return {"updated": False}


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=False)
