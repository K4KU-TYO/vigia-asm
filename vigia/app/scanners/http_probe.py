"""
Scanner HTTP (probe).

Para cada host informado, tenta HTTP e HTTPS e coleta:
status code, título da página, cabeçalho Server e tamanho da resposta.
Isso ajuda a identificar rapidamente o que mudou entre um scan e outro
(ex: um admin panel que ficou exposto, uma tecnologia que mudou).
"""
import re
from typing import List

import requests

from app.models.ativo import AtivoEncontrado, TipoAtivo
from app.scanners.base import Scanner

PADRAO_TITULO = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


class HttpProbeScanner(Scanner):
    """Verifica quais hosts respondem em HTTP/HTTPS e coleta metadados básicos."""

    def __init__(self, timeout_segundos: int = 5):
        self._timeout = timeout_segundos

    @property
    def nome(self) -> str:
        return "HTTP Probe"

    def executar(self, dominio: str) -> List[AtivoEncontrado]:
        encontrados = []
        for esquema in ("https", "http"):
            url = f"{esquema}://{dominio}"
            resultado = self._sondar(url)
            if resultado:
                encontrados.append(resultado)
        return encontrados

    def _sondar(self, url: str) -> AtivoEncontrado | None:
        try:
            resposta = requests.get(
                url,
                timeout=self._timeout,
                allow_redirects=True,
                headers={"User-Agent": "VIGIA-Recon/1.0"},
            )
        except requests.RequestException:
            return None

        titulo_match = PADRAO_TITULO.search(resposta.text or "")
        titulo = titulo_match.group(1).strip()[:200] if titulo_match else ""

        return AtivoEncontrado(
            tipo=TipoAtivo.HTTP,
            valor=url,
            metadados={
                "status_code": resposta.status_code,
                "titulo": titulo,
                "servidor": resposta.headers.get("Server", "desconhecido"),
                "tamanho_bytes": len(resposta.content),
                "url_final": resposta.url,
            },
        )
