"""
Scanner de portas.

Faz uma varredura TCP connect simples nas portas mais comuns,
usando threads para não ser lento. Propositalmente NÃO faz
SYN scan (que exigiria socket raw + privilégios de root) para
manter o projeto simples de rodar em qualquer ambiente.
"""
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from app.config import config
from app.models.ativo import AtivoEncontrado, TipoAtivo
from app.scanners.base import Scanner


class PortScanner(Scanner):
    """Verifica quais portas TCP comuns estão abertas no domínio."""

    def __init__(self, timeout_segundos: float = 1.5, max_threads: int = 50):
        self._timeout = timeout_segundos
        self._max_threads = max_threads
        self._portas = [int(p) for p in config.portas_padrao.split(",")]

    @property
    def nome(self) -> str:
        return "Portas"

    def executar(self, dominio: str) -> List[AtivoEncontrado]:
        try:
            ip = socket.gethostbyname(dominio)
        except socket.gaierror:
            return []  # domínio não resolve, não tem o que escanear

        portas_abertas = []
        with ThreadPoolExecutor(max_workers=self._max_threads) as executor:
            tarefas = {
                executor.submit(self._testar_porta, ip, porta): porta
                for porta in self._portas
            }
            for tarefa in as_completed(tarefas):
                porta = tarefas[tarefa]
                if tarefa.result():
                    portas_abertas.append(porta)

        return [
            AtivoEncontrado(
                tipo=TipoAtivo.PORTA,
                valor=f"{dominio}:{porta}",
                metadados={"ip": ip, "porta": porta},
            )
            for porta in sorted(portas_abertas)
        ]

    def _testar_porta(self, ip: str, porta: int) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self._timeout)
                resultado = sock.connect_ex((ip, porta))
                return resultado == 0
        except socket.error:
            return False
