from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from settings import settings

engine = create_engine(
    url=settings.DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()