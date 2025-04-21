import io
from logging import Logger
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import IO
from lib.application.dto.model import PaperChunkDto, PaperDto
from lib.application.ports.inbound.embedding_usecase import EmbeddingUseCase
from lib.application.ports.inbound.paper_crud_usecase import PaperCrudUseCase
from lib.application.ports.inbound.paper_scraper_usecase import PaperScraperUseCase
from lib.application.ports.inbound.scraper_coordinator_usecase import ScraperCoordinatorUseCase
from lib.application.service.paper_service import PaperService


class ScraperCoordinatorService(ScraperCoordinatorUseCase):
    def __init__(self, scraper_service: PaperScraperUseCase,
                 paper_service: PaperCrudUseCase,
                 embedding_service: EmbeddingUseCase,
                 logger: Logger,
                 max_workers=5,
                 save_pdf=False):
        self.scraper_service = scraper_service
        self.paper_service = paper_service
        self.embedding_service = embedding_service
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.logger = logger
        self.save_pdf = save_pdf

    def crawl_page(self):
        links = self.scraper_service.extract_links(self.logger)

        futures = [self.executor.submit(
            self.scraper_service.process_link, link, self.logger) for link in links]

        for future in as_completed(futures):
            paper = future.result()
            try:
                db_paper = self.paper_service.add(paper)
                if self.save_pdf:
                    pdf = self.download_paper_pdf(paper)
                    saved = self.paper_service.upload(db_paper.id, pdf)
                    if not saved:
                        raise Exception("Failed to save pdf on storage")
                embeddings = self.embedding_service.embeddings(paper.abstract)
                _ = self.paper_service.clean_embeddings(db_paper.id)
                for i, embedding in enumerate(embeddings):
                    _ = self.paper_service.add_embedding(PaperChunkDto(
                        paper_id=db_paper.id,
                        chunk_index=i,
                        embedding=embedding))
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
