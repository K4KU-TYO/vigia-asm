"""Rota de status geral do sistema - usada pela interface para mostrar o painel de config."""
from fastapi import APIRouter

from app.config import config
from app.fabrica import criar_alerta_service

router = APIRouter(prefix="/api/status", tags=["status"])


@router.get("")
def status_geral():
    alerta_service = criar_alerta_service()
    notificadores_ativos = [
        n.__class__.__name__.replace("Notificador", "")
        for n in alerta_service._notificadores  # leitura interna só para exibir status
        if n.esta_configurado()
    ]
    return {
        "sistema": "VIGIA",
        "versao": "1.0.0",
        "intervalo_padrao_minutos": config.intervalo_padrao_minutos,
        "notificadores_configurados": notificadores_ativos,
    }
