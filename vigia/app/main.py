"""
VIGIA - Sentinela de Superfície de Ataque
Ponto de entrada da aplicação.

Sobe a API FastAPI, cria as tabelas do banco, serve a interface
web estática e inicia o agendador de scans automáticos.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import criar_tabelas
from app.routers import alvos, scans, status
from app.scheduler import iniciar_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    # Executado na inicialização
    criar_tabelas()
    scheduler = iniciar_scheduler()
    yield
    # Executado no encerramento
    scheduler.shutdown()


app = FastAPI(
    title="VIGIA",
    description="Sentinela de Superfície de Ataque - monitoramento contínuo de OSINT/ASM",
    version="1.0.0",
    lifespan=ciclo_de_vida,
)

# CORS liberado para facilitar uso local/self-hosted
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alvos.router)
app.include_router(scans.router)
app.include_router(status.router)

# Serve a interface hacker (index.html + assets)
app.mount("/", StaticFiles(directory="app/static", html=True), name="estatico")
