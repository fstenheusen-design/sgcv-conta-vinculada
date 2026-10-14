from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel


class ItemMedicaoResposta(BaseModel):
    empregado_id: int
    matricula: str
    nome: str
    dias_trabalhados: int
    provisao_13o: Decimal
    provisao_ferias: Decimal
    encargos_13o: Decimal
    encargos_ferias: Decimal
    fgts_mensal: Decimal
    fgts_13o: Decimal
    fgts_ferias: Decimal
    provisao_rescisoria: Decimal
    total: Decimal


class MedicaoResposta(BaseModel):
    id: int
    contrato_id: int
    ano: int
    mes: int
    status: str
    total_retido: Decimal
    fechado_em: datetime | None
    itens: list[ItemMedicaoResposta]