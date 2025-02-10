from sqlalchemy.orm import declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from flask import session, flash
from sqlalchemy.sql import text


# Senha e configuração de conexão

password = quote_plus("Lgns123!")
engine = create_engine(f"mysql://root:{password}@127.0.0.1:3306/db_equipe09")

# Criando a sessão para interação com o banco
Session = sessionmaker(bind=engine)
db_session = Session()

# Definindo a base para as tabelas
Base = declarative_base()

# Remova o decorator @check_tables_exist desta linha
def check_tables_exist(engine):
    insp = inspect(engine)
    table_names = insp.get_table_names()

    # Lista de nomes de tabelas que você espera existir
    expected_tables = ['avaliacoes', 'user','filmes', 'preferencias']

    for table_name in expected_tables:
        if table_name not in table_names:
            # Vincule os modelos ao engine  
            Base.metadata.create_all(engine)
            print("Tabelas foram criadas com sucesso!")
            return False

    return True

# Testando a conexão com o banco de dados
try:
    # Usando 'text' para garantir que a consulta seja executável
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Conexão bem-sucedida com o banco de dados!")
except Exception as e:
    print(f"Erro de conexão: {e}")
    