from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
db_session = Session()

Base = declarative_base()