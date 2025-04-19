import io
from logging import Logger
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import IO
from lib.application.dto.model import PaperDto
from lib.application.ports.inbound.paper_crud_usecase import PaperCrudUseCase
from lib.application.ports.inbound.paper_scraper_usecase import PaperScraperUseCase
from lib.application.ports.inbound.scraper_coordinator_usecase import ScraperCoordinatorUseCase
from lib.application.service.paper_service import PaperService


class ScaperCoordinatorService(ScraperCoordinatorUseCase):
    def __init__(self, scraper_service: PaperScraperUseCase,
                 paper_service: PaperCrudUseCase,
                 logger: Logger,
                 max_workers=5):
        self.scraper_service = scraper_service
        self.paper_service = paper_service
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.logger = logger

    def crawl_page(self):
        links = self.scraper_service.extract_links(self.logger)

        futures = [self.executor.submit(
            self.scraper_service.process_link, link, self.logger) for link in links]

        for future in as_completed(futures):
            try:
                paper = future.result()
                pdf = self.download_paper_pdf(paper)
                db_paper = self.paper_service.add(paper)
                saved = self.paper_service.upload(db_paper.id, pdf)
                if saved:
                    # once uploaded, it will trigger an event to create embeddings, wait for that for HW constraints
                    time.sleep(5)
                else:
                    raise Exception("Failed to save pdf on storage")
            except Exception as e:
                self.logger.error(f"Error processing link {paper.title}: {e}")

    def download_paper_pdf(self, paper: PaperDto) -> IO[bytes]:
        if not paper.url:
            self.logger.error(f"No PDF URL found for paper: {paper.title}")
            return
        try:
            resp = requests.get(paper.url)
            resp.raise_for_status()
            self.logger.info(f"Successfully downloaded: {paper.title}")
            return io.BytesIO(resp.content)
        except Exception as e:
            self.logger.error(f"Failed downloading: {paper.title}")
