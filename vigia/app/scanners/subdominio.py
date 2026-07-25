"""
Scanner de subdomínios.

Combina duas fontes:
1. crt.sh: base pública de certificados TLS emitidos (certificate transparency).
   Rápido e não gera tráfego direto contra o alvo.
2. Brute force de DNS com uma wordlist pequena embutida, resolvendo cada
   possibilidade via DNS de verdade.

Não depende de binários externos (subfinder/amass) - só bibliotecas Python,
para o projeto rodar em qualquer máquina com "pip install -r requirements.txt".
"""
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Set

import requests
import dns.resolver

from app.models.ativo import AtivoEncontrado, TipoAtivo
from app.scanners.base import Scanner

# Wordlist enxuta com os subdomínios mais comuns em programas de bug bounty.
# Pode ser expandida livremente sem mudar nenhuma outra parte do código.
WORDLIST_PADRAO = [
    "www", "api", "app", "dev", "staging", "test", "admin", "portal",
    "vpn", "mail", "smtp", "ftp", "cdn", "static", "media", "blog",
    "shop", "store", "docs", "status", "beta", "demo", "internal",
    "git", "gitlab", "jenkins", "jira", "confluence", "sso", "auth",
    "login", "dashboard", "monitor", "grafana", "kibana", "es",
    "db", "mysql", "redis", "backup", "old", "new", "prod",
]


class SubdomainScanner(Scanner):
    """Descobre subdomínios de um domínio raiz."""

    def __init__(self, timeout_segundos: int = 3, wordlist: List[str] = None, max_threads: int = 20):
        self._timeout = timeout_segundos
        self._wordlist = wordlist or WORDLIST_PADRAO
        self._max_threads = max_threads

    @property
    def nome(self) -> str:
        return "Subdomínios"

    def executar(self, dominio: str) -> List[AtivoEncontrado]:
        encontrados: Set[str] = set()
        encontrados |= self._buscar_certificate_transparency(dominio)
        encontrados |= self._forca_bruta_dns(dominio)

        return [
            AtivoEncontrado(tipo=TipoAtivo.SUBDOMINIO, valor=sub, metadados={"fonte": "crt.sh/dns"})
            for sub in sorted(encontrados)
        ]

    def _buscar_certificate_transparency(self, dominio: str) -> Set[str]:
        """Consulta crt.sh procurando certificados emitidos para *.dominio."""
        encontrados: Set[str] = set()
        try:
            resposta = requests.get(
                "https://crt.sh/",
                params={"q": f"%.{dominio}", "output": "json"},
                timeout=self._timeout,
            )
            if resposta.status_code != 200:
                return encontrados

            for registro in resposta.json():
                nomes = registro.get("name_value", "")
                for nome in nomes.split("\n"):
                    nome = nome.strip().lower().lstrip("*.")
                    if self._e_subdominio_valido(nome, dominio):
                        encontrados.add(nome)
        except (requests.RequestException, ValueError):
            # Falha de rede ou JSON inválido: não trava o scan, só retorna vazio
            pass
        return encontrados

    def _forca_bruta_dns(self, dominio: str) -> Set[str]:
        """
        Tenta resolver cada palavra da wordlist como subdomínio.
        Roda em paralelo (ThreadPoolExecutor) pra não travar o scan inteiro
        esperando timeout de DNS um candidato de cada vez.
        """
        encontrados: Set[str] = set()
        candidatos = [f"{prefixo}.{dominio}" for prefixo in self._wordlist]

        with ThreadPoolExecutor(max_workers=self._max_threads) as executor:
            tarefas = {
                executor.submit(self._resolve_um, candidato): candidato
                for candidato in candidatos
            }
            for tarefa in as_completed(tarefas):
                if tarefa.result():
                    encontrados.add(tarefas[tarefa])

        return encontrados

    def _resolve_um(self, candidato: str) -> bool:
        """Resolve um único candidato. Cria seu próprio resolver (thread-safe)."""
        resolvedor = dns.resolver.Resolver()
        resolvedor.timeout = self._timeout
        resolvedor.lifetime = self._timeout
        try:
            resolvedor.resolve(candidato, "A")
            return True
        except Exception:
            # Não resolveu = não existe (ou está fora do ar); segue o scan
            return False

    @staticmethod
    def _e_subdominio_valido(nome: str, dominio: str) -> bool:
        if not nome.endswith(dominio):
            return False
        padrao = re.compile(r"^[a-z0-9]([a-z0-9\-\.]*[a-z0-9])?$")
        return bool(padrao.match(nome))
