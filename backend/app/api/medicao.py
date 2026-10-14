from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario, Perfil
from app.models.auditoria import Auditoria
from app.models.medicao import MedicaoMensal, ItemMedicao
from app.schemas.medicao import MedicaoResposta
from app.services.medicao_service import gerar_medicao, fechar_medicao
from app.auth.dependencies import get_usuario_atual, exigir_perfil

router = APIRouter(tags=["Medição Mensal"])


@router.post("/contratos/{contrato_id}/medicoes/{ano}/{mes}/gerar", response_model=MedicaoResposta)
def gerar(
    contrato_id: int,
    ano: int,
    mes: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_perfil(Perfil.ADMIN)),
):
    medicao = gerar_medicao(db, contrato_id, ano, mes)
    db.add(Auditoria(
        usuario_id=usuario.id, acao="GERAR_MEDICAO",
        detalhe=f"Medição {ano}-{mes:02d} do contrato {contrato_id} gerada. Total: {medicao.total_retido}",
        ip=request.client.host if request.client else None,
    ))
    db.commit()
    return _resposta(db, medicao)


@router.post("/medicoes/{medicao_id}/fechar", response_model=MedicaoResposta)
def fechar(
    medicao_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_perfil(Perfil.ADMIN)),
):
    medicao = fechar_medicao(db, medicao_id, usuario.id)
    db.add(Auditoria(
        usuario_id=usuario.id, acao="FECHAR_MEDICAO",
        detalhe=f"Medição {medicao.ano}-{medicao.mes:02d} (id {medicao_id}) FECHADA. Total: {medicao.total_retido}",
        ip=request.client.host if request.client else None,
    ))
    db.commit()
    return _resposta(db, medicao)


@router.get("/medicoes/{medicao_id}", response_model=MedicaoResposta)
def detalhar(
    medicao_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    medicao = db.query(MedicaoMensal).filter(MedicaoMensal.id == medicao_id).first()
    if not medicao:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Medição não encontrada")
    return _resposta(db, medicao)


def _resposta(db: Session, medicao: MedicaoMensal) -> MedicaoResposta:
    itens = (
        db.query(ItemMedicao)
        .filter(ItemMedicao.medicao_id == medicao.id)
        .all()
    )
    from app.models.empregado import Empregado
    empregados = {e.id: e for e in db.query(Empregado).filter(
        Empregado.id.in_([i.empregado_id for i in itens])
    ).all()} if itens else {}

    return MedicaoResposta(
        id=medicao.id,
        contrato_id=medicao.contrato_id,
        ano=medicao.ano,
        mes=medicao.mes,
        status=medicao.status,
        total_retido=medicao.total_retido,
        fechado_em=medicao.fechado_em,
        itens=[
            {
                "empregado_id": i.empregado_id,
                "matricula": empregados[i.empregado_id].matricula,
                "nome": empregados[i.empregado_id].nome,
                "dias_trabalhados": i.dias_trabalhados,
                "provisao_13o": i.provisao_13o,
                "provisao_ferias": i.provisao_ferias,
                "encargos_13o": i.encargos_13o,
                "encargos_ferias": i.encargos_ferias,
                "fgts_mensal": i.fgts_mensal,
                "fgts_13o": i.fgts_13o,
                "fgts_ferias": i.fgts_ferias,
                "provisao_rescisoria": i.provisao_rescisoria,
                "total": i.total,
            }
            for i in itens
        ],
    )