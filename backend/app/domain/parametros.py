from dataclasses import dataclass
from datetime import date
from decimal import Decimal

# Valores padrão da IN 05/2017 — podem ser sobrescritos por contrato/vigência
INSS_PATRONAL_PADRAO = Decimal("0.20")   # 20% — cota patronal
RAT_PADRAO = Decimal("0.03")             # 3% — RAT/FAP (ajustável por CNAE da contratada)
FGTS_PADRAO = Decimal("0.08")            # 8% — depósito mensal de FGTS
MULTA_RESCISORIA_PADRAO = Decimal("0.50")  # 50% do FGTS provisionado p/ rescisão


@dataclass(frozen=True)
class ParametrosContrato:
    """Alíquotas vigentes em um período, por contrato."""
    vigencia_inicio: date
    vigencia_fim: date | None = None  # None = vigente até nova versão
    inss_patronal: Decimal = INSS_PATRONAL_PADRAO
    rat: Decimal = RAT_PADRAO
    fgts: Decimal = FGTS_PADRAO
    multa_rescisoria: Decimal = MULTA_RESCISORIA_PADRAO

    @property
    def encargos_previdenciarios(self) -> Decimal:
        """INSS + RAT incidem sobre provisões de 13º e férias."""
        return self.inss_patronal + self.rat


def parametros_vigentes(parametros: list[ParametrosContrato], data_ref: date) -> ParametrosContrato:
    """Retorna a versão de parâmetros vigente na data de referência.
    Se houver sobreposição, vale a de vigência mais recente."""
    vigentes = [
        p for p in parametros
        if p.vigencia_inicio <= data_ref and (p.vigencia_fim is None or data_ref <= p.vigencia_fim)
    ]
    if not vigentes:
        raise ValueError(f"Sem parâmetros vigentes em {data_ref}")
    return max(vigentes, key=lambda p: p.vigencia_inicio)