from datetime import date

from sqlalchemy import String, Numeric, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Empregado(Base):
    __tablename__ = "empregados"

    id: Mapped[int] = mapped_column(primary_key=True)
    contrato_id: Mapped[int] = mapped_column(ForeignKey("contratos.id"), nullable=False)
    matricula: Mapped[str] = mapped_column(String(30), nullable=False)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    funcao: Mapped[str] = mapped_column(String(120), nullable=False)
    salario_base: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    data_admissao: Mapped[date] = mapped_column(Date, nullable=False)
    data_demissao: Mapped[date | None] = mapped_column(Date)