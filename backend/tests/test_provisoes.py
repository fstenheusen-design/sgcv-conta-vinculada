from datetime import date
from decimal import Decimal

from app.domain.parametros import ParametrosContrato
from app.domain.provisoes import calcular_provisao_mensal

PARAMS = ParametrosContrato(vigencia_inicio=date(2026, 1, 1))


def test_mes_completo_salario_2000():
    """Régua: salário R$ 2.000,00, mês completo, alíquotas padrão."""
    p = calcular_provisao_mensal(
        salario_base=Decimal("2000"),
        parametros=PARAMS,
        data_referencia=date(2026, 3, 15),
        data_admissao=date(2025, 1, 1),
    )
    assert p.dias_trabalhados == 30
    assert p.provisao_13o == Decimal("166.67")        # 2000/12
    assert p.provisao_ferias == Decimal("222.22")     # 2000/12 x 4/3
    assert p.encargos_13o == Decimal("38.33")         # 166.67 x 23%
    assert p.encargos_ferias == Decimal("51.11")      # 222.22 x 23%
    assert p.fgts_mensal == Decimal("160.00")         # 2000 x 8%
    assert p.fgts_13o == Decimal("13.33")             # 166.67 x 8%
    assert p.fgts_ferias == Decimal("17.78")          # 222.22 x 8%
    assert p.provisao_rescisoria == Decimal("80.00")  # 2000 x 8% x 50%
    assert p.total_retido == Decimal("749.44")


def test_admissao_no_meio_do_mes():
    """Admitido em 16/03: 15 dias na base 30 (30 - 16 + 1)."""
    p = calcular_provisao_mensal(
        salario_base=Decimal("2000"),
        parametros=PARAMS,
        data_referencia=date(2026, 3, 15),
        data_admissao=date(2026, 3, 16),
    )
    assert p.dias_trabalhados == 15
    assert p.provisao_13o == Decimal("83.33")         # 166.67 x 0,5
    assert p.fgts_mensal == Decimal("80.00")
    assert p.provisao_rescisoria == Decimal("40.00")


def test_demissao_no_meio_do_mes():
    """Demitido em 10/03: 10 dias de fração."""
    p = calcular_provisao_mensal(
        salario_base=Decimal("3000"),
        parametros=PARAMS,
        data_referencia=date(2026, 3, 15),
        data_admissao=date(2025, 1, 1),
        data_demissao=date(2026, 3, 10),
    )
    assert p.dias_trabalhados == 10
    assert p.provisao_13o == Decimal("83.33")         # 3000/12 x 10/30
    assert p.fgts_mensal == Decimal("80.00")          # 3000 x 8% x 10/30


def test_parametros_versionados_por_vigencia():
    """Mudança de RAT no meio do ano: cada mês usa a alíquota vigente."""
    p_antigo = ParametrosContrato(vigencia_inicio=date(2026, 1, 1), vigencia_fim=date(2026, 6, 30), rat=Decimal("0.03"))
    p_novo = ParametrosContrato(vigencia_inicio=date(2026, 7, 1), rat=Decimal("0.04"))
    from app.domain.parametros import parametros_vigentes

    assert parametros_vigentes([p_antigo, p_novo], date(2026, 3, 1)).rat == Decimal("0.03")
    assert parametros_vigentes([p_antigo, p_novo], date(2026, 8, 1)).rat == Decimal("0.04")


def test_salario_invalido_rejeitado():
    import pytest
    with pytest.raises(ValueError):
        calcular_provisao_mensal(
            salario_base=Decimal("0"),
            parametros=PARAMS,
            data_referencia=date(2026, 3, 15),
            data_admissao=date(2025, 1, 1),
        )