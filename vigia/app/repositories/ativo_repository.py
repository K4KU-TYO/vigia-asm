"""Repositório de Ativo - acesso ao banco relacionado aos ativos encontrados em cada scan."""
from typing import List

from sqlalchemy.orm import Session

from app.models.ativo import Ativo, AtivoEncontrado


class AtivoRepository:
    def __init__(self, sessao: Session):
        self._sessao = sessao

    def salvar_varios(self, scan_id: int, ativos: List[AtivoEncontrado]) -> None:
        """Persiste em lote os ativos encontrados pelos scanners em um scan."""
        objetos = [
            Ativo(scan_id=scan_id, tipo=a.tipo, valor=a.valor, metadados=a.metadados)
            for a in ativos
        ]
        self._sessao.add_all(objetos)
        self._sessao.commit()

    def listar_por_scan(self, scan_id: int) -> List[Ativo]:
        return self._sessao.query(Ativo).filter(Ativo.scan_id == scan_id).all()
