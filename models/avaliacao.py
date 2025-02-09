from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from .base import Base

class Avaliacao(Base):
    __tablename__ = 'avaliacoes'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(String(100), ForeignKey('user.email'), nullable=False)
    filme_id = Column(Integer, ForeignKey('filmes.id'), nullable=False)
    avaliacao = Column(Integer, nullable=False)  # De 1 a 5
    created_at = Column(DateTime, default=datetime.utcnow)

    usuario = relationship('User', back_populates='avaliacoes')
    filme = relationship('Filmes', back_populates='avaliacoes')
