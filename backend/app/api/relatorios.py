import csv
import io
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario, Perfil
from app.models.auditoria import Auditoria
from app.models.contrato import Contrato
from app.models.empregado import Empregado
from app.models.medicao import MedicaoMensal
from app.models.movimento import MovimentoBancario
from app.schemas.relatorio import (
    MovimentoCriar, MovimentoResposta,
    SaldoInicialAtualizar, ConciliacaoResposta,
    MedicaoLinhaResposta, PainelResposta,
)
from app.services.conciliacao_service import conciliar_contrato
from app.auth.dependencies import get_usuario_atual, exigir_perfil

router = APIRouter(tags=["Relatórios e Conciliação"])


def _resposta_conciliacao(contrato, c, medicoes_incluidas, ate) -> ConciliacaoResposta:
    return ConciliacaoResposta(
        contrato_id=contrato.id,
        numero_contrato=contrato.numero,
        contratada=contrato.contratada,
        ate=ate,
        saldo_inicial=c.saldo_inicial,
        provisionado_acumulado=c.provisionado_acumulado,
        depositado_acumulado=c.depositado_acumulado,
        liberado_acumulado=c.liberado_acumulado,
        saldo_final=c.saldo_final,
        divergencia_deposito=c.divergencia_deposito,
        medicoes_incluidas=medicoes_incluidas,
    )


@router.post("/contratos/{contrato_id}/movimentos", response_model=MovimentoResposta, status_code=status.HTTP_201_CREATED)
def criar_movimento(
    contrato_id: int,
    dados: MovimentoCriar,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_perfil(Perfil.ADMIN)),
):
    if dados.tipo not in ("DEPOSITO", "LIBERACAO"):
        raise HTTPException(status_code=422, detail="Tipo deve ser DEPOSITO ou LIBERACAO")
    if dados.valor <= 0:
        raise HTTPException(status_code=422, detail="Valor deve ser positivo")
    if not db.query(Contrato).filter(Contrato.id == contrato_id).first():
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    novo = MovimentoBancario(contrato_id=contrato_id, **dados.model_dump())
    db.add(novo)
    db.flush()
    db.add(Auditoria(
        usuario_id=usuario.id, acao="CRIAR_MOVIMENTO",
        detalhe=f"{dados.tipo} de {dados.valor} em {dados.data} — contrato {contrato_id}",
        ip=request.client.host if request.client else None,
    ))
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/contratos/{contrato_id}/movimentos", response_model=list[MovimentoResposta])
def listar_movimentos(
    contrato_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    return (
        db.query(MovimentoBancario)
        .filter(MovimentoBancario.contrato_id == contrato_id)
        .order_by(MovimentoBancario.data, MovimentoBancario.id)
        .all()
    )


@router.patch("/contratos/{contrato_id}/saldo-inicial", response_model=ConciliacaoResposta)
def atualizar_saldo_inicial(
    contrato_id: int,
    dados: SaldoInicialAtualizar,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_perfil(Perfil.ADMIN)),
):
    contrato, c, n, ate = conciliar_contrato(db, contrato_id)
    contrato.saldo_inicial = dados.saldo_inicial
    db.add(Auditoria(
        usuario_id=usuario.id, acao="ATUALIZAR_SALDO_INICIAL",
        detalhe=f"Saldo inicial do contrato {contrato.numero} alterado para {dados.saldo_inicial}",
        ip=request.client.host if request.client else None,
    ))
    db.commit()
    contrato, c, n, ate = conciliar_contrato(db, contrato_id)
    return _resposta_conciliacao(contrato, c, n, ate)


@router.get("/contratos/{contrato_id}/conciliacao", response_model=ConciliacaoResposta)
def conciliacao(
    contrato_id: int,
    ate_ano: int | None = None,
    ate_mes: int | None = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    contrato, c, n, ate = conciliar_contrato(db, contrato_id, ate_ano, ate_mes)
    return _resposta_conciliacao(contrato, c, n, ate)


@router.get("/contratos/{contrato_id}/relatorio/medicoes", response_model=list[MedicaoLinhaResposta])
def relatorio_medicoes(
    contrato_id: int,
    ano: int | None = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    query = db.query(MedicaoMensal).filter(MedicaoMensal.contrato_id == contrato_id)
    if ano:
        query = query.filter(MedicaoMensal.ano == ano)
    return query.order_by(MedicaoMensal.ano, MedicaoMensal.mes).all()


@router.get("/contratos/{contrato_id}/relatorio/medicoes/csv")
def exportar_medicoes_csv(
    contrato_id: int,
    ano: int | None = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    query = db.query(MedicaoMensal).filter(MedicaoMensal.contrato_id == contrato_id)
    if ano:
        query = query.filter(MedicaoMensal.ano == ano)
    medicoes = query.order_by(MedicaoMensal.ano, MedicaoMensal.mes).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")  # ponto e vírgula: Excel BR
    writer.writerow(["Ano", "Mês", "Status", "Total Retido (R$)", "Fechado em"])
    for m in medicoes:
        writer.writerow([
            m.ano, f"{m.mes:02d}", m.status,
            str(m.total_retido).replace(".", ","),
            m.fechado_em or "",
        ])
    conteudo = "\ufeff" + buffer.getvalue()  # BOM para acentos no Excel
    nome_arquivo = f"medicoes_{contrato.numero.replace('/', '-')}.csv"
    return StreamingResponse(
        iter([conteudo]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"},
    )


@router.get("/painel", response_model=PainelResposta)
def painel(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    total_contratos = db.query(Contrato).filter(Contrato.ativo.is_(True)).count()
    empregados_ativos = db.query(Empregado).filter(Empregado.data_demissao.is_(None)).count()
    fechadas = (
        db.query(MedicaoMensal)
        .filter(MedicaoMensal.status == "FECHADA")
        .order_by(MedicaoMensal.ano, MedicaoMensal.mes)
        .all()
    )
    provisao_acumulada = sum((m.total_retido for m in fechadas), Decimal("0"))
    ultima = fechadas[-1] if fechadas else None
    return PainelResposta(
        total_contratos=total_contratos,
        empregados_ativos=empregados_ativos,
        medicoes_fechadas=len(fechadas),
        provisao_acumulada=provisao_acumulada,
        ultimo_fechamento=f"{ultima.ano}-{ultima.mes:02d}" if ultima else None,
    )