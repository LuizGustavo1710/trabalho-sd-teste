from pydantic import BaseModel
import os


class Settings(BaseModel):
  mongo_url: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")
  mongo_db: str = os.getenv("MONGO_DB", "chat4all")
  kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


settings = Settings()
