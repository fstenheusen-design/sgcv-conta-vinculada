from app.database import SessaoLocal
from app.models.usuario import Usuario, Perfil
from app.auth.security import gerar_hash_senha


def criar_admin():
    db = SessaoLocal()
    try:
        if db.query(Usuario).filter(Usuario.login == "admin").first():
            print("Usuário admin já existe. Nada a fazer.")
            return
        admin = Usuario(
            login="admin",
            nome="Administrador SGCV",
            senha_hash=gerar_hash_senha("TroqueEstaSenha@2026"),
            perfil=Perfil.ADMIN,
        )
        db.add(admin)
        db.commit()
        print("Usuário admin criado. SENHA PADRÃO: TroqueEstaSenha@2026 — troque no primeiro acesso!")
    finally:
        db.close()


if __name__ == "__main__":
    criar_admin()