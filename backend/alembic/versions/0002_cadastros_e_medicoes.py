"""Segunda migração: contratos, empregados, parâmetros e medições

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contratos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("numero", sa.String(60), nullable=False, unique=True),
        sa.Column("contratada", sa.String(200), nullable=False),
        sa.Column("faturamento_mensal", sa.Numeric(14, 2), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_table(
        "empregados",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("contrato_id", sa.Integer(), sa.ForeignKey("contratos.id"), nullable=False),
        sa.Column("matricula", sa.String(30), nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("funcao", sa.String(120), nullable=False),
        sa.Column("salario_base", sa.Numeric(12, 2), nullable=False),
        sa.Column("data_admissao", sa.Date(), nullable=False),
        sa.Column("data_demissao", sa.Date()),
    )
    op.create_table(
        "parametros_vigencia",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("contrato_id", sa.Integer(), sa.ForeignKey("contratos.id"), nullable=False),
        sa.Column("vigencia_inicio", sa.Date(), nullable=False),
        sa.Column("vigencia_fim", sa.Date()),
        sa.Column("inss_patronal", sa.Numeric(6, 4), nullable=False),
        sa.Column("rat", sa.Numeric(6, 4), nullable=False),
        sa.Column("fgts", sa.Numeric(6, 4), nullable=False),
        sa.Column("multa_rescisoria", sa.Numeric(6, 4), nullable=False),
    )
    op.create_table(
        "medicoes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("contrato_id", sa.Integer(), sa.ForeignKey("contratos.id"), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(10), nullable=False, server_default="ABERTA"),
        sa.Column("total_retido", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("fechado_por_id", sa.Integer(), sa.ForeignKey("usuarios.id")),
        sa.Column("fechado_em", sa.DateTime(timezone=True)),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("contrato_id", "ano", "mes"),
    )
    op.create_table(
        "itens_medicao",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("medicao_id", sa.Integer(), sa.ForeignKey("medicoes.id"), nullable=False),
        sa.Column("empregado_id", sa.Integer(), sa.ForeignKey("empregados.id"), nullable=False),
        sa.Column("data_referencia", sa.Date(), nullable=False),
        sa.Column("dias_trabalhados", sa.Integer(), nullable=False),
        sa.Column("provisao_13o", sa.Numeric(12, 2), nullable=False),
        sa.Column("provisao_ferias", sa.Numeric(12, 2), nullable=False),
        sa.Column("encargos_13o", sa.Numeric(12, 2), nullable=False),
        sa.Column("encargos_ferias", sa.Numeric(12, 2), nullable=False),
        sa.Column("fgts_mensal", sa.Numeric(12, 2), nullable=False),
        sa.Column("fgts_13o", sa.Numeric(12, 2), nullable=False),
        sa.Column("fgts_ferias", sa.Numeric(12, 2), nullable=False),
        sa.Column("provisao_rescisoria", sa.Numeric(12, 2), nullable=False),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("itens_medicao")
    op.drop_table("medicoes")
    op.drop_table("parametros_vigencia")
    op.drop_table("empregados")
    op.drop_table("contratos")