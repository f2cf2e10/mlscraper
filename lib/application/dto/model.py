from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from lib.domain.model import Paper, PaperChunk, PaperCreate, SearchScorePaper


class PaperCreateDto(BaseModel):
    title: str
    authors: List[str] = []
    publication_date: datetime
    url: Optional[str] = None
    abstract: Optional[str] = None
    conference: Optional[str] = None
    volume: Optional[str] = None
    keywords: Optional[str] = None

    def to_entity(self) -> PaperCreate:
        entity = PaperCreate(title=self.title,
                             authors=self.authors,
                             publication_date=self.publication_date,
                             abstract=self.abstract,
                             conference=self.conference,
                             volume=self.volume,
                             url=self.url,
                             keywords=self.keywords)
        return entity


class PaperDto(PaperCreateDto):
    id: Optional[str]

    @classmethod
    def from_entity(cls, entity: Paper) -> "PaperDto":
        return cls(title=entity.title,
                   authors=entity.authors,
                   abstract=entity.abstract,
                   conference=entity.conference,
                   volume=entity.volume,
                   publication_date=entity.publication_date,
                   url=entity.url,
                   keywords=entity.keywords,
                   id=entity.id)

    def to_entity(self) -> Paper:
        entity = Paper(title=self.title,
                       authors=self.authors,
                       abstract=self.abstract,
                       conference=self.conference,
                       volume=self.volume,
                       publication_date=self.publication_date,
                       url=self.url,
                       keywords=self.keywords,
                       id=self.id)
        return entity


class PaperChunkDto(BaseModel):
    paper_id: str
    chunk_index: int
    embedding: List[float]

    @classmethod
    def from_entity(cls, entity: PaperChunk) -> "PaperChunkDto":
        return cls(chunk_index=entity.chunk_index,
                   paper_id=entity.paper_id,
                   embedding=entity.embedding)

    def to_entity(self) -> PaperChunk:
        entity = PaperChunk(chunk_index=self.chunk_index,
                            paper_id=self.paper_id,
                            embedding=self.embedding)
        return entity


class SearchScorePaperDto(BaseModel):
    score: float
    paper: PaperDto

    @classmethod
    def from_entity(cls, entity: SearchScorePaper) -> "SearchScorePaperDto":
        return cls(score=entity.score, paper=PaperDto.from_entity(entity.paper))
