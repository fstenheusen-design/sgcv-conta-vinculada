"""Terceira migração: movimentos bancários e saldo inicial dos contratos

Revision ID: 0003
Revises: 0002
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "contratos",
        sa.Column("saldo_inicial", sa.Numeric(14, 2), nullable=False, server_default="0"),
    )
    op.create_table(
        "movimentos_bancarios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("contrato_id", sa.Integer(), sa.ForeignKey("contratos.id"), nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("tipo", sa.String(10), nullable=False),
        sa.Column("valor", sa.Numeric(14, 2), nullable=False),
        sa.Column("descricao", sa.String(200)),
        sa.Column("documento", sa.String(60)),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("movimentos_bancarios")
    op.drop_column("contratos", "saldo_inicial")