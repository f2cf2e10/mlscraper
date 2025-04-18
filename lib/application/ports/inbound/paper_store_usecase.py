from abc import ABC, abstractmethod
from typing import IO


class PaperStoreUseCase(ABC):
    @abstractmethod
    def upload(self, key: str, content: IO[bytes]) -> bool:
        """ Stores a new paper """
        pass

    @abstractmethod
    def download(self, key: str) -> IO[bytes]:
        """ Fetches a paper given its key """
        pass
