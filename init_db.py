from sqlalchemy import create_engine
from app.db.base import Base
from app.models.user import User
from app.models.todo import Todo
from app.core.config import settings

def init_db():
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

if __name__ == "__main__":
    init_db()