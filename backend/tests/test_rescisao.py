from datetime import date
from decimal import Decimal

from app.domain.rescisao import calcular_rescisao


def test_rescisao_completa_salario_2000():
    """Admitido 01/01/2025, demitido 15/03/2026, aviso 30 dias, saldo FGTS R$ 1.920."""
    r = calcular_rescisao(
        salario_base=Decimal("2000"),
        data_admissao=date(2025, 1, 1),
        data_demissao=date(2026, 3, 15),
        fgts_saldo_anterior=Decimal("1920"),
    )
    assert r.saldo_salario == Decimal("1000.00")            # 15 dias = 15/30 x 2000
    assert r.aviso_previo == Decimal("2000.00")
    assert r.decimo_terceiro_proporcional == Decimal("500.00")  # 3 meses no ano da demissão x 166,67
    assert r.ferias_proporcionais == Decimal("666.67")      # 500 x 4/3
    assert r.multa_fgts_40 == Decimal("832.00")             # (1920 + 160) x 40%
    assert r.total == Decimal("4998.67")


def test_rescisao_sem_aviso_indenizado():
    r = calcular_rescisao(
        salario_base=Decimal("2000"),
        data_admissao=date(2025, 1, 1),
        data_demissao=date(2026, 3, 15),
        dias_aviso_indenizado=0,
        fgts_saldo_anterior=Decimal("1920"),
    )
    assert r.aviso_previo == Decimal("0.00")
    assert r.multa_fgts_40 == Decimal("768.00")             # 1920 x 40% (sem FGTS do aviso)


def test_datas_invalidas_rejeitadas():
    import pytest
    with pytest.raises(ValueError):
        calcular_rescisao(
            salario_base=Decimal("2000"),
            data_admissao=date(2026, 6, 1),
            data_demissao=date(2026, 3, 15),
        )