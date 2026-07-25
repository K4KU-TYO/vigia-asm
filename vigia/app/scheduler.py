"""
Agendador de scans automáticos.

A cada minuto verifica quais alvos estão "vencidos" (passou o intervalo
configurado desde o último scan) e dispara um novo scan + diff + alerta.
Usa APScheduler em background, sem depender de cron do sistema operacional.
"""
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from app.database import SessionLocal
from app.fabrica import criar_alerta_service, criar_diff_service, criar_scan_service
from app.repositories.alvo_repository import AlvoRepository
from app.repositories.scan_repository import ScanRepository

logger = logging.getLogger("vigia.scheduler")


def _alvo_precisa_de_scan(alvo, ultimo_scan) -> bool:
    if ultimo_scan is None:
        return True
    limite = ultimo_scan.iniciado_em + timedelta(minutes=alvo.intervalo_minutos)
    return datetime.utcnow() >= limite


def verificar_e_escanear_alvos() -> None:
    """Job executado periodicamente pelo scheduler."""
    sessao = SessionLocal()
    try:
        alvo_repo = AlvoRepository(sessao)
        scan_repo = ScanRepository(sessao)

        for alvo in alvo_repo.listar_com_monitoramento_ativo():
            ultimos = scan_repo.listar_por_alvo(alvo.id)
            ultimo_scan = ultimos[0] if ultimos else None

            if not _alvo_precisa_de_scan(alvo, ultimo_scan):
                continue

            logger.info("Escaneando automaticamente: %s", alvo.dominio)
            try:
                scan_service = criar_scan_service(sessao)
                scan_service.executar_scan(alvo.id)

                diff_service = criar_diff_service(sessao)
                diff = diff_service.comparar_ultimos_scans(alvo.id)

                alerta_service = criar_alerta_service()
                alerta_service.notificar_se_necessario(alvo.dominio, diff)
            except Exception:
                logger.exception("Falha ao escanear alvo %s", alvo.dominio)
    finally:
        sessao.close()


def iniciar_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(verificar_e_escanear_alvos, "interval", minutes=1, id="verificacao_periodica")
    scheduler.start()
    return scheduler
