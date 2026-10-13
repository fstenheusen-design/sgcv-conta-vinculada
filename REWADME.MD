# SGCV — Sistema de Gestão da Conta Vinculada

Sistema para controle da Conta-Depósito Vinculada (IN 05/2017, art. 18 e Anexo VII)
nos contratos de serviços continuados do DETRAN/RO.

## Stack
Python 3.12 · FastAPI · PostgreSQL 16 · SQLAlchemy/Alembic · Streamlit · Docker

## Como subir o banco (Fase 0)
1. Copie `.env.example` para `.env` e defina a senha
2. `docker compose up -d`
3. Verifique: `docker compose ps` (status healthy)