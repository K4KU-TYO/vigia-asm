"""Notificador para Discord via webhook."""
import requests

from app.notifiers.base import Notificador


class NotificadorDiscord(Notificador):
    def __init__(self, webhook_url: str):
        self._webhook_url = webhook_url

    def esta_configurado(self) -> bool:
        return bool(self._webhook_url)

    def enviar(self, mensagem: str) -> bool:
        if not self.esta_configurado():
            return False
        try:
            resposta = requests.post(
                self._webhook_url,
                json={"content": mensagem[:1900]},  # Discord limita ~2000 caracteres
                timeout=5,
            )
            return resposta.status_code in (200, 204)
        except requests.RequestException:
            return False
