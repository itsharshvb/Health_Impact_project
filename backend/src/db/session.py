# db/session.py

from core.config import SessionLocal, engine
from db.models import Base  # adjust import if needed

# Automatically create tables if they don't exist
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
