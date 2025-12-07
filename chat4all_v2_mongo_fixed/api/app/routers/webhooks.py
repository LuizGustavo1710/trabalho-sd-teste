from datetime import datetime
from fastapi import APIRouter

from ..db import get_db
from ..models import DeliveryWebhook

router = APIRouter(prefix="/v1/webhooks", tags=["webhooks"])


@router.post("/delivery")
async def delivery_callback(body: DeliveryWebhook):
  db = get_db()
  await db.messages.update_one(
    {"_id": body.message_id},
    {"$set": {"status": body.status, "updated_at": datetime.utcnow()}},
  )
  return {"status": "ok"}
