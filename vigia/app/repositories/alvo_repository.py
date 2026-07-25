"""
Repositório de Alvo.

Isola toda a lógica de acesso ao banco relacionada a Alvo.
Se um dia trocarmos SQLAlchemy por outra coisa, só esta classe muda
(Princípio da Responsabilidade Única + Inversão de Dependência).
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.alvo import Alvo


class AlvoRepository:
    def __init__(self, sessao: Session):
        self._sessao = sessao

    def criar(self, nome: str, dominio: str, intervalo_minutos: int) -> Alvo:
        alvo = Alvo(nome=nome, dominio=dominio, intervalo_minutos=intervalo_minutos)
        self._sessao.add(alvo)
        self._sessao.commit()
        self._sessao.refresh(alvo)
        return alvo

    def listar(self) -> List[Alvo]:
        return self._sessao.query(Alvo).order_by(Alvo.criado_em.desc()).all()

    def obter_por_id(self, alvo_id: int) -> Optional[Alvo]:
        return self._sessao.query(Alvo).filter(Alvo.id == alvo_id).first()

    def remover(self, alvo_id: int) -> bool:
        alvo = self.obter_por_id(alvo_id)
        if not alvo:
            return False
        self._sessao.delete(alvo)
        self._sessao.commit()
        return True

    def listar_com_monitoramento_ativo(self) -> List[Alvo]:
        return self._sessao.query(Alvo).filter(Alvo.ativo_monitoramento.is_(True)).all()
