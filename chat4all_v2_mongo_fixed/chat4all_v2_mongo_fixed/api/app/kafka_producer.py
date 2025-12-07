import json
import asyncio
import logging
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError

from .config import settings

logger = logging.getLogger(__name__)

_topic_messages = "chat4all.messages"
_producer: AIOKafkaProducer | None = None


async def get_producer() -> AIOKafkaProducer:
    global _producer
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        
        # LÓGICA DE RETRY QUE ESTÁ FALTANDO NO SEU ARQUIVO:
        retries = 30 
        for i in range(retries):
            try:
                await _producer.start()
                logger.info("✅ Kafka Producer conectado com sucesso.")
                break
            except KafkaConnectionError as e:
                if i == retries - 1:
                    logger.error("❌ Falha crítica: Kafka não respondeu em 90 segundos.")
                    raise e
                # Aumentei o intervalo de log para não poluir
                if i % 5 == 0: 
                    logger.warning(f"⚠️ Kafka indisponível. Aguardando... (Tentativa {i+1}/{retries})")
                await asyncio.sleep(3)
                
    return _producer


async def send_message_event(event: dict) -> None:
    producer = await get_producer()
    try:
        await producer.send_and_wait(_topic_messages, event)
    except KafkaConnectionError:
        # Tenta reconectar se cair
        global _producer
        if _producer:
            try:
                await _producer.stop()
            except Exception: pass
            _producer = None
        producer = await get_producer()
        await producer.send_and_wait(_topic_messages, event)