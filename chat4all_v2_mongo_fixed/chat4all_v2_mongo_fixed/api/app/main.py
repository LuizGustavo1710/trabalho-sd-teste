from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator # Novo

from .auth import DEMO_CLIENT_ID, DEMO_CLIENT_SECRET, TokenRequest, TokenResponse
from .routers import conversations, messages, files, webhooks
from .db import get_db

app = FastAPI(title="Chat4All v2 API", version="1.0.0")

# Instrumentação para métricas (Prometheus)
Instrumentator().instrument(app).expose(app)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
  db = get_db()
  # CORREÇÃO CRÍTICA: unique=True impede mensagens duplicadas na mesma sequência
  await db.messages.create_index([("conversation_id", 1), ("sequence", 1)], unique=True)

@app.post("/auth/token", response_model=TokenResponse, tags=["auth"])
async def auth_token(body: TokenRequest):
  if body.client_id != DEMO_CLIENT_ID or body.client_secret != DEMO_CLIENT_SECRET:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid client credentials",
    )
  from .auth import create_access_token

  access_token = create_access_token(subject=body.client_id)
  return TokenResponse(access_token=access_token)

app.include_router(conversations.router)
app.include_router(messages.router)
app.include_router(files.router)
app.include_router(webhooks.router)