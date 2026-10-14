from decimal import Decimal

from app.domain.conciliacao import calcular_conciliacao


def test_conciliacao_quadrada():
    """Depósitos exatamente iguais às provisões: divergência zero."""
    c = calcular_conciliacao(
        saldo_inicial=Decimal("0"),
        provisionado_acumulado=Decimal("6595.12"),
        depositado_acumulado=Decimal("6595.12"),
        liberado_acumulado=Decimal("0"),
    )
    assert c.saldo_final == Decimal("6595.12")
    assert c.divergencia_deposito == Decimal("0.00")


def test_conciliacao_com_liberacao():
    c = calcular_conciliacao(
        saldo_inicial=Decimal("1000.00"),
        provisionado_acumulado=Decimal("6595.12"),
        depositado_acumulado=Decimal("6595.12"),
        liberado_acumulado=Decimal("3000.00"),
    )
    assert c.saldo_final == Decimal("4595.12")


def test_conciliacao_com_divergencia():
    """Depositou a menos: divergência negativa sinaliza o gap."""
    c = calcular_conciliacao(
        saldo_inicial=Decimal("0"),
        provisionado_acumulado=Decimal("6595.12"),
        depositado_acumulado=Decimal("6000.00"),
        liberado_acumulado=Decimal("0"),
    )
    assert c.divergencia_deposito == Decimal("-595.12")