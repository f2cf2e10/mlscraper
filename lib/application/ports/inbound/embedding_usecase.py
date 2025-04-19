from abc import ABC, abstractmethod
from typing import IO, List


class EmbeddingUseCase(ABC):
    @abstractmethod
    def extract_text_from_pdf(self, pdf_file: IO[bytes]) -> str:
        """ Extracts text from pdf"""
        pass

    @abstractmethod
    def split_text(self, text: str) -> List[str]:
        """ Splits text into smaller chuncks"""
        pass

    @abstractmethod
    def embeddings(self, text:str) -> List[List[float]]:
        pass

    @abstractmethod
    def get_embeddings(self, pdf_file: IO[bytes]) -> List[List[float]]:
        """ Get embeddings per chunck """
        pass
