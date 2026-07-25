"""Rotas HTTP para gerenciar Alvos (criar, listar, remover, disparar scan)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import obter_sessao
from app.fabrica import criar_alerta_service, criar_diff_service, criar_scan_service
from app.repositories.alvo_repository import AlvoRepository
from app.repositories.scan_repository import ScanRepository

router = APIRouter(prefix="/api/alvos", tags=["alvos"])


class AlvoEntrada(BaseModel):
    nome: str = Field(..., min_length=1, max_length=120)
    dominio: str = Field(..., min_length=3, max_length=255)
    intervalo_minutos: int = Field(default=60, ge=5, le=10080)


@router.get("")
def listar_alvos(sessao: Session = Depends(obter_sessao)):
    repo = AlvoRepository(sessao)
    alvos = repo.listar()
    return [
        {
            "id": a.id,
            "nome": a.nome,
            "dominio": a.dominio,
            "intervalo_minutos": a.intervalo_minutos,
            "ativo_monitoramento": a.ativo_monitoramento,
            "criado_em": a.criado_em,
        }
        for a in alvos
    ]


@router.post("", status_code=201)
def criar_alvo(dados: AlvoEntrada, sessao: Session = Depends(obter_sessao)):
    repo = AlvoRepository(sessao)
    alvo = repo.criar(nome=dados.nome, dominio=dados.dominio, intervalo_minutos=dados.intervalo_minutos)
    return {"id": alvo.id, "nome": alvo.nome, "dominio": alvo.dominio}


@router.delete("/{alvo_id}", status_code=204)
def remover_alvo(alvo_id: int, sessao: Session = Depends(obter_sessao)):
    repo = AlvoRepository(sessao)
    removido = repo.remover(alvo_id)
    if not removido:
        raise HTTPException(status_code=404, detail="Alvo não encontrado")


@router.post("/{alvo_id}/scan")
def disparar_scan(alvo_id: int, sessao: Session = Depends(obter_sessao)):
    """Dispara um scan manual imediato e retorna o resumo + diff."""
    scan_service = criar_scan_service(sessao)
    try:
        resumo = scan_service.executar_scan(alvo_id)
    except ValueError as erro:
        raise HTTPException(status_code=404, detail=str(erro))

    diff_service = criar_diff_service(sessao)
    diff = diff_service.comparar_ultimos_scans(alvo_id)

    alvo_repo = AlvoRepository(sessao)
    alvo = alvo_repo.obter_por_id(alvo_id)
    alerta_service = criar_alerta_service()
    alerta_service.notificar_se_necessario(alvo.dominio, diff)

    resumo["novos"] = len(diff.novos)
    resumo["removidos"] = len(diff.removidos)
    return resumo


@router.get("/{alvo_id}/scans")
def listar_scans(alvo_id: int, sessao: Session = Depends(obter_sessao)):
    repo = ScanRepository(sessao)
    scans = repo.listar_por_alvo(alvo_id)
    return [
        {
            "id": s.id,
            "status": s.status,
            "iniciado_em": s.iniciado_em,
            "finalizado_em": s.finalizado_em,
            "total_ativos": s.total_ativos,
        }
        for s in scans
    ]


@router.get("/{alvo_id}/diff")
def obter_diff(alvo_id: int, sessao: Session = Depends(obter_sessao)):
    diff_service = criar_diff_service(sessao)
    diff = diff_service.comparar_ultimos_scans(alvo_id)

    def _serializar(ativo):
        return {"tipo": ativo.tipo, "valor": ativo.valor, "metadados": ativo.metadados}

    return {
        "scan_atual_id": diff.scan_atual_id,
        "scan_anterior_id": diff.scan_anterior_id,
        "novos": [_serializar(a) for a in diff.novos],
        "removidos": [_serializar(a) for a in diff.removidos],
        "inalterados": [_serializar(a) for a in diff.inalterados],
    }
