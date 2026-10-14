from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel


class MovimentoCriar(BaseModel):
    data: date
    tipo: str                     # DEPOSITO | LIBERACAO
    valor: Decimal
    descricao: str | None = None
    documento: str | None = None


class MovimentoResposta(BaseModel):
    id: int
    contrato_id: int
    data: date
    tipo: str
    valor: Decimal
    descricao: str | None
    documento: str | None
    criado_em: datetime

    class Config:
        from_attributes = True


class SaldoInicialAtualizar(BaseModel):
    saldo_inicial: Decimal


class ConciliacaoResposta(BaseModel):
    contrato_id: int
    numero_contrato: str
    contratada: str
    ate: date | None
    saldo_inicial: Decimal
    provisionado_acumulado: Decimal
    depositado_acumulado: Decimal
    liberado_acumulado: Decimal
    saldo_final: Decimal
    divergencia_deposito: Decimal
    medicoes_incluidas: int


class MedicaoLinhaResposta(BaseModel):
    ano: int
    mes: int
    status: str
    total_retido: Decimal
    fechado_em: datetime | None

    class Config:
        from_attributes = True


class PainelResposta(BaseModel):
    total_contratos: int
    empregados_ativos: int
    medicoes_fechadas: int
    provisao_acumulada: Decimal
    ultimo_fechamento: str | None