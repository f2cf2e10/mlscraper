from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from lib.domain.model import Paper


class PaperDto(BaseModel):
    id: Optional[str]
    title: str
    authors: List[str] = []
    publication_date: datetime
    pdf: str
    url: Optional[str] = None
    abstract: Optional[str] = None
    conference: Optional[str] = None
    summary: Optional[str] = None
    keywords: List[str] = []

    @classmethod
    def from_entity(cls, entity: Paper) -> "PaperDto":
        return cls(title=entity.title,
                   authors=entity.authors,
                   abstract=entity.abstract,
                   conference=entity.conference,
                   publication_date=entity.publication_date,
                   pdf=entity.pdf,
                   url=entity.url,
                   summary=entity.summary,
                   keywords=entity.keywords,
                   id=entity.id)

    def to_entity(self) -> Paper:
        entity = Paper(title=self.title,
                       authors=self.authors,
                       abstract=self.abstract,
                       conference=self.conference,
                       publication_date=self.publication_date,
                       pdf=self.pdf,
                       url=self.url,
                       summary=self.summary,
                       keywords=self.keywords,
                       id=self.id)
        return entity
