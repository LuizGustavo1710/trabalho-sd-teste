from pydantic import BaseModel
import os

class Settings(BaseModel):
  mongo_url: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")
  mongo_db: str = os.getenv("MONGO_DB", "chat4all")
  kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
  
  # Comunicação interna (API -> MinIO)
  minio_endpoint: str = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
  # Comunicação externa (Navegador -> MinIO)
  minio_external_endpoint: str = os.getenv("MINIO_EXTERNAL_ENDPOINT", "http://localhost:9000")
  
  minio_access_key: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
  minio_secret_key: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
  minio_bucket: str = os.getenv("MINIO_BUCKET", "chat4all-files")
  
  jwt_secret: str = os.getenv("JWT_SECRET", "supersecret")
  jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")

settings = Settings()