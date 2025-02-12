from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from .base import *


class User(Base):
    __tablename__ = 'user'

    email = Column(String(100), primary_key=True)
    nome = Column(String(50), nullable=False)
    admin = Column(Boolean, nullable=True)
    senha = Column(String(255), nullable=False)  # A senha deve ser armazenada como hash

    preferencia = relationship('Preferencia', back_populates='usuario')
    avaliacoes = relationship('Avaliacao', back_populates='usuario')

    def __repr__(self):
        return f'<User {self.nome}>'

# Função para fazer login
def loginUser(email: str, senha: str):
    check_tables_exist(engine)
    adicionar_admin()
    user = db_session.query(User).filter_by(email=email, senha=senha).first()
    if user:  # Se o usuário foi encontrado
        # Armazene o email do usuário na sessão
        session['user_email'] = user.email  # ou algum identificador único
        return user  # Retorna o objeto do usuário autenticado
    return None  # Retorna None se a autenticação falhar

def adicionar_admin():
    """Cria um usuário admin se ele não existir."""
    admin_user = db_session.query(User).filter_by(email="admin@example.com").first()
    if not admin_user:
        admin = User(email="admin@example.com", nome="Administrador", senha="admin123", admin=True)
        db_session.add(admin)
        db_session.commit()
        print("🛠️ Usuário administrador criado!")

# Função para logout (Simples, pois geralmente o logout é feito no front-end)
def logoutUser():
    check_tables_exist(engine)
    session.pop('user_email', None)

# Função para adicionar um usuário
def adicionarUser(email: str, nome: str, senha: str, admin: bool = False):
    check_tables_exist(engine)
    adicionar_admin()
    novo_user = User(email=email, nome=nome, senha=senha, admin=admin)
    db_session.add(novo_user)
    db_session.commit()
    loginUser(email, senha)
    return novo_user

def buscarUser():
    check_tables_exist(engine)
    user = db_session.query(User).filter_by(email = session['user_email']).first()
    return user

def verificarLogin():
    check_tables_exist(engine)
    if session.get('user_email'):
        return True
    else:
        return False
    

