from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel


class ContratoCriar(BaseModel):
    numero: str
    contratada: str
    faturamento_mensal: Decimal


class ContratoResposta(BaseModel):
    id: int
    numero: str
    contratada: str
    faturamento_mensal: Decimal
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True


class EmpregadoCriar(BaseModel):
    matricula: str
    nome: str
    funcao: str
    salario_base: Decimal
    data_admissao: date
    data_demissao: date | None = None


class EmpregadoResposta(BaseModel):
    id: int
    contrato_id: int
    matricula: str
    nome: str
    funcao: str
    salario_base: Decimal
    data_admissao: date
    data_demissao: date | None

    class Config:
        from_attributes = True


class ParametroCriar(BaseModel):
    vigencia_inicio: date
    vigencia_fim: date | None = None
    inss_patronal: Decimal
    rat: Decimal
    fgts: Decimal
    multa_rescisoria: Decimal


class ParametroResposta(BaseModel):
    id: int
    contrato_id: int
    vigencia_inicio: date
    vigencia_fim: date | None
    inss_patronal: Decimal
    rat: Decimal
    fgts: Decimal
    multa_rescisoria: Decimal

    class Config:
        from_attributes = True