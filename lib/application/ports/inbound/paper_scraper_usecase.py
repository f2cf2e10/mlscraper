from abc import ABC, abstractmethod
from logging import Logger
from typing import List
from lib.application.dto.model import PaperCreateDto


class PaperScraperUseCase(ABC):
    @abstractmethod
    def extract_links(self, logger: Logger) -> List[str]:
        pass

    @abstractmethod
    def process_link(self, link: str, logger: Logger) -> PaperCreateDto:
        pass
