import os
from dependency_injector import containers, providers
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()


class Container(containers.DeclarativeContainer):
    database_url = providers.Singleton(str, os.getenv("DATABASE_URL"))

    # DB
    db_engine = providers.Singleton(
        create_engine,
        database_url,
        pool_size=5,  # Pool size for SQLite
        max_overflow=10,  # Allow overflow connections
        echo=True
    )
    session_factory = providers.Singleton(
        sessionmaker,
        bind=db_engine,
        autocommit=False,
        autoflush=False
    )
    db_session = providers.Resource(
        lambda session_factory: session_factory(),
        session_factory
    )
