"""Rotas HTTP para consultar detalhes de um scan específico."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import obter_sessao
from app.repositories.ativo_repository import AtivoRepository

router = APIRouter(prefix="/api/scans", tags=["scans"])


@router.get("/{scan_id}/ativos")
def listar_ativos_do_scan(scan_id: int, sessao: Session = Depends(obter_sessao)):
    repo = AtivoRepository(sessao)
    ativos = repo.listar_por_scan(scan_id)
    return [
        {"id": a.id, "tipo": a.tipo, "valor": a.valor, "metadados": a.metadados}
        for a in ativos
    ]
