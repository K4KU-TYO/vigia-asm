"""Repositório de Scan - acesso ao banco relacionado às execuções de reconhecimento."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.scan import Scan, StatusScan


class ScanRepository:
    def __init__(self, sessao: Session):
        self._sessao = sessao

    def criar(self, alvo_id: int) -> Scan:
        scan = Scan(alvo_id=alvo_id, status=StatusScan.EXECUTANDO)
        self._sessao.add(scan)
        self._sessao.commit()
        self._sessao.refresh(scan)
        return scan

    def finalizar(self, scan_id: int, total_ativos: int, status: StatusScan = StatusScan.CONCLUIDO) -> None:
        scan = self.obter_por_id(scan_id)
        if scan:
            scan.status = status
            scan.total_ativos = total_ativos
            scan.finalizado_em = datetime.utcnow()
            self._sessao.commit()

    def obter_por_id(self, scan_id: int) -> Optional[Scan]:
        return self._sessao.query(Scan).filter(Scan.id == scan_id).first()

    def listar_por_alvo(self, alvo_id: int) -> List[Scan]:
        return (
            self._sessao.query(Scan)
            .filter(Scan.alvo_id == alvo_id)
            .order_by(Scan.iniciado_em.desc())
            .all()
        )

    def obter_ultimos_dois(self, alvo_id: int) -> List[Scan]:
        """Retorna os dois scans mais recentes e concluídos de um alvo (para o diff)."""
        return (
            self._sessao.query(Scan)
            .filter(Scan.alvo_id == alvo_id, Scan.status == StatusScan.CONCLUIDO)
            .order_by(Scan.iniciado_em.desc())
            .limit(2)
            .all()
        )
