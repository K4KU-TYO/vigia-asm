"""
Serviço de Scan.

Orquestra a execução de todos os scanners registrados sobre um alvo,
persiste o resultado e devolve um resumo. Não sabe COMO cada scanner
funciona por dentro - só chama a interface comum `Scanner.executar()`.

Os scanners são injetados no construtor (Injeção de Dependência),
então trocar/adicionar scanners não exige alterar esta classe.
"""
from typing import List

from app.models.scan import StatusScan
from app.repositories.alvo_repository import AlvoRepository
from app.repositories.ativo_repository import AtivoRepository
from app.repositories.scan_repository import ScanRepository
from app.scanners.base import Scanner


class ScanService:
    def __init__(
        self,
        alvo_repo: AlvoRepository,
        scan_repo: ScanRepository,
        ativo_repo: AtivoRepository,
        scanners: List[Scanner],
    ):
        self._alvo_repo = alvo_repo
        self._scan_repo = scan_repo
        self._ativo_repo = ativo_repo
        self._scanners = scanners

    def executar_scan(self, alvo_id: int) -> dict:
        """
        Executa todos os scanners sobre o domínio do alvo e salva o resultado.
        Retorna um resumo simples (usado pela API/log).
        """
        alvo = self._alvo_repo.obter_por_id(alvo_id)
        if not alvo:
            raise ValueError(f"Alvo {alvo_id} não encontrado")

        scan = self._scan_repo.criar(alvo_id=alvo.id)

        try:
            todos_ativos = []
            resumo_por_scanner = {}

            for scanner in self._scanners:
                try:
                    encontrados = scanner.executar(alvo.dominio)
                except Exception:
                    # Um scanner falhar não deve derrubar o scan inteiro -
                    # os outros continuam rodando normalmente.
                    encontrados = []
                todos_ativos.extend(encontrados)
                resumo_por_scanner[scanner.nome] = len(encontrados)

            self._ativo_repo.salvar_varios(scan.id, todos_ativos)
            self._scan_repo.finalizar(scan.id, total_ativos=len(todos_ativos), status=StatusScan.CONCLUIDO)

            return {
                "scan_id": scan.id,
                "alvo": alvo.dominio,
                "total_ativos": len(todos_ativos),
                "por_scanner": resumo_por_scanner,
            }
        except Exception as erro:
            self._scan_repo.finalizar(scan.id, total_ativos=0, status=StatusScan.ERRO)
            raise erro
