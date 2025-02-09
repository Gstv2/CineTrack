from sqlalchemy import Column, Integer, String, Text,ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base

class Preferencia(Base):
    __tablename__ = 'preferencias'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(String(100), ForeignKey('user.email'), nullable=False)
    genero = Column(String(50), nullable=False, index=True)
    usuario = relationship('User', back_populates='preferencia')


