from datetime import datetime
from fastapi import APIRouter
from bson import ObjectId

from ..db import get_db
from ..models import DeliveryWebhook

router = APIRouter(prefix="/v1/webhooks", tags=["webhooks"])


@router.post("/delivery")
async def delivery_callback(body: DeliveryWebhook):
  db = get_db()
  filter_id = {"_id": body.message_id}
  try:
    filter_id = {"_id": ObjectId(body.message_id)}
  except Exception:
    # Mantém o filtro original em caso de IDs não-ObjectId (compatibilidade com mocks)
    pass

  await db.messages.update_one(
    filter_id,
    {"$set": {"status": body.status, "updated_at": datetime.utcnow()}},
  )
  return {"status": "ok"}
