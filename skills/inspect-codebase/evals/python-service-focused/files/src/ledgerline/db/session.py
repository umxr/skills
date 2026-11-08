from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ledgerline.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def get_session():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()
