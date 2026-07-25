"""
Fábrica de dependências (Factory).

Centraliza a montagem dos serviços com suas dependências injetadas.
Isso evita espalhar "new Scanner()" ou "new Repository()" por todo
o código - se um construtor mudar, só se ajusta aqui.
"""
from sqlalchemy.orm import Session

from app.config import config
from app.notifiers.discord import NotificadorDiscord
from app.notifiers.slack import NotificadorSlack
from app.notifiers.telegram import NotificadorTelegram
from app.repositories.alvo_repository import AlvoRepository
from app.repositories.ativo_repository import AtivoRepository
from app.repositories.scan_repository import ScanRepository
from app.scanners.http_probe import HttpProbeScanner
from app.scanners.portas import PortScanner
from app.scanners.subdominio import SubdomainScanner
from app.services.alerta_service import AlertaService
from app.services.diff_service import DiffService
from app.services.scan_service import ScanService


def criar_scan_service(sessao: Session) -> ScanService:
    return ScanService(
        alvo_repo=AlvoRepository(sessao),
        scan_repo=ScanRepository(sessao),
        ativo_repo=AtivoRepository(sessao),
        scanners=[
            SubdomainScanner(),
            PortScanner(),
            HttpProbeScanner(),
        ],
    )


def criar_diff_service(sessao: Session) -> DiffService:
    return DiffService(
        scan_repo=ScanRepository(sessao),
        ativo_repo=AtivoRepository(sessao),
    )


def criar_alerta_service() -> AlertaService:
    return AlertaService(
        notificadores=[
            NotificadorDiscord(config.webhook_discord),
            NotificadorSlack(config.webhook_slack),
            NotificadorTelegram(config.telegram_token, config.telegram_chat_id),
        ]
    )
