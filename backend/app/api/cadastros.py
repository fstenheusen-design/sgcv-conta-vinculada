from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario, Perfil
from app.models.auditoria import Auditoria
from app.models.contrato import Contrato
from app.models.empregado import Empregado
from app.models.parametro import ParametroVigencia
from app.schemas.cadastro import (
    ContratoCriar, ContratoResposta,
    EmpregadoCriar, EmpregadoResposta,
    ParametroCriar, ParametroResposta,
)
from app.auth.dependencies import get_usuario_atual, exigir_perfil

router = APIRouter(tags=["Cadastros"])


@router.post("/contratos", response_model=ContratoResposta, status_code=status.HTTP_201_CREATED)
def criar_contrato(
    dados: ContratoCriar,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_perfil(Perfil.ADMIN)),
):
    if db.query(Contrato).filter(Contrato.numero == dados.numero).first():
        raise HTTPException(status_code=409, detail="Número de contrato já existe")
    novo = Contrato(**dados.model_dump())
    db.add(novo)
    db.flush()
    db.add(Auditoria(
        usuario_id=usuario.id, acao="CRIAR_CONTRATO",
        detalhe=f"Contrato {dados.numero} — {dados.contratada}",
        ip=request.client.host if request.client else None,
    ))
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/contratos", response_model=list[ContratoResposta])
def listar_contratos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    return db.query(Contrato).order_by(Contrato.numero).all()


@router.post("/contratos/{contrato_id}/empregados", response_model=EmpregadoResposta, status_code=status.HTTP_201_CREATED)
def criar_empregado(
    contrato_id: int,
    dados: EmpregadoCriar,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_perfil(Perfil.ADMIN)),
):
    if not db.query(Contrato).filter(Contrato.id == contrato_id).first():
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    novo = Empregado(contrato_id=contrato_id, **dados.model_dump())
    db.add(novo)
    db.flush()
    db.add(Auditoria(
        usuario_id=usuario.id, acao="CRIAR_EMPREGADO",
        detalhe=f"Empregado {dados.matricula} — {dados.nome} no contrato {contrato_id}",
        ip=request.client.host if request.client else None,
    ))
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/contratos/{contrato_id}/empregados", response_model=list[EmpregadoResposta])
def listar_empregados(
    contrato_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    return (
        db.query(Empregado)
        .filter(Empregado.contrato_id == contrato_id)
        .order_by(Empregado.nome)
        .all()
    )


@router.post("/contratos/{contrato_id}/parametros", response_model=ParametroResposta, status_code=status.HTTP_201_CREATED)
def criar_parametro(
    contrato_id: int,
    dados: ParametroCriar,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_perfil(Perfil.ADMIN)),
):
    if not db.query(Contrato).filter(Contrato.id == contrato_id).first():
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    novo = ParametroVigencia(contrato_id=contrato_id, **dados.model_dump())
    db.add(novo)
    db.flush()
    db.add(Auditoria(
        usuario_id=usuario.id, acao="CRIAR_PARAMETRO",
        detalhe=f"Parâmetros do contrato {contrato_id} a partir de {dados.vigencia_inicio}",
        ip=request.client.host if request.client else None,
    ))
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/contratos/{contrato_id}/parametros", response_model=list[ParametroResposta])
def listar_parametros(
    contrato_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    return (
        db.query(ParametroVigencia)
        .filter(ParametroVigencia.contrato_id == contrato_id)
        .order_by(ParametroVigencia.vigencia_inicio)
        .all()
    )