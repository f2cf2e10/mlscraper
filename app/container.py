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
from lib.application.service.scraper.neurips_scraper_service import NeurIpsScraper
from lib.application.service.scraper.openreview_scraper_service import OpenReviewScraper
from lib.application.service.paper_service import PaperService
from lib.application.service.scraper.pmlr_scraper_service import PmlrScraper
from lib.infrastructure.outbound.minio.paper_storage import MinioPaperStorage
from lib.infrastructure.outbound.orm.paper_repository import SQLAlchemyPaperRepository

load_dotenv()


class Conferences(str, Enum):
    NeurIPS = "NeurIPS"
    ICLR = "ICLR"
    PMLR = "PMLR"


conferences = ["NeurIPS", "ICLR", "PMLR"]


class Container(containers.DeclarativeContainer):
    # DB
    db_engine = providers.Singleton(
        create_engine,
        os.getenv("DATABASE_URL"),
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
                                os.getenv("MINIO_HOST"),
                                access_key=os.getenv("MINIO_ACCESS_KEY"),
                                secret_key=os.getenv("MINIO_SECRET_KEY"),
                                secure=False)

    # Providers for services
    paper_repository = providers.Factory(SQLAlchemyPaperRepository, db_session)
    paper_storage = providers.Factory(
        MinioPaperStorage, minio, os.getenv("MINIO_BUCKET"))

    # Services
    embedding_service = providers.Factory(
        EmbeddingService, os.getenv("EMBEDDING_MODEL"),
        int(os.getenv("EMBEDDING_CHUNK_SIZE")),
        int(os.getenv("EMBEDDING_N_PAGES")))
    paper_service = providers.Factory(
        PaperService, paper_repository, paper_storage, embedding_service)

    def _scraper_factory(conference_name: str, year: str) -> PaperScraperUseCase:
        name = conference_name.lower()

        def MyOpenReviewScrapper(year) -> OpenReviewScraper:
            return OpenReviewScraper(year, os.getenv("OPENREVIEW_USER"),
                                     os.getenv("OPENREVIEW_PWD"))

        SCRAPER_CLASSES: dict[str, Type[PaperScraperUseCase]] = {
            "neurips": NeurIpsScraper,
            "pmlr": PmlrScraper,
            "iclr": MyOpenReviewScrapper,
        }
        try:
            scraper_cls = SCRAPER_CLASSES[name]
            return scraper_cls(year)
        except KeyError:
            raise ValueError(f"Unknown conference: {conference_name}")

    scraper_service = providers.Factory(_scraper_factory)
