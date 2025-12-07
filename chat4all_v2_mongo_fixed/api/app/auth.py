from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from .config import settings

# modelos usados em app.main
class TokenRequest(BaseModel):
    client_id: str
    client_secret: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# Demo: autenticação simplificada baseada em client_id / client_secret fixos.
DEMO_CLIENT_ID = "demo"
DEMO_CLIENT_SECRET = "demo"


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
  if expires_delta is None:
    expires_delta = timedelta(hours=1)
  to_encode = {"sub": subject, "exp": datetime.utcnow() + expires_delta}
  return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


async def get_current_client(token: str = Depends(oauth2_scheme)) -> str:
  try:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
  except Exception:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid token",
      headers={"WWW-Authenticate": "Bearer"},
    )
  sub = payload.get("sub")
  if not sub:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
  return sub
