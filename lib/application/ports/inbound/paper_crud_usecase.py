from abc import ABC, abstractmethod
from typing import IO, List

from lib.application.dto.model import PaperChunkCreateDto, PaperChunkDto, PaperCreateDto, PaperDto, SearchScorePaperDto


class PaperCrudUseCase(ABC):

    @abstractmethod
    def add(self, metadata: PaperCreateDto) -> PaperDto:
        """ Stores a new paper """
        pass

    @abstractmethod
    def get_by_id(self, paper_id: str) -> PaperDto:
        """ Gets a paper by id"""
        pass

    @abstractmethod
    def search(self, query: str) -> List[SearchScorePaperDto]:
        """ Searches for papers """
        pass

    @abstractmethod
    def find_similar(self, text: str) -> List[SearchScorePaperDto]:
        """ Searches for papers """
        pass

    @abstractmethod
    def add_embedding(self, chunk=PaperChunkCreateDto) -> PaperChunkDto:
        """ Updates paper with embeddings vector """
        pass
