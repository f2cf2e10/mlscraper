import os
from dependency_injector import containers, providers
from dotenv import load_dotenv
from minio import Minio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lib.application.service.embedding_service import EmbeddingService
from lib.application.service.paper_service import PaperService
from lib.infrastructure.outbound.minio.paper_storage import MinioPaperStorage
from lib.infrastructure.outbound.orm.paper_repository import SQLAlchemyPaperRepository

load_dotenv()


class Container(containers.DeclarativeContainer):
    database_url = providers.Singleton(str, os.getenv("DATABASE_URL"))
    minio_host = providers.Singleton(str, os.getenv("MINIO_HOST"))
    minio_access_key = providers.Singleton(str, os.getenv("MINIO_ACCESS_KEY"))
    minio_secret_key = providers.Singleton(str, os.getenv("MINIO_SECRET_KEY"))
    minio_bucket = providers.Singleton(str, os.getenv("MINIO_BUCKET"))
    embedding_model = providers.Singleton(str, os.getenv("EMBEDDING_MODEL"))

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

    minio = providers.Singleton(Minio,
                                minio_host,
                                access_key=minio_access_key,
                                secret_key=minio_secret_key,
                                secure=False)

    # Providers for services
    paper_repository = providers.Factory(SQLAlchemyPaperRepository, db_session)
    paper_storage = providers.Factory(MinioPaperStorage, minio, minio_bucket)

    # Services
    embedding_service = providers.Factory(EmbeddingService, embedding_model)
    paper_service = providers.Factory(
        PaperService, paper_repository, paper_storage, embedding_service)
