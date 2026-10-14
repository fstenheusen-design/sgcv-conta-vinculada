from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ParametroVigencia(Base):
    """Alíquotas de um contrato, versionadas por período."""
    __tablename__ = "parametros_vigencia"

    id: Mapped[int] = mapped_column(primary_key=True)
    contrato_id: Mapped[int] = mapped_column(ForeignKey("contratos.id"), nullable=False)
    vigencia_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    vigencia_fim: Mapped[date | None] = mapped_column(Date)  # None = vigente
    inss_patronal: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    rat: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    fgts: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    multa_rescisoria: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)