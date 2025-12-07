from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from ..auth import get_current_client
from ..db import get_db
from ..models import ConversationCreate, ConversationDB

router = APIRouter(prefix="/v1/conversations", tags=["conversations"])


@router.post("", response_model=ConversationDB)
async def create_conversation(
  body: ConversationCreate, client_id: str = Depends(get_current_client)
):
  db = get_db()
  doc = {
    "type": body.type,
    "members": body.members,
    "metadata": body.metadata or {},
    "created_at": datetime.utcnow(),
    "client_id": client_id,
  }
  res = await db.conversations.insert_one(doc)
  doc["_id"] = str(res.inserted_id)
  return ConversationDB(**doc)


@router.get("/{conversation_id}/messages")
async def list_messages(conversation_id: str, client_id: str = Depends(get_current_client)):
  db = get_db()
  try:
    conv = await db.conversations.find_one({"_id": ObjectId(conversation_id)})
  except Exception:
    raise HTTPException(status_code=400, detail="Invalid conversation_id")
  if not conv:
    raise HTTPException(status_code=404, detail="Conversation not found")
  cursor = db.messages.find({"conversation_id": conversation_id}).sort("sequence", 1)
  items = []
  async for doc in cursor:
    doc["_id"] = str(doc["_id"])
    items.append(doc)
  return items
