"""Notificador para Slack via webhook."""
import requests

from app.notifiers.base import Notificador


class NotificadorSlack(Notificador):
    def __init__(self, webhook_url: str):
        self._webhook_url = webhook_url

    def esta_configurado(self) -> bool:
        return bool(self._webhook_url)

    def enviar(self, mensagem: str) -> bool:
        if not self.esta_configurado():
            return False
        try:
            resposta = requests.post(self._webhook_url, json={"text": mensagem}, timeout=5)
            return resposta.status_code == 200
        except requests.RequestException:
            return False
