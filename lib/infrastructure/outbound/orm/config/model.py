from sqlalchemy import ARRAY, TIMESTAMP, Column, String, Text
from sqlalchemy.orm import declarative_base
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
    pdf = Column(Text, nullable=False)
    url = Column(Text, nullable=True)
    summary = Column(Text)
    keywords = Column(ARRAY(String), default=[])
    embedding = Column(Vector(768))
    created_at = Column(TIMESTAMP, default=datetime.now(timezone.utc))