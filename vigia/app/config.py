"""
Configurações centrais do VIGIA.

Usa pydantic-settings para ler variáveis de ambiente (.env).
Mantemos tudo em um único lugar (SRP: esta classe só cuida de config).
"""
from pydantic_settings import BaseSettings


class Configuracoes(BaseSettings):
    # Banco de dados
    database_url: str = "sqlite:///./vigia.db"

    # Intervalo padrão de scan automático (minutos)
    intervalo_padrao_minutos: int = 60

    # Webhooks de notificação (opcionais)
    webhook_discord: str = ""
    webhook_slack: str = ""
    telegram_token: str = ""
    telegram_chat_id: str = ""

    # Portas verificadas pelo scanner de portas (as mais comuns)
    portas_padrao: str = "21,22,23,25,53,80,110,143,443,445,587,993,995,3306,3389,5432,6379,8000,8080,8443,9200,27017"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instância única (singleton) usada em toda a aplicação
config = Configuracoes()
