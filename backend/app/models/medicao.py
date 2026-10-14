from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import String, Integer, Numeric, Date, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MedicaoMensal(Base):
    """Fechamento mensal das provisões de um contrato.
    Uma vez FECHADA, torna-se imutável (trilha de auditoria)."""
    __tablename__ = "medicoes"
    __table_args__ = (UniqueConstraint("contrato_id", "ano", "mes"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    contrato_id: Mapped[int] = mapped_column(ForeignKey("contratos.id"), nullable=False)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="ABERTA")
    total_retido: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    fechado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    fechado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ItemMedicao(Base):
    """Provisão calculada de um empregado dentro de uma medição."""
    __tablename__ = "itens_medicao"

    id: Mapped[int] = mapped_column(primary_key=True)
    medicao_id: Mapped[int] = mapped_column(ForeignKey("medicoes.id"), nullable=False)
    empregado_id: Mapped[int] = mapped_column(ForeignKey("empregados.id"), nullable=False)
    data_referencia: Mapped[date] = mapped_column(Date, nullable=False)
    dias_trabalhados: Mapped[int] = mapped_column(Integer, nullable=False)
    provisao_13o: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    provisao_ferias: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    encargos_13o: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    encargos_ferias: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    fgts_mensal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    fgts_13o: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    fgts_ferias: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    provisao_rescisoria: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)