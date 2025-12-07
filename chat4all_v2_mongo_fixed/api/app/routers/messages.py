from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId  # <--- IMPORTAÇÃO OBRIGATÓRIA

from ..auth import get_current_client
from ..db import get_db
from ..kafka_producer import send_message_event
from ..models import MessageCreate, MessageDB

router = APIRouter(prefix="/v1/messages", tags=["messages"])


@router.post("", response_model=MessageDB)
async def send_message(body: MessageCreate, client_id: str = Depends(get_current_client)):
  db = get_db()

  try:
      # CORREÇÃO: Converte a string que vem do JSON para ObjectId do MongoDB
      conversation_oid = ObjectId(body.conversation_id)
  except Exception:
      raise HTTPException(status_code=400, detail="Invalid conversation_id format")

  # Busca no banco usando o Objeto correto
  conversation = await db.conversations.find_one({"_id": conversation_oid})
  
  if not conversation:
    raise HTTPException(status_code=404, detail="Conversation not found")

  # Lógica de sequência (mantém busca por string aqui pois foi salvo assim na msg anterior)
  last = await db.messages.find_one(
    {"conversation_id": body.conversation_id}, sort=[("sequence", -1)]
  )
  next_seq = 1 if not last else int(last["sequence"]) + 1

  now = datetime.utcnow()
  doc = {
    "conversation_id": body.conversation_id,
    "from_user": body.from_user,
    "to": body.to,
    "channels": body.channels,
    "payload": body.payload.model_dump(),
    "metadata": body.metadata or {},
    "status": "SENT",
    "sequence": next_seq,
    "created_at": now,
    "updated_at": now,
  }
  res = await db.messages.insert_one(doc)
  doc["_id"] = str(res.inserted_id)

  event = {
    "message_id": doc["_id"],
    "conversation_id": body.conversation_id,
    "from_user": body.from_user,
    "to": body.to,
    "channels": body.channels,
    "payload": body.payload.model_dump(),
    "metadata": body.metadata or {},
  }
  await send_message_event(event)

  return MessageDB(**doc)