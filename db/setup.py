from .database import SessionLocal, engine
from .models import Base

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Base.metadata.create_all(engine)