from abc import ABC, abstractmethod
from typing import List, Optional

from lib.domain.model import Paper, PaperChunk, PaperCreate, SearchScorePaper


class PaperRepository(ABC):
    @abstractmethod
    def create(self, paper: PaperCreate) -> Paper:
        """ Saves a new paper"""
        pass

    @abstractmethod
    def get_by_id(self, paper_id: str) -> Optional[Paper]:
        """ Fetches paper by ID from the repository """
        pass

    @abstractmethod
    def update(self, paper_id: str, paper: Paper) -> Optional[Paper]:
        """Updates a paper"""
        pass

    @abstractmethod
    def add_embedding(self, embedding: PaperChunk) -> Optional[PaperChunk]:
        pass

    @abstractmethod
    def similarity_search(self, embedding: List[float]) -> List[SearchScorePaper]:
        """Finds similar chats to the embedding."""
        pass

    @abstractmethod
    def text_search(self, query: str) -> List[Paper]:
        """Finds papers by query text."""
        pass

    @abstractmethod
    def delete(self, paper_id: str) -> bool:
        """Deletes a paper."""
        pass
