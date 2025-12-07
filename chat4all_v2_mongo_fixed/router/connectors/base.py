from typing import Protocol, Any, Dict


class ChannelConnector(Protocol):
    name: str

    async def send_text(self, dest: str, payload: Dict[str, Any]) -> None:
        """
        Envia uma mensagem de texto para um destino específico.
        """
        ...
