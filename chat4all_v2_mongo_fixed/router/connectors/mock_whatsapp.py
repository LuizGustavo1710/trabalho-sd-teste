from typing import Any, Dict
import asyncio


class MockWhatsAppConnector:
    name = "whatsapp"

    async def send_text(self, dest: str, payload: Dict[str, Any]) -> None:
        # Simula latência de rede
        await asyncio.sleep(0.05)
        print(f"[MockWhatsApp] Enviando para {dest}: {payload}")
