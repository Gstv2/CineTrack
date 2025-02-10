from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from datetime import datetime
from sqlalchemy.orm import relationship
from .base import *

class Avaliacao(Base):
    __tablename__ = 'avaliacoes'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(String(100), ForeignKey('user.email'), nullable=False)
    filme_id = Column(Integer, ForeignKey('filmes.id'), nullable=False)
    avaliacao = Column(Integer, nullable=False)  # De 1 a 5
    created_at = Column(DateTime, default=datetime.utcnow)

    usuario = relationship('User', back_populates='avaliacoes')
    filme = relationship('Filmes', back_populates='avaliacoes')

def adicionar_avaliacao(cls, usuario_id: str, filme_id: int, avaliacao: int):
    """Adiciona ou atualiza a avaliação de um filme por um usuário."""
    avaliacao_existente = db_session.query(cls).filter_by(usuario_id=usuario_id, filme_id=filme_id).first()
    if avaliacao_existente:
        avaliacao_existente.avaliacao = avaliacao
    else:
        nova_avaliacao = cls(usuario_id=usuario_id, filme_id=filme_id, avaliacao=avaliacao)
        db_session.add(nova_avaliacao)
    db_session.commit()


def obter_media_avaliacoes(cls, filme_id: int):
    """Obtém a média de avaliações de um filme."""
    media = db_session.query(func.avg(cls.avaliacao)).filter_by(filme_id=filme_id).scalar()
    return round(media, 1) if media else 0
