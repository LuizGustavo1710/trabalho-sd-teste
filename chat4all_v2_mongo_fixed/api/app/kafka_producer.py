import json
import asyncio
from aiokafka import AIOKafkaProducer

from .config import settings

_topic_messages = "chat4all.messages"
_producer: AIOKafkaProducer | None = None


async def get_producer() -> AIOKafkaProducer:
  global _producer
  if _producer is None:
    _producer = AIOKafkaProducer(
      bootstrap_servers=settings.kafka_bootstrap_servers,
      value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    await _producer.start()
  return _producer


async def send_message_event(event: dict) -> None:
  producer = await get_producer()
  await producer.send_and_wait(_topic_messages, event)
