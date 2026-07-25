"""
Modelo: Alvo

Representa um domínio/programa que o usuário quer monitorar
continuamente (ex: "empresa.com").
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class Alvo(Base):
    __tablename__ = "alvos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)          # nome amigável (ex: "Programa X - HackerOne")
    dominio = Column(String(255), nullable=False, index=True)  # domínio raiz (ex: "empresa.com")
    intervalo_minutos = Column(Integer, default=60)      # de quanto em quanto tempo re-escanear
    ativo_monitoramento = Column(Boolean, default=True)  # liga/desliga o monitoramento contínuo
    criado_em = Column(DateTime, default=datetime.utcnow)

    scans = relationship("Scan", back_populates="alvo", cascade="all, delete-orphan")
