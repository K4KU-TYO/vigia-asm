"""
Modelo: Scan

Representa uma execução de reconhecimento sobre um Alvo,
em um determinado momento no tempo.
"""
from datetime import datetime
import enum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.database import Base


class StatusScan(str, enum.Enum):
    EXECUTANDO = "executando"
    CONCLUIDO = "concluido"
    ERRO = "erro"


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    alvo_id = Column(Integer, ForeignKey("alvos.id"), nullable=False)
    status = Column(Enum(StatusScan), default=StatusScan.EXECUTANDO)
    iniciado_em = Column(DateTime, default=datetime.utcnow)
    finalizado_em = Column(DateTime, nullable=True)
    total_ativos = Column(Integer, default=0)

    alvo = relationship("Alvo", back_populates="scans")
    ativos = relationship("Ativo", back_populates="scan", cascade="all, delete-orphan")
