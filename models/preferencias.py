from sqlalchemy import Column, Integer, String, Text,ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .base import *

class Preferencia(Base):
    __tablename__ = 'preferencias'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(String(100), ForeignKey('user.email'), nullable=False)
    genero = Column(String(50), nullable=False, index=True)
    usuario = relationship('User', back_populates='preferencia')

def adicionarPreferencias(usuario_id: str, genero: str):
    preferencia_existente = db_session.query(Preferencia).filter_by(usuario_id=usuario_id, genero=genero).first()
    if not preferencia_existente:
        nova_preferencia = Preferencia(usuario_id=usuario_id, genero=genero)
        db_session.add(nova_preferencia)
        db_session.commit()

def removerPreferencia(id: str):
    check_tables_exist(engine)
    preferencia = db_session.query(Preferencia).filter_by(id=id).first()
    if preferencia:
        db_session.delete(preferencia)
        db_session.commit()
        return f"Usuário {id} removido com sucesso."
    return "Usuário não encontrado."

def listaPreferencias(email):
    check_tables_exist(engine)
    preferencia = db_session.query(Preferencia).filter_by(usuario_id=email).all()
    return preferencia

def recomendarFilmes(email):
    generos_preferidos = listaPreferencias(email)
    if not generos_preferidos:
        return []  # Se não há preferências, não há recomendações
    
    # Extrai os gêneros preferidos da lista de objetos Preferencia
    generos_preferidos = [preferencia.genero for preferencia in generos_preferidos]
    
    return generos_preferidos

    

