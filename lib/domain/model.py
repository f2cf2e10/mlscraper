from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from lib.infrastructure.outbound.orm.config.model import Paper as PaperOrm


class PaperCreate(BaseModel):
    title: str
    authors: List[str] = []
    publication_date: datetime
    pdf: str
    url: Optional[str] = None
    abstract: Optional[str] = None
    conference: Optional[str] = None
    summary: Optional[str] = None
    keywords: List[str] = []

    def to_entity(self) -> PaperOrm:
        entity = PaperOrm(title=self.title,
                          authors=self.authors,
                          abstract=self.abstract,
                          conference=self.conference,
                          publication_date=self.publication_date,
                          pdf=self.pdf,
                          url=self.url,
                          summary=self.summary,
                          keywords=self.keywords)
        return entity


class Paper(PaperCreate):
    id: str
    embedding = Optional[List[float]] = None
    created_at: datetime

    @classmethod
    def from_entity(cls, entity: PaperOrm) -> "Paper":
        return cls(title=entity.title,
                   authors=entity.authors,
                   abstract=entity.abstract,
                   conference=entity.conference,
                   publication_date=entity.publication_date,
                   pdf=entity.pdf,
                   url=entity.url,
                   summary=entity.summary,
                   keywords=entity.keywords,
                   embedding=entity.embedding,
                   created_at=entity.created_at,
                   id=entity.id)

    def to_entity(self) -> PaperOrm:
        entity = PaperOrm(title=self.title,
                          authors=self.authors,
                          abstract=self.abstract,
                          conference=self.conference,
                          publication_date=self.publication_date,
                          pdf=self.pdf,
                          url=self.url,
                          summary=self.summary,
                          keywords=self.keywords,
                          embedding=self.embedding,
                          created_at=self.created_at,
                          id=self.id)
        return entity
