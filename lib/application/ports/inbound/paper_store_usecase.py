from abc import ABC, abstractmethod
from typing import IO

from lib.application.dto.model import PaperDto


class PaperStoreUseCase(ABC):
    @abstractmethod
    def save(self, metadata: PaperDto, file: IO[bytes]) -> PaperDto:
        """ Stores a new paper """
        pass

    @abstractmethod
    def get(self, paper_key: str) -> IO[bytes]:
        """ Fetches a paper given its key """
        pass
