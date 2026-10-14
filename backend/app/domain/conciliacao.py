from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Conciliacao:
    saldo_inicial: Decimal
    provisionado_acumulado: Decimal
    depositado_acumulado: Decimal
    liberado_acumulado: Decimal
    saldo_final: Decimal
    divergencia_deposito: Decimal   # depositado - provisionado (ideal: 0,00)


def calcular_conciliacao(
    saldo_inicial: Decimal,
    provisionado_acumulado: Decimal,
    depositado_acumulado: Decimal,
    liberado_acumulado: Decimal,
) -> Conciliacao:
    """Conciliação da conta vinculada (aba Conciliacao da planilha de referência).

    - Saldo final = saldo inicial + depósitos - liberações.
    - Divergência de depósito = depositado - provisionado
      (positiva: depositou a mais; negativa: depositou a menos).
    """
    saldo_final = saldo_inicial + depositado_acumulado - liberado_acumulado
    divergencia = depositado_acumulado - provisionado_acumulado
    return Conciliacao(
        saldo_inicial=saldo_inicial,
        provisionado_acumulado=provisionado_acumulado,
        depositado_acumulado=depositado_acumulado,
        liberado_acumulado=liberado_acumulado,
        saldo_final=saldo_final,
        divergencia_deposito=divergencia,
    )