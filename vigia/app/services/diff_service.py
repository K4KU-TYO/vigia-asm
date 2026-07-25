"""
Serviço de Diff.

Compara os ativos do scan mais recente com os do scan anterior
e classifica cada ativo como NOVO, REMOVIDO ou INALTERADO.
Essa é a funcionalidade central do VIGIA: saber O QUE MUDOU.
"""
from dataclasses import dataclass, field
from typing import List

from app.models.ativo import Ativo
from app.repositories.ativo_repository import AtivoRepository
from app.repositories.scan_repository import ScanRepository

NOVO = "novo"
REMOVIDO = "removido"
INALTERADO = "inalterado"


@dataclass
class ResultadoDiff:
    scan_atual_id: int
    scan_anterior_id: int | None
    novos: List[Ativo] = field(default_factory=list)
    removidos: List[Ativo] = field(default_factory=list)
    inalterados: List[Ativo] = field(default_factory=list)

    def total_mudancas(self) -> int:
        return len(self.novos) + len(self.removidos)


class DiffService:
    def __init__(self, scan_repo: ScanRepository, ativo_repo: AtivoRepository):
        self._scan_repo = scan_repo
        self._ativo_repo = ativo_repo

    def comparar_ultimos_scans(self, alvo_id: int) -> ResultadoDiff:
        ultimos = self._scan_repo.obter_ultimos_dois(alvo_id)

        if not ultimos:
            return ResultadoDiff(scan_atual_id=-1, scan_anterior_id=None)

        scan_atual = ultimos[0]
        scan_anterior = ultimos[1] if len(ultimos) > 1 else None

        ativos_atuais = self._ativo_repo.listar_por_scan(scan_atual.id)

        if not scan_anterior:
            # Primeiro scan: tudo é "novo" por definição
            return ResultadoDiff(
                scan_atual_id=scan_atual.id,
                scan_anterior_id=None,
                novos=ativos_atuais,
            )

        ativos_anteriores = self._ativo_repo.listar_por_scan(scan_anterior.id)

        chaves_atuais = {self._chave(a): a for a in ativos_atuais}
        chaves_anteriores = {self._chave(a): a for a in ativos_anteriores}

        novos = [a for chave, a in chaves_atuais.items() if chave not in chaves_anteriores]
        removidos = [a for chave, a in chaves_anteriores.items() if chave not in chaves_atuais]
        inalterados = [a for chave, a in chaves_atuais.items() if chave in chaves_anteriores]

        return ResultadoDiff(
            scan_atual_id=scan_atual.id,
            scan_anterior_id=scan_anterior.id,
            novos=novos,
            removidos=removidos,
            inalterados=inalterados,
        )

    @staticmethod
    def _chave(ativo: Ativo) -> str:
        return f"{ativo.tipo}:{ativo.valor}"
