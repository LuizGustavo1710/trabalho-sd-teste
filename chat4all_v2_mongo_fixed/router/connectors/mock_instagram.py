from typing import Any, Dict
import asyncio


class MockInstagramConnector:
    name = "instagram"

    async def send_text(self, dest: str, payload: Dict[str, Any]) -> None:
        # Simula latência de rede
        await asyncio.sleep(0.05)
        print(f"[MockInstagram] Enviando para {dest}: {payload}")
