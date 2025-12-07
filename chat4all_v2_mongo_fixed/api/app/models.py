from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


MessageStatus = Literal["SENT", "DELIVERED", "READ"]


class ConversationCreate(BaseModel):
  type: Literal["private", "group"]
  members: List[str]
  metadata: Dict[str, Any] | None = None


class ConversationDB(BaseModel):
  id: str = Field(alias="_id")
  type: Literal["private", "group"]
  members: List[str]
  metadata: Dict[str, Any] | None = None
  created_at: datetime


class MessagePayload(BaseModel):
  type: Literal["text"]
  text: str


class MessageCreate(BaseModel):
  conversation_id: str
  from_user: str = Field(alias="from")
  to: List[str]
  channels: List[str]
  payload: MessagePayload
  metadata: Dict[str, Any] | None = None


class MessageDB(BaseModel):
  id: str = Field(alias="_id")
  conversation_id: str
  from_user: str
  to: List[str]
  channels: List[str]
  payload: MessagePayload
  metadata: Dict[str, Any] | None = None
  status: MessageStatus
  sequence: int
  created_at: datetime
  updated_at: datetime


class FileInitiateRequest(BaseModel):
  filename: str
  size: int


class FileInitiateResponse(BaseModel):
  file_id: str
  upload_url: str


class FileCompleteRequest(BaseModel):
  file_id: str
  checksum: str


class TokenRequest(BaseModel):
  client_id: str
  client_secret: str


class TokenResponse(BaseModel):
  access_token: str
  token_type: str = "bearer"
  expires_in: int = 3600


class DeliveryWebhook(BaseModel):
  message_id: str
  status: MessageStatus
  channel: str
  timestamp: datetime
