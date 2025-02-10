from sqlalchemy import Column, Integer, String, Text, Float, Date
from werkzeug.utils import secure_filename
from sqlalchemy.orm import relationship
from datetime import datetime, date
from flask import current_app
from .base import *
import os

class Filmes(Base):
    __tablename__ = 'filmes'

    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=False)
    ano = Column(Date, nullable=False)
    genero = Column(String(50), nullable=False, index=True)
    classificacao = Column(Float, default=0.0)  # Média das avaliações
    imagem = Column(String(255), nullable=True)  # Caminho da imagem do filme
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)

    avaliacoes = relationship('Avaliacao', back_populates='filme', cascade='all, delete-orphan')

# Função para salvar a imagem do filme
def salvar_imagem(imagem, pasta_destino='static/imgs/filmes'):
    """
    Função para salvar a imagem na pasta e retornar o caminho relativo.
    """
    # Certifique-se de que a pasta de destino existe
    pasta_destino_completa = os.path.join(current_app.root_path, pasta_destino)
    if not os.path.exists(pasta_destino_completa):
        os.makedirs(pasta_destino_completa)

    # Gerar nome seguro para a imagem
    nome_imagem = secure_filename(imagem.filename)
    caminho_imagem = os.path.join(pasta_destino_completa, nome_imagem)

    # Salvar a imagem
    imagem.save(caminho_imagem)

    # Retornar o caminho relativo da imagem para armazenar no banco de dados
    return os.path.join(pasta_destino, nome_imagem)

# Função para adicionar um filme
def adicionarFilme(nome: str, descricao: str, ano: int, genero: str, imagem=None, classificacao: float = 0.0):
    check_tables_exist(engine)
    
    # Processar a imagem, se fornecida
    caminho_imagem = None
    if imagem:
        caminho_imagem = salvar_imagem(imagem)  # Salva a imagem e obtém o caminho relativo

    novo_filme = Filmes(
        nome=nome,
        descricao=descricao,
        ano=ano,
        genero=genero,
        classificacao=classificacao,
        imagem=caminho_imagem  # Armazena o caminho da imagem no banco de dados
    )
    
    db_session.add(novo_filme)
    db_session.commit()
    return novo_filme

# Função para remover um filme
def removerFilme(filme_id: int):
    check_tables_exist(engine)
    filme = db_session.query(Filmes).filter_by(id=filme_id).first()
    if filme:
        db_session.delete(filme)
        db_session.commit()
        return f"Filme {filme_id} removido com sucesso."
    return "Filme não encontrado."

# Função para buscar filmes por gênero
def buscarFilmesPorGenero(generos: list):
    check_tables_exist(engine)
    filmes = db_session.query(Filmes).filter(Filmes.genero.in_(generos)).all()
    return filmes

# Função para listar todos os filmes
def listarFilmes():
    check_tables_exist(engine)
    filmes = db_session.query(Filmes).all()
    return filmes

# Função para buscar filmes com base no nome
def buscarFilmesPorNome(nome: str):
    check_tables_exist(engine)
    filmes = db_session.query(Filmes).filter(Filmes.nome.like(f'%{nome}%')).all()
    return filmes

# Função para atualizar informações de um filme
def atualizarFilme(filme_id: int, nome: str = None, descricao: str = None, ano: int = None, genero: str = None, classificacao: float = None):
    check_tables_exist(engine)
    filme = db_session.query(Filmes).filter_by(id=filme_id).first()
    if filme:
        if nome:
            filme.nome = nome
        if descricao:
            filme.descricao = descricao
        if ano:
            filme.ano = ano
        if genero:
            filme.genero = genero
        if classificacao is not None:  # Permite que a classificação seja atualizada, incluindo 0
            filme.classificacao = classificacao
        db_session.commit()
        return filme
    return "Filme não encontrado."
