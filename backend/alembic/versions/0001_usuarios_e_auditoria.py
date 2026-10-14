"""Primeira migração: tabelas usuarios e auditoria

Revision ID: 0001
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("login", sa.String(60), nullable=False, unique=True),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("senha_hash", sa.String(255), nullable=False),
        sa.Column("perfil", sa.Enum("ADMIN", "OPERADOR", "CONSULTA", name="perfil_usuario"), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_table(
        "auditoria",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id")),
        sa.Column("acao", sa.String(60), nullable=False),
        sa.Column("detalhe", sa.Text()),
        sa.Column("ip", sa.String(45)),
        sa.Column("data_hora", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("auditoria")
    op.drop_table("usuarios")
    sa.Enum(name="perfil_usuario").drop(op.get_bind(), checkfirst=True)