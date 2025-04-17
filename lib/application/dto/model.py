from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from lib.domain.model import Paper, PaperChunk, PaperMetadata, SearchScorePaper


class PaperCreateDto(BaseModel):
    title: str
    authors: List[str] = []
    publication_date: datetime
    url: Optional[str] = None
    abstract: Optional[str] = None
    conference: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[str] = None


class PaperMetadataDto(PaperCreateDto):
    pdf: str

    def to_entity(self) -> PaperMetadata:
        entity = PaperMetadata(title=self.title,
                               authors=self.authors,
                               publication_date=self.publication_date,
                               abstract=self.abstract,
                               conference=self.conference,
                               pdf=self.pdf,
                               url=self.url,
                               summary=self.summary,
                               keywords=self.keywords)
        return entity


class PaperDto(PaperMetadataDto):
    id: Optional[str]

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


class PaperChunkCreateDto(BaseModel):
    paper_id: str
    chunk_index: int
    embedding: List[float]

    def to_entity(self) -> Paper:
        entity = PaperChunk(chunk_index=self.chunk_index,
                            paper_id=self.paper_id,
                            embedding=self.embedding)
        return entity


class PaperChunkDto(PaperChunkCreateDto):
    id: str

    @classmethod
    def from_entity(cls, entity: Paper) -> "PaperChunkDto":
        return cls(chunk_index=entity.chunk_index,
                   paper_id=entity.paper_id,
                   embedding=entity.embedding,
                   id=entity.id)

    def to_entity(self) -> Paper:
        entity = PaperChunk(chunk_index=self.chunk_index,
                            paper_id=self.paper_id,
                            embedding=self.embedding,
                            id=self.id)
        return entity


class SearchScorePaperDto(BaseModel):
    score: float
    paper: PaperDto

    @classmethod
    def from_entity(cls, entity: SearchScorePaper) -> "SearchScorePaperDto":
        return cls(score=entity.score, paper=PaperDto.from_entity(entity.paper))
