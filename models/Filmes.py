from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Filmes(Base):
    __tablename__ = 'filmes'

    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=False)
    ano = Column(Integer, nullable=False)
    genero = Column(String(50), nullable=False, index=True)
    classificacao = Column(Float, default=0.0)  # Média das avaliações
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    avaliacoes = relationship('Avaliacao', back_populates='filme', cascade='all, delete-orphan')
