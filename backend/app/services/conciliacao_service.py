from datetime import date, timedelta
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.domain.conciliacao import calcular_conciliacao
from app.models.contrato import Contrato
from app.models.medicao import MedicaoMensal
from app.models.movimento import MovimentoBancario


def _fim_do_periodo(ano: int | None, mes: int | None) -> date | None:
    if ano is None or mes is None:
        return None
    if mes == 12:
        return date(ano, 12, 31)
    return date(ano, mes + 1, 1) - timedelta(days=1)


def conciliar_contrato(
    db: Session,
    contrato_id: int,
    ate_ano: int | None = None,
    ate_mes: int | None = None,
):
    """Retorna (contrato, conciliacao, qtd_medicoes, data_corte)."""
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    ate = _fim_do_periodo(ate_ano, ate_mes)

    medicoes = [
        m for m in db.query(MedicaoMensal)
        .filter(MedicaoMensal.contrato_id == contrato_id, MedicaoMensal.status == "FECHADA")
        .all()
        if ate is None or (m.ano, m.mes) <= (ate.year, ate.month)
    ]
    provisionado = sum((m.total_retido for m in medicoes), Decimal("0"))

    query_mov = db.query(MovimentoBancario).filter(MovimentoBancario.contrato_id == contrato_id)
    if ate:
        query_mov = query_mov.filter(MovimentoBancario.data <= ate)
    movimentos = query_mov.all()

    depositado = sum(
        (Decimal(str(m.valor)) for m in movimentos if m.tipo == "DEPOSITO"), Decimal("0")
    )
    liberado = sum(
        (Decimal(str(m.valor)) for m in movimentos if m.tipo == "LIBERACAO"), Decimal("0")
    )

    c = calcular_conciliacao(
        saldo_inicial=Decimal(str(contrato.saldo_inicial)),
        provisionado_acumulado=provisionado,
        depositado_acumulado=depositado,
        liberado_acumulado=liberado,
    )
    return contrato, c, len(medicoes), ate