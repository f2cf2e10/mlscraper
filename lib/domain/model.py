from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from lib.infrastructure.outbound.orm.config.model import Paper as PaperOrm, PaperChunk as PaperChunkOrm


class PaperMetadata(BaseModel):
    title: str
    authors: List[str] = []
    publication_date: datetime
    url: Optional[str] = None
    abstract: Optional[str] = None
    conference: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[str] = None


class PaperCreate(PaperMetadata):
    pdf: str

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
                   created_at=entity.created_at,
                   id=entity.id)

    @classmethod
    def from_dict(cls, d: dict) -> "Paper":
        return Paper(**{k: v for k, v in d.items() if hasattr(Paper, k)})

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

    def to_entity(self) -> PaperOrm:
        entity = PaperOrm(paper_id=self.paper_id,
                          chunk_index=self.chunk_index,
                          embedding=self.embedding)
        return entity


class SearchScorePaper(BaseModel):
    score: float
    paper: Paper
