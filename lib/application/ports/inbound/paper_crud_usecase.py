from abc import ABC, abstractmethod
from typing import IO, List

from lib.application.dto.model import PaperDto


class PaperCrudUseCase(ABC):
    @abstractmethod
    def create(self, paper: PaperDto) -> PaperDto:
        """ Saves a new paper """
        pass

    @abstractmethod
    def get_by_id(self, paper_id: str) -> PaperDto:
        """ Gets a paper by id"""
        pass

    @abstractmethod
    def search(self, query: str) -> List[PaperDto]:
        """ Searches for papers """
        pass

    @abstractmethod
    def find_similar(self, text: str) -> List[PaperDto]:
        """ Searches for papers """
        pass


