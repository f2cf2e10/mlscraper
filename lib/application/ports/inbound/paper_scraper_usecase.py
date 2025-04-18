from abc import ABC, abstractmethod
import io
import logging
from typing import IO, List

import requests

from lib.application.dto.model import PaperDto


logger = logging.getLogger("uvicorn")


class PaperScraperUseCase(ABC):
    @abstractmethod
    def list_papers(self) -> List[PaperDto]:
        pass

    def download_paper_pdf(self, paper: PaperDto) -> IO[bytes]:
        if not paper.url:
            logger.info(f"No PDF URL found for paper: {paper.title}")
            return

        try:
            resp = requests.get(paper.url)
            resp.raise_for_status()
            logger.info(f"Successfully downloaded: {paper.title}")
            return io.BytesIO(resp.content)
        except Exception as e:
            logger.error(f"Failed downloading: {paper.title}")
