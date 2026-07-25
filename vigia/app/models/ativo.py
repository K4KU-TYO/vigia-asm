"""
Modelo: Ativo

Representa um item de superfície de ataque encontrado durante um scan:
um subdomínio, uma porta aberta, um host HTTP vivo, etc.
"""
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class TipoAtivo:
    """Constantes com os tipos de ativo suportados (evita strings soltas pelo código)."""
    SUBDOMINIO = "subdominio"
    PORTA = "porta"
    HTTP = "http"


class Ativo(Base):
    __tablename__ = "ativos"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    tipo = Column(String(30), nullable=False)      # subdominio | porta | http
    valor = Column(String(500), nullable=False)    # ex: "api.empresa.com" ou "empresa.com:443"
    metadados = Column(JSON, default=dict)         # dados extras (status_code, titulo, servidor...)
    criado_em = Column(DateTime, default=datetime.utcnow)

    scan = relationship("Scan", back_populates="ativos")


@dataclass
class AtivoEncontrado:
    """
    DTO (Data Transfer Object) usado pelos scanners para retornar resultados
    sem depender diretamente do ORM. Isso desacopla a lógica de scan do
    banco de dados (Princípio da Inversão de Dependência - DIP).
    """
    tipo: str
    valor: str
    metadados: dict = field(default_factory=dict)

    def chave_unica(self) -> str:
        """Chave usada para comparar ativos entre scans diferentes (diff)."""
        return f"{self.tipo}:{self.valor}"
