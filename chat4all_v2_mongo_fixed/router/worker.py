import asyncio
import json
import logging
from datetime import datetime

from aiokafka import AIOKafkaConsumer
from bson import ObjectId
from bson.errors import InvalidId

from config import settings
from db import get_db
from connectors.mock_whatsapp import MockWhatsAppConnector
from connectors.mock_instagram import MockInstagramConnector


TOPIC_MESSAGES = "chat4all.messages"

logger = logging.getLogger(__name__)

# Conectores instanciados uma única vez
CONNECTORS = {
    "whatsapp": MockWhatsAppConnector(),
    "instagram": MockInstagramConnector(),
}


async def handle_message(event: dict) -> None:
    """
    Processa um evento vindo do Kafka.
    """
    db = get_db()

    message_id = event.get("message_id")
    channels = event.get("channels") or []
    payload = event.get("payload")
    dest = event.get("to")

    logger.info("Processando evento: %s", event)

    # Envia para cada canal configurado
    for ch in channels:
        connector = CONNECTORS.get(ch)
        if not connector:
            logger.warning("Conector não encontrado para canal: %s", ch)
            continue

        try:
            await connector.send_text(dest, payload)
            logger.info("Mensagem enviada via %s para %s", ch, dest)
        except Exception as e:
            logger.exception("Erro ao enviar mensagem via %s: %s", ch, e)

    # Atualiza status para DELIVERED no MongoDB
    if message_id is not None:
        try:
            if isinstance(message_id, str):
                try:
                    filter_id = {"_id": ObjectId(message_id)}
                except InvalidId:
                    filter_id = {"_id": message_id}
            else:
                filter_id = {"_id": message_id}

            result = await db.messages.update_one(
                filter_id,
                {
                    "$set": {
                        "status": "DELIVERED",
                        "updated_at": datetime.utcnow(),
                    }
                },
            )
            if result.matched_count == 0:
                logger.warning("Nenhum documento encontrado: %s", filter_id)
            else:
                logger.info("Status atualizado para DELIVERED: %s", message_id)
        except Exception as e:
            logger.exception("Erro ao atualizar status: %s", message_id)


async def main() -> None:
    """
    Loop principal do worker com deserialização SEGURA.
    """
    consumer = AIOKafkaConsumer(
        TOPIC_MESSAGES,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        # REMOVIDO: value_deserializer (causa crash em mensagens ruins)
        enable_auto_commit=True,
        group_id="chat4all-worker",
    )

    await consumer.start()
    logger.info("Worker Kafka iniciado. Consumindo do tópico: %s", TOPIC_MESSAGES)

    try:
        async for msg in consumer:
            try:
                # Deserialização manual protegida
                if msg.value:
                    event = json.loads(msg.value.decode("utf-8"))
                    await handle_message(event)
                else:
                    logger.warning("Mensagem vazia recebida.")
            except json.JSONDecodeError:
                logger.error("Falha ao ler JSON (ignorado): %s", msg.value)
            except Exception:
                logger.exception("Erro inesperado ao processar evento")
    finally:
        logger.info("Parando consumer Kafka...")
        await consumer.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())