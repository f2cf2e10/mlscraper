from abc import ABC, abstractmethod
from typing import IO


class PaperStorage(ABC):
    @abstractmethod
    def upload_file(self, key: str, content: IO[bytes]) -> bool:
        """ Uploads file to storage """
        pass

    @abstractmethod
    def get_file(self, key: str) -> IO[bytes]:
        """ Get file """
        pass

