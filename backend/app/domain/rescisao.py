from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from app.domain.parametros import ParametrosContrato


def _moeda(valor: Decimal) -> Decimal:
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Rescisao:
    saldo_salario: Decimal
    aviso_previo: Decimal
    decimo_terceiro_proporcional: Decimal
    ferias_proporcionais: Decimal      # já acrescidas de 1/3
    multa_fgts_40: Decimal

    @property
    def total(self) -> Decimal:
        return (
            self.saldo_salario + self.aviso_previo
            + self.decimo_terceiro_proporcional + self.ferias_proporcionais
            + self.multa_fgts_40
        )


def calcular_rescisao(
    salario_base: Decimal,
    data_admissao: date,
    data_demissao: date,
    dias_aviso_indenizado: int = 30,
    fgts_saldo_anterior: Decimal = Decimal("0"),
    parametros: ParametrosContrato | None = None,
) -> Rescisao:
    """Calcula as verbas rescisórias do empregado.

    - Saldo de salário: dias trabalhados no mês da demissão (base 30).
    - Aviso prévio indenizado: dias informados (padrão 30).
    - 13º proporcional: meses trabalhados NO ANO DA DEMISSÃO
      (fração de 15+ dias conta como mês inteiro).
    - Férias proporcionais + 1/3: mesmo critério do 13º.
    - Multa FGTS 40%: sobre o saldo de FGTS (anterior + depósitos do aviso).
    """
    if data_demissao < data_admissao:
        raise ValueError("Demissão anterior à admissão")

    dias_saldo = min(data_demissao.day, 30)
    saldo_salario = _moeda(salario_base / Decimal("30") * Decimal(dias_saldo))
    aviso = _moeda(salario_base / Decimal("30") * Decimal(dias_aviso_indenizado))

    meses_13 = _meses_proporcionais(data_admissao, data_demissao)
    dt_prop = _moeda(salario_base / Decimal("12") * Decimal(meses_13))
    ferias_prop = _moeda(salario_base / Decimal("12") * Decimal(meses_13) * Decimal("4") / Decimal("3"))

    fgts_do_aviso = _moeda(aviso * Decimal("0.08"))
    base_multa = fgts_saldo_anterior + fgts_do_aviso
    multa = _moeda(base_multa * Decimal("0.40"))

    return Rescisao(
        saldo_salario=saldo_salario,
        aviso_previo=aviso,
        decimo_terceiro_proporcional=dt_prop,
        ferias_proporcionais=ferias_prop,
        multa_fgts_40=multa,
    )


def _meses_proporcionais(admissao: date, demissao: date) -> int:
    """Meses trabalhados no ano da demissão; fração de 15+ dias conta como mês inteiro."""
    inicio_contagem = max(admissao, date(demissao.year, 1, 1))
    meses = demissao.month - inicio_contagem.month
    if demissao.day >= 15:
        meses += 1
    return max(meses, 0)