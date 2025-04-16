from abc import ABC, abstractmethod
from typing import IO

from lib.application.dto.model import PaperMetadataDto


class PaperStorage(ABC):
    @abstractmethod
    def upload_file(self, file: IO[bytes]) -> str:
        """ Uploads file to storage """
        pass

    @abstractmethod
    def upload_metadata(self, metadata: PaperMetadataDto) -> str:
        """ Uploads file to storage """
        pass
