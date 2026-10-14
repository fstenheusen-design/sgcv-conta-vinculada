from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.config import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def gerar_hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha, senha_hash)


def criar_token(login: str) -> str:
    expira = datetime.now(timezone.utc) + timedelta(hours=config.token_expira_horas)
    payload = {"sub": login, "exp": expira}
    return jwt.encode(payload, config.secret_key, algorithm="HS256")


def decodificar_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, config.secret_key, algorithms=["HS256"])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None