from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# String de conexão com o MySQL que subiremos no Docker
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://admin:senha123@localhost:3306/estoque_agro"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()