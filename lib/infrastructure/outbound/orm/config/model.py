from sqlalchemy import ARRAY, TIMESTAMP, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime, timezone
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class Paper(Base):
    __tablename__ = "papers"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(Text, nullable=False)
    authors = Column(ARRAY(String), default=[])
    abstract = Column(Text)
    conference = Column(String)
    publication_date = Column(TIMESTAMP, nullable=False)
    url = Column(Text, nullable=True)
    keywords = Column(String, default=[])
    created_at = Column(TIMESTAMP, default=datetime.now(timezone.utc))

    chunks = relationship(
        "PaperChunk", back_populates="paper", cascade="all, delete-orphan")


class PaperChunk(Base):
    __tablename__ = "paper_chunks"

    id = Column(Integer, primary_key=True)
    chunk_index = Column(Integer, nullable=False)  # e.g. 0, 1, 2, ...
    embedding = Column(Vector(384), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now(timezone.utc))
    paper_id = Column(String, ForeignKey("papers.id"), nullable=False) 
    paper = relationship("Paper", back_populates="chunks")
