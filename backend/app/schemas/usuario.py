from datetime import datetime
from pydantic import BaseModel

from app.models.usuario import Perfil


class UsuarioCriar(BaseModel):
    login: str
    nome: str
    senha: str
    perfil: Perfil


class UsuarioResposta(BaseModel):
    id: int
    login: str
    nome: str
    perfil: Perfil
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"