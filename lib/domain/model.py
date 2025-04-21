from pydantic import BaseModel
import pydantic
from typing import List, Optional
from datetime import datetime
from lib.infrastructure.outbound.orm.config.model import Paper as PaperOrm, PaperChunk as PaperChunkOrm


class PaperCreate(BaseModel):
    title: str
    authors: List[str] = []
    publication_date: datetime
    url: Optional[str] = None
    abstract: Optional[str] = None
    conference: Optional[str] = None
    volume: Optional[str] = None
    keywords: Optional[str] = None

    def to_entity(self) -> PaperOrm:
        entity = PaperOrm(title=self.title,
                          authors=self.authors,
                          abstract=self.abstract,
                          conference=self.conference,
                          volume=self.volume,
                          publication_date=self.publication_date,
                          url=self.url,
                          keywords=self.keywords)
        return entity


class Paper(PaperCreate):
    id: str
    created_at: datetime

    @classmethod
    def from_entity(cls, entity: PaperOrm) -> "Paper":
        return cls(title=entity.title,
                   authors=entity.authors,
                   abstract=entity.abstract,
                   conference=entity.conference,
                   volume=entity.volume,
                   publication_date=entity.publication_date,
                   url=entity.url,
                   keywords=entity.keywords,
                   created_at=entity.created_at,
                   id=entity.id)

    @classmethod
    def from_dict(cls, d: dict) -> "Paper":
        paper = Paper(title=d.get('title'),
                      authors=d.get('authors'),
                      abstract=d.get('abstract'),
                      conference=d.get('conference'),
                      volume=d.get('volume'),
                      publication_date=d.get('publication_date'),
                      url=d.get('url'),
                      keywords=d.get('keywords'),
                      created_at=d.get('created_at'),
                      id=d.get('id'))
        return paper

    def to_entity(self) -> PaperOrm:
        entity = PaperOrm(title=self.title,
                          authors=self.authors,
                          abstract=self.abstract,
                          conference=self.conference,
                          volume=self.volume,
                          publication_date=self.publication_date,
                          url=self.url,
                          keywords=self.keywords,
                          created_at=self.created_at,
                          id=self.id)
        return entity


class PaperChunk(BaseModel):
    paper_id: str
    chunk_index: int
    embedding: List[float]

    @classmethod
    def from_entity(cls, entity: PaperChunkOrm) -> "PaperChunk":
        return cls(paper_id=entity.paper_id,
                   chunk_index=entity.chunk_index,
                   embedding=entity.embedding)

    def to_entity(self) -> PaperChunkOrm:
        entity = PaperChunkOrm(paper_id=self.paper_id,
                               chunk_index=self.chunk_index,
                               embedding=self.embedding)
        return entity


class SearchScorePaper(BaseModel):
    score: float
    paper: Paper
