from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session


from lib.application.ports.outbound.paper_repository import PaperRepository
from lib.domain.model import Paper, PaperChunk, PaperCreate, SearchScorePaper
from .config.model import Paper as PaperOrm, PaperChunk as PaperChunkOrm


class SQLAlchemyPaperRepository(PaperRepository):
    def __init__(self, session: Session, top_k: int = 10, similarity_type: str = 'cosine'):
        self.top_k = top_k
        self.similarity_type = similarity_type
        self.db = session

    def create(self, paper: PaperCreate) -> Paper:
        entity = paper.to_entity()
        self.db.add(entity)
        try:
            self.db.commit()
            self.db.refresh(entity)
        except Exception as e:
            self.db.rollback()
            raise e
        return Paper.from_entity(entity)

    def get_by_id(self, paper_id: str) -> Optional[Paper]:
        entity = self.db.query(PaperOrm).filter(
            PaperOrm.id == paper_id).first()
        if entity:
            return Paper.from_entity(entity)

    def update(self, paper_id: str, paper: Paper) -> Optional[Paper]:
        entity = self.db.query(Paper).filter(Paper.id == paper_id).first()

        if not entity:
            return None

        # Update fields
        entity.title = paper.title
        # Convert list to comma-separated string
        entity.authors = ', '.join(paper.authors)
        entity.abstract = paper.abstract
        entity.conference = paper.conference
        entity.summary = paper.summary
        entity.keywords = ', '.join(paper.keywords) if paper.keywords else None
        entity.year = paper.year
        entity.url = paper.url

        # Commit changes
        self.db.commit()
        self.db.refresh(entity)  # Refresh to get the updated paper
        return Paper.from_entity(entity)

    def add_embedding(self, embedding: PaperChunk) -> Optional[PaperChunk]:
        entity = embedding.to_entity()
        self.db.add(entity)
        try:
            self.db.commit()
            self.db.refresh(entity)
        except Exception as e:
            self.db.rollback()
            raise e
        return PaperChunk.from_entity(entity)

    def clean_embeddings(self, paper_id: str) -> bool:
        entities = self.db.query(PaperChunkOrm).filter(
            PaperChunkOrm.paper_id == paper_id)
        try:
            for entity in entities:
                self.db.delete(entity)
                self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
        return True

    def similarity_search(self, embedding: List[float]) -> List[SearchScorePaper]:
        if self.similarity_type == 'cosine':
            sql_query = """
                    SELECT pc.*,p.*,
                    pc.embedding::vector <=> ('[' || ARRAY_TO_STRING(:query_vector, ',') || ']')::vector AS similarity_score
                    FROM paper_chunks pc
                    JOIN papers p ON pc.paper_id = p.id
                    ORDER BY similarity_score ASC 
                    LIMIT :limit;     
            """
        elif self.similarity_type == 'euclidean':
            sql_query = """
                    SELECT pc.*,p.*,
                    pc.embedding::vector <#> ('[' || ARRAY_TO_STRING(:query_vector, ',') || ']')::vector AS similarity_score
                    FROM paper_chunks pc
                    JOIN papers p ON pc.paper_id = p.id
                    ORDER BY similarity_score ASC 
                    LIMIT :limit;     
            """
        elif self.similarity_type == 'inner_product':
            sql_query = """
                    SELECT pc.*,p.*,
                    pc.embedding::vector @> ('[' || ARRAY_TO_STRING(:query_vector, ',') || ']')::vector AS similarity_score
                    FROM paper_chunks pc
                    JOIN papers p ON pc.paper_id = p.id
                    ORDER BY similarity_score DESC 
                    LIMIT :limit;     
            """
        else:
            raise ValueError("Unsupported similarity type")

        result = self.db.execute(
            text(sql_query),
            {"query_vector": embedding, "limit": 10*self.top_k}
        )

        rows = result.fetchall()
        ids = []
        results = []

        for row in rows:
            paper = Paper.from_dict(row._mapping)
            if not paper.id in ids:
                results += [SearchScorePaper(paper=paper,
                                             score=row._mapping["similarity_score"])]
            if len(results) >= self.top_k:
                break
        return results

    def text_search(self, query: str):
        sql = text("""
            SELECT *,
              ts_rank_cd(
                to_tsvector('english', coalesce(title, '') || ' ' || coalesce(abstract, '') || ' ' || coalesce(keywords, '')),
                plainto_tsquery('english', :query)
              ) AS score 
            FROM papers
            WHERE to_tsvector('english', coalesce(title, '') || ' ' || coalesce(abstract, '') || ' ' || coalesce(keywords, ''))
              @@ plainto_tsquery('english', :query)
            ORDER BY score DESC
            LIMIT :top_k;
        """)

        result = self.db.execute(sql, {"query": query, "top_k": self.top_k})
        rows = result.fetchall()

        return [SearchScorePaper(paper=Paper.from_dict(row._mapping),
                                 score=row._mapping["score"])
                for row in rows]

    def delete(self, paper_id: int) -> bool:
        entity = self.db.query(PaperOrm).filter(Paper.id == paper_id).first()
        if not entity:
            return False
        try:
            self.db.delete(entity)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
        return True
