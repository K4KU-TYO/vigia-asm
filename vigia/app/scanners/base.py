"""
Interface base para scanners de reconhecimento.

Todo scanner novo (ex: um futuro scanner de certificados TLS,
ou de tecnologias JS) deve herdar de Scanner e implementar `executar`.
Isso segue o Princípio Aberto/Fechado (OCP): o orquestrador não
precisa mudar quando um scanner novo é adicionado.
"""
from abc import ABC, abstractmethod
from typing import List

from app.models.ativo import AtivoEncontrado


class Scanner(ABC):
    """Contrato comum a todos os scanners de reconhecimento."""

    @property
    @abstractmethod
    def nome(self) -> str:
        """Nome legível do scanner, usado nos logs da interface."""
        raise NotImplementedError

    @abstractmethod
    def executar(self, dominio: str) -> List[AtivoEncontrado]:
        """
        Executa o reconhecimento sobre o domínio informado e retorna
        a lista de ativos encontrados. Nunca deve levantar exceção não
        tratada: erros de rede devem ser capturados e retornar lista vazia.
        """
        raise NotImplementedError
