"""
Interface base para notificadores.

Cada canal (Discord, Slack, Telegram...) implementa `enviar`.
O AlertaService não sabe (e não precisa saber) qual canal está usando
- ele só depende desta abstração (Princípio da Inversão de Dependência).
"""
from abc import ABC, abstractmethod


class Notificador(ABC):
    @abstractmethod
    def enviar(self, mensagem: str) -> bool:
        """Envia a mensagem pelo canal. Retorna True se enviou com sucesso."""
        raise NotImplementedError

    @abstractmethod
    def esta_configurado(self) -> bool:
        """Indica se o notificador tem as credenciais/URL necessárias preenchidas."""
        raise NotImplementedError
