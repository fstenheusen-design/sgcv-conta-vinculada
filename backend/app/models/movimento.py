from datetime import date, datetime

from sqlalchemy import String, Numeric, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MovimentoBancario(Base):
    """Movimentação da conta-depósito vinculada: depósitos da contratada
    e liberações para pagamento de verbas."""
    __tablename__ = "movimentos_bancarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    contrato_id: Mapped[int] = mapped_column(ForeignKey("contratos.id"), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)  # DEPOSITO | LIBERACAO
    valor: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(200))
    documento: Mapped[str | None] = mapped_column(String(60))
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )