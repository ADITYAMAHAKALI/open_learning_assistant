# app/db/init_db.py
from app.db.base import Base
from app.db.session import engine

def init_db() -> None:
    """
    Simple metadata.create_all for early iterations.

    Later you can replace this with Alembic migrations.
    """
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
