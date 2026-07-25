"""
Configuração da conexão com o banco de dados.

Centraliza engine, sessão e base declarativa do SQLAlchemy.
Qualquer módulo que precise falar com o banco importa daqui,
evitando conexões duplicadas.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import config

# connect_args necessário só para SQLite (permite uso em múltiplas threads)
engine = create_engine(
    config.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in config.database_url else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def obter_sessao():
    """
    Gerador de sessão usado como dependência do FastAPI.
    Garante que a sessão é sempre fechada, mesmo em caso de erro.
    """
    sessao = SessionLocal()
    try:
        yield sessao
    finally:
        sessao.close()


def criar_tabelas():
    """Cria todas as tabelas no banco caso ainda não existam."""
    from app.models import alvo, ativo, scan  # noqa: F401 (garante que os models sejam registrados)
    Base.metadata.create_all(bind=engine)
