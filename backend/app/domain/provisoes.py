from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from app.domain.parametros import ParametrosContrato

DOZE = Decimal("12")
UM_TERCO = Decimal("1") / Decimal("3")
OITO_CENTAVOS = Decimal("0.08")


def _moeda(valor: Decimal) -> Decimal:
    """Arredonda para centavos (meio para cima, padrão contábil)."""
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class ProvisaoMensal:
    dias_trabalhados: int          # 30 = mês completo
    provisao_13o: Decimal
    provisao_ferias: Decimal
    encargos_13o: Decimal
    encargos_ferias: Decimal
    fgts_mensal: Decimal
    fgts_13o: Decimal
    fgts_ferias: Decimal
    provisao_rescisoria: Decimal

    @property
    def total_retido(self) -> Decimal:
        return (
            self.provisao_13o + self.provisao_ferias
            + self.encargos_13o + self.encargos_ferias
            + self.fgts_mensal + self.fgts_13o + self.fgts_ferias
            + self.provisao_rescisoria
        )


def calcular_provisao_mensal(
    salario_base: Decimal,
    parametros: ParametrosContrato,
    data_referencia: date,
    data_admissao: date,
    data_demissao: date | None = None,
) -> ProvisaoMensal:
    """Calcula a provisão do mês para um empregado.

    Regras:
    - Base 30: mês completo = 30 dias, independentemente do mês ter 28, 29 ou 31.
    - Admissão no meio do mês: dias = 30 - dia da admissão + 1 (dia 16 = 15 dias).
    - Demissão no meio do mês: dias = dia da demissão (limitado a 30).
    - 13º e férias: 1/12 do salário por mês (férias acrescidas de 1/3).
    - INSS patronal + RAT incidem sobre 13º e férias.
    - FGTS 8% incide sobre salário, 13º e férias.
    - Provisão rescisória: FGTS 8% x percentual de multa (padrão 50%).
    """
    if salario_base <= 0:
        raise ValueError("Salário base deve ser positivo")

    ultimo_dia = _ultimo_dia_do_mes(data_referencia)
    if data_admissao > ultimo_dia:
        raise ValueError("Admissão posterior ao mês de referência")
    inicio = max(data_admissao, data_referencia.replace(day=1))
    fim = ultimo_dia if data_demissao is None else min(data_demissao, ultimo_dia)
    if fim < inicio:
        raise ValueError("Demissão anterior à admissão")

    if data_demissao is not None and fim < ultimo_dia:
        # Demissão dentro do mês de referência
        if inicio.day > 1:
            dias = min(fim.day, 30) - inicio.day + 1
        else:
            dias = min(fim.day, 30)
    else:
        # Mês completo na base 30 (com ou sem admissão no meio do mês)
        dias = 30 - inicio.day + 1 if inicio.day > 1 else 30

    fracao = Decimal(dias) / Decimal("30")

    decimo_terceiro = _moeda(salario_base / DOZE * fracao)
    ferias = _moeda(salario_base / DOZE * (Decimal("1") + UM_TERCO) * fracao)

    enc_13 = _moeda(decimo_terceiro * parametros.encargos_previdenciarios)
    enc_fer = _moeda(ferias * parametros.encargos_previdenciarios)

    fgts_sal = _moeda(salario_base * OITO_CENTAVOS * fracao)
    fgts_13 = _moeda(decimo_terceiro * parametros.fgts)
    fgts_fer = _moeda(ferias * parametros.fgts)

    rescisoria = _moeda(salario_base * parametros.fgts * parametros.multa_rescisoria * fracao)

    return ProvisaoMensal(
        dias_trabalhados=dias,
        provisao_13o=decimo_terceiro,
        provisao_ferias=ferias,
        encargos_13o=enc_13,
        encargos_ferias=enc_fer,
        fgts_mensal=fgts_sal,
        fgts_13o=fgts_13,
        fgts_ferias=fgts_fer,
        provisao_rescisoria=rescisoria,
    )


def _ultimo_dia_do_mes(data_ref: date) -> date:
    if data_ref.month == 12:
        return date(data_ref.year, 12, 31)
    return date(data_ref.year, data_ref.month + 1, 1) - __import__("datetime").timedelta(days=1)