from fastapi import FastAPI

from app.api import auth

app = FastAPI(
    title="SGCV — Sistema de Gestão da Conta Vinculada",
    description="Controle da Conta-Depósito Vinculada (IN 05/2017) — DETRAN/RO",
    version="0.1.0",
)

app.include_router(auth.router)


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok"}