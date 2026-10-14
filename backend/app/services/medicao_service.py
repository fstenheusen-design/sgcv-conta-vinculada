from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.domain.parametros import ParametrosContrato, parametros_vigentes
from app.domain.provisoes import calcular_provisao_mensal
from app.models.contrato import Contrato
from app.models.empregado import Empregado
from app.models.parametro import ParametroVigencia
from app.models.medicao import MedicaoMensal, ItemMedicao


def _parametros_do_banco(vigencias: list[ParametroVigencia], data_ref: date) -> ParametrosContrato:
    """Converte as vigências do banco no dataclass do domínio."""
    lista = [
        ParametrosContrato(
            vigencia_inicio=v.vigencia_inicio,
            vigencia_fim=v.vigencia_fim,
            inss_patronal=v.inss_patronal,
            rat=v.rat,
            fgts=v.fgts,
            multa_rescisoria=v.multa_rescisoria,
        )
        for v in vigencias
    ]
    return parametros_vigentes(lista, data_ref)


def gerar_medicao(db: Session, contrato_id: int, ano: int, mes: int) -> MedicaoMensal:
    """Gera (ou regenera, se ainda ABERTA) a medição mensal do contrato."""
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    existente = (
        db.query(MedicaoMensal)
        .filter(MedicaoMensal.contrato_id == contrato_id, MedicaoMensal.ano == ano, MedicaoMensal.mes == mes)
        .first()
    )
    if existente and existente.status == "FECHADA":
        raise HTTPException(status_code=409, detail="Medição já FECHADA — imutável")

    data_ref = date(ano, mes, 15)
    vigencias = (
        db.query(ParametroVigencia)
        .filter(ParametroVigencia.contrato_id == contrato_id)
        .all()
    )
    if not vigencias:
        raise HTTPException(status_code=400, detail="Contrato sem parâmetros cadastrados")
    parametros = _parametros_do_banco(vigencias, data_ref)

    empregados = db.query(Empregado).filter(Empregado.contrato_id == contrato_id).all()
    if not empregados:
        raise HTTPException(status_code=400, detail="Contrato sem empregados cadastrados")

    itens = []
    total_geral = Decimal("0")
    for emp in empregados:
        if emp.data_admissao > date(ano, mes, 28):
            continue  # admitido depois do mês de referência
        p = calcular_provisao_mensal(
            salario_base=emp.salario_base,
            parametros=parametros,
            data_referencia=data_ref,
            data_admissao=emp.data_admissao,
            data_demissao=emp.data_demissao,
        )
        itens.append((emp, p))
        total_geral += p.total_retido

    if existente is None:
        medicao = MedicaoMensal(contrato_id=contrato_id, ano=ano, mes=mes)
        db.add(medicao)
    else:
        medicao = existente
        medicao.itens.clear()  # regeneração: apaga os itens antigos

    db.flush()
    for emp, p in itens:
        db.add(ItemMedicao(
            medicao_id=medicao.id,
            empregado_id=emp.id,
            data_referencia=data_ref,
            dias_trabalhados=p.dias_trabalhados,
            provisao_13o=p.provisao_13o,
            provisao_ferias=p.provisao_ferias,
            encargos_13o=p.encargos_13o,
            encargos_ferias=p.encargos_ferias,
            fgts_mensal=p.fgts_mensal,
            fgts_13o=p.fgts_13o,
            fgts_ferias=p.fgts_ferias,
            provisao_rescisoria=p.provisao_rescisoria,
            total=p.total_retido,
        ))
    medicao.total_retido = total_geral
    db.commit()
    db.refresh(medicao)
    return medicao


def fechar_medicao(db: Session, medicao_id: int, usuario_id: int) -> MedicaoMensal:
    medicao = db.query(MedicaoMensal).filter(MedicaoMensal.id == medicao_id).first()
    if not medicao:
        raise HTTPException(status_code=404, detail="Medição não encontrada")
    if medicao.status == "FECHADA":
        raise HTTPException(status_code=409, detail="Medição já está fechada")
    medicao.status = "FECHADA"
    medicao.fechado_por_id = usuario_id
    medicao.fechado_em = medicao.criado_em if False else None  # preenchido abaixo
    from datetime import datetime, timezone
    medicao.fechado_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(medicao)
    return medicao