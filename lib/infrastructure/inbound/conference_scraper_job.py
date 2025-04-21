import argparse
import logging
from app.container import Container, conferences
from app.utils import CustomFormatter
from lib.application.ports.inbound.embedding_usecase import EmbeddingUseCase
from lib.application.ports.inbound.paper_crud_usecase import PaperCrudUseCase
from lib.application.ports.inbound.paper_scraper_usecase import PaperScraperUseCase
from lib.application.ports.inbound.scraper_coordinator_usecase import ScraperCoordinatorUseCase
from lib.application.service.scraper.scraper_coordinator_service import ScraperCoordinatorService


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--conference', type=str, required=True,
                        help=f"Possible choices: {", ".join(conferences)}")
    parser.add_argument('--volume', type=str, required=True,
                        help="volume")
    parser.add_argument('--workers', type=str, required=False,
                        help="Max workers", default=2)
    parser.add_argument('--save-pdf', type=bool, required=False,
                        help="Store pdf locally", default=False)

    args = parser.parse_args()
    conference = args.conference
    volume = args.volume
    max_workers = args.workers
    save_pdf = args.save_pdf
    logger = logging.Logger(f"{volume}{conference}scraper")
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(CustomFormatter())
    logger.addHandler(consoleHandler)

    container = Container()
    paper_service: PaperCrudUseCase = container.paper_service()
    scraper_service: PaperScraperUseCase = container.scraper_service(
        conference, volume)
    embedding_service: EmbeddingUseCase = container.embedding_service()

    coordinator_service: ScraperCoordinatorUseCase = ScraperCoordinatorService(
        scraper_service, paper_service, embedding_service, logger, max_workers, save_pdf)
    coordinator_service.crawl_page()


if __name__ == "__main__":
    main()
