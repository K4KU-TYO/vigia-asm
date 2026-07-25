"""Notificador via bot do Telegram."""
import requests

from app.notifiers.base import Notificador


class NotificadorTelegram(Notificador):
    def __init__(self, token: str, chat_id: str):
        self._token = token
        self._chat_id = chat_id

    def esta_configurado(self) -> bool:
        return bool(self._token and self._chat_id)

    def enviar(self, mensagem: str) -> bool:
        if not self.esta_configurado():
            return False
        try:
            url = f"https://api.telegram.org/bot{self._token}/sendMessage"
            resposta = requests.post(
                url, json={"chat_id": self._chat_id, "text": mensagem}, timeout=5
            )
            return resposta.status_code == 200
        except requests.RequestException:
            return False
