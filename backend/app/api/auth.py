from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario, Perfil
from app.models.auditoria import Auditoria
from app.schemas.usuario import UsuarioCriar, UsuarioResposta, Token
from app.auth.security import verificar_senha, criar_token
from app.auth.dependencies import get_usuario_atual, exigir_perfil

router = APIRouter(tags=["Autenticação"])


@router.post("/auth/login", response_model=Token)
def login(dados: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.login == dados.username).first()
    if not usuario or not verificar_senha(dados.password, usuario.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login ou senha incorretos")
    if not usuario.ativo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário inativo")
    db.add(Auditoria(usuario_id=usuario.id, acao="LOGIN", detalhe=f"Login do usuário {usuario.login}"))
    db.commit()
    return Token(access_token=criar_token(usuario.login))


@router.post("/usuarios", response_model=UsuarioResposta, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    dados: UsuarioCriar,
    request: Request,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(exigir_perfil(Perfil.ADMIN)),
):
    if db.query(Usuario).filter(Usuario.login == dados.login).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Login já existe")
    from app.auth.security import gerar_hash_senha

    novo = Usuario(
        login=dados.login,
        nome=dados.nome,
        senha_hash=gerar_hash_senha(dados.senha),
        perfil=dados.perfil,
    )
    db.add(novo)
    db.flush()
    db.add(Auditoria(
        usuario_id=usuario_atual.id,
        acao="CRIAR_USUARIO",
        detalhe=f"Usuário {dados.login} criado com perfil {dados.perfil.value}",
        ip=request.client.host if request.client else None,
    ))
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/usuarios/me", response_model=UsuarioResposta)
def quem_sou(usuario: Usuario = Depends(get_usuario_atual)):
    return usuario