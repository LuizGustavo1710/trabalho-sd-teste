import uuid
from fastapi import APIRouter, Depends
import boto3

from ..auth import get_current_client
from ..config import settings
from ..db import get_db
from ..models import FileInitiateRequest, FileInitiateResponse, FileCompleteRequest

router = APIRouter(prefix="/v1/files", tags=["files"])

def _s3_client():
  # Usa endpoint interno (Docker) para assinar
  return boto3.client(
    "s3",
    endpoint_url=settings.minio_endpoint,
    aws_access_key_id=settings.minio_access_key,
    aws_secret_access_key=settings.minio_secret_key,
  )

@router.post("/initiate", response_model=FileInitiateResponse)
async def initiate_upload(body: FileInitiateRequest, client_id: str = Depends(get_current_client)):
  db = get_db()
  file_id = str(uuid.uuid4())
  s3 = _s3_client()
  key = f"uploads/{file_id}/{body.filename}"
  
  # Gera URL assinada (apontando internamente para minio:9000)
  presigned = s3.generate_presigned_url(
    ClientMethod="put_object",
    Params={"Bucket": settings.minio_bucket, "Key": key},
    ExpiresIn=3600,
  )
  
  # CORREÇÃO: Troca o domínio interno pelo externo (localhost)
  # Isso permite que o usuário faça upload da máquina dele
  if settings.minio_endpoint != settings.minio_external_endpoint:
      presigned = presigned.replace(settings.minio_endpoint, settings.minio_external_endpoint)

  await db.files.insert_one(
    {
      "_id": file_id,
      "filename": body.filename,
      "size": body.size,
      "key": key,
      "status": "INITIATED",
      "client_id": client_id,
    }
  )
  return FileInitiateResponse(file_id=file_id, upload_url=presigned)

@router.post("/complete")
async def complete_upload(body: FileCompleteRequest, client_id: str = Depends(get_current_client)):
  db = get_db()
  await db.files.update_one(
    {"_id": body.file_id},
    {"$set": {"status": "COMPLETED", "checksum": body.checksum}},
  )
  return {"status": "ok"}