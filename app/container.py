from enum import Enum
import os
from typing import Literal, Type
from dependency_injector import containers, providers
from dotenv import load_dotenv
from minio import Minio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lib.application.ports.inbound.paper_scraper_usecase import PaperScraperUseCase
from lib.application.service.embedding_service import EmbeddingService
from lib.application.service.neurips_scraper_service import NeurIpsScraper
from lib.application.service.openreview_scraper_service import OpenReviewScraper
from lib.application.service.paper_service import PaperService
from lib.application.service.pmlr_scraper_service import PmlrScraper
from lib.infrastructure.outbound.minio.paper_storage import MinioPaperStorage
from lib.infrastructure.outbound.orm.paper_repository import SQLAlchemyPaperRepository

load_dotenv()


class Conferences(str, Enum):
    NeurIPS = "NeurIPS"
    ICML = "ICML"
    PMLR = "PMLR"
conferences = ["NeurIPS", "ICML", "PMLR"]

class Container(containers.DeclarativeContainer):
    database_url = providers.Singleton(str, os.getenv("DATABASE_URL"))
    minio_host = providers.Singleton(str, os.getenv("MINIO_HOST"))
    minio_access_key = providers.Singleton(str, os.getenv("MINIO_ACCESS_KEY"))
    minio_secret_key = providers.Singleton(str, os.getenv("MINIO_SECRET_KEY"))
    minio_bucket = providers.Singleton(str, os.getenv("MINIO_BUCKET"))
    embedding_model = providers.Singleton(str, os.getenv("EMBEDDING_MODEL"))
    embed_chunk_size = providers.Singleton(
        int, os.getenv("EMBEDDING_CHUNK_SIZE"))
    n_pages_to_embed = providers.Singleton(int, os.getenv("EMBEDDING_N_PAGES"))

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
    embedding_service = providers.Factory(
        EmbeddingService, embedding_model, embed_chunk_size, n_pages_to_embed)
    paper_service = providers.Factory(
        PaperService, paper_repository, paper_storage, embedding_service)

    def _scraper_factory(conference_name: str, year: str) -> PaperScraperUseCase:
        name = conference_name.lower()
        SCRAPER_CLASSES: dict[str, Type[PaperScraperUseCase]] = {
            "neurips": NeurIpsScraper,
            "pmlr": PmlrScraper,
            "iclr": OpenReviewScraper,
        }
        try:
            scraper_cls = SCRAPER_CLASSES[name]
            return scraper_cls(year)
        except KeyError:
            raise ValueError(f"Unknown conference: {conference_name}")

    scraper_service = providers.Factory(_scraper_factory)
