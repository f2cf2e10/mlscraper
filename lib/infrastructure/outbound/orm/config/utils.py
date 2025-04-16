from app.container import Container
from lib.infrastructure.outbound.orm.config.model import Base
from sqlalchemy import text

container = Container()


def init_db():
    engine = container.db_engine()
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    print("Done.")


if __name__ == "__main__":
    init_db()
