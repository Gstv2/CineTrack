from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import Session
from .base import Base
from .database import db_session  # Certifique-se de que esta importação está correta

class User(Base):
    __tablename__ = 'user'

    email = Column(String(100), primary_key=True)
    nome = Column(String(50), nullable=False)
    admin = Column(Boolean, nullable=True)
    senha = Column(String(255), nullable=False)  # A senha deve ser armazenada como hash

    def __repr__(self):
        return f'<User {self.nome}>'


# Função para fazer login
def login(email: str, senha: str):
    user = db_session.query(User).filter_by(email=email, senha=senha).first()
    if user:
        return user  # Retorna o objeto do usuário autenticado
    return None  # Retorna None se a autenticação falhar


# Função para logout (Simples, pois geralmente o logout é feito no front-end)
def logout():
    return "Usuário deslogado!"


# Função para verificar se o usuário é admin
def verificarAdmin(email: str):
    user = db_session.query(User).filter_by(email=email).first()
    if user and user.admin:
        return True
    return False


# Função para adicionar um usuário
def adicionarUser(email: str, nome: str, senha: str, admin: bool = False):
    novo_user = User(email=email, nome=nome, senha=senha, admin=admin)
    db_session.add(novo_user)
    db_session.commit()
    return novo_user


# Função para remover um usuário
def removerUser(email: str):
    user = db_session.query(User).filter_by(email=email).first()
    if user:
        db_session.delete(user)
        db_session.commit()
        return f"Usuário {email} removido com sucesso."
    return "Usuário não encontrado."
