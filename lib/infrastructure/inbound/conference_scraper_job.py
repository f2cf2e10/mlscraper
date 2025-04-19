import argparse
import logging
from app.container import Container, conferences
from lib.application.ports.inbound.paper_crud_usecase import PaperCrudUseCase
from lib.application.ports.inbound.paper_scraper_usecase import PaperScraperUseCase
from lib.application.ports.inbound.scraper_coordinator_usecase import ScraperCoordinatorUseCase
from lib.application.service.scraper.scraper_coordinator_service import ScaperCoordinatorService


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--conference', type=str, required=True,
                        help=f"Possible choices: {", ".join(conferences)}")
    parser.add_argument('--year', type=str, required=True,
                        help="Year")
    parser.add_argument('--workers', type=str, required=False,
                        help="Max workers", default=2)

    args = parser.parse_args()
    conference = args.conference
    year = args.year
    max_workers = args.workers
    logger = logging.Logger(f"{year}{conference}scraper")

    container = Container()
    paper_service: PaperCrudUseCase = container.paper_service()
    scraper_service: PaperScraperUseCase = container.scraper_service(
        conference, year)

    coordinator_service: ScraperCoordinatorUseCase = ScaperCoordinatorService(
        scraper_service, paper_service, logger, max_workers)
    coordinator_service.crawl_page()


if __name__ == "__main__":
    main()
