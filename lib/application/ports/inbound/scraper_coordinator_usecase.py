from abc import ABC, abstractmethod


class ScraperCoordinatorUseCase(ABC):

    @abstractmethod
    def crawl_page(self):
        pass
