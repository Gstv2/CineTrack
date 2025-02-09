from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from urllib.parse import quote_plus

# Senha e configuração de conexão
password = quote_plus("Lgns123!")
engine = create_engine(f"mysql://root:{password}@127.0.0.1:3306/db_equipe09")

# Criando a sessão para interação com o banco
Session = sessionmaker(bind=engine)
db_session = Session()

# Definindo a base para as tabelas
Base = declarative_base()

# Testando a conexão com o banco de dados
try:
    # Usando 'text' para garantir que a consulta seja executável
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Conexão bem-sucedida com o banco de dados!")
except Exception as e:
    print(f"Erro de conexão: {e}")
    