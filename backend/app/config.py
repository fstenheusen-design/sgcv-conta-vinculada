from pydantic_settings import BaseSettings


class Configuracoes(BaseSettings):
    database_url: str
    secret_key: str
    token_expira_horas: int = 8

    class Config:
        env_file = ".env"


config = Configuracoes()