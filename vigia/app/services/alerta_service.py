"""
Serviço de Alertas.

Recebe um resultado de diff e, se houver mudanças relevantes,
envia a mensagem para todos os notificadores configurados
(Discord, Slack, Telegram...). Não sabe os detalhes de cada canal
- só depende da interface Notificador.
"""
from typing import List

from app.notifiers.base import Notificador
from app.services.diff_service import ResultadoDiff


class AlertaService:
    def __init__(self, notificadores: List[Notificador]):
        self._notificadores = notificadores

    def notificar_se_necessario(self, dominio: str, diff: ResultadoDiff) -> bool:
        """Envia alerta apenas se houver ativos novos ou removidos. Retorna se algo foi enviado."""
        if diff.total_mudancas() == 0:
            return False

        mensagem = self._montar_mensagem(dominio, diff)
        enviou_algo = False

        for notificador in self._notificadores:
            if notificador.esta_configurado():
                if notificador.enviar(mensagem):
                    enviou_algo = True

        return enviou_algo

    @staticmethod
    def _montar_mensagem(dominio: str, diff: ResultadoDiff) -> str:
        linhas = [f"[VIGIA] Mudanças detectadas em {dominio}"]

        if diff.novos:
            linhas.append(f"\n+ {len(diff.novos)} ativo(s) NOVO(S):")
            for ativo in diff.novos[:15]:
                linhas.append(f"  + {ativo.tipo}: {ativo.valor}")

        if diff.removidos:
            linhas.append(f"\n- {len(diff.removidos)} ativo(s) REMOVIDO(S):")
            for ativo in diff.removidos[:15]:
                linhas.append(f"  - {ativo.tipo}: {ativo.valor}")

        return "\n".join(linhas)
