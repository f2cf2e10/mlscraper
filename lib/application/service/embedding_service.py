from typing import IO, List
import fitz
import textwrap
from lib.application.ports.inbound.embedding_usecase import EmbeddingUseCase
from sentence_transformers import SentenceTransformer


class EmbeddingService(EmbeddingUseCase):

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", chunck_max_chars: int = 1000, number_of_pages: int = 1):
        self.model_name = model_name
        self.max_chars = chunck_max_chars
        self.model = SentenceTransformer(self.model_name)
        self.number_of_pages = number_of_pages

    def extract_text_from_pdf(self, pdf_stream: IO[bytes]) -> str:
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        full_text = ""
        for i, page in enumerate(doc):
            if i >= self.number_of_pages:
                break
            full_text += page.get_text()
        return full_text.strip()

    def split_text(self, text: str) -> List[str]:
        paragraphs = text.split("\n")
        chunks = []
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            wrapped = textwrap.wrap(
                para, self.max_chars, break_long_words=False)
            chunks.extend(wrapped)
        return chunks

    def embeddings(self, text: str) -> List[List[float]]:
        chunks = self.split_text(text)
        embeddings = self.model.encode(chunks)
        return ([e.tolist() for e in embeddings])

    def get_embeddings(self, pdf_file: IO[bytes]) -> List[List[float]]:
        text = self.extract_text_from_pdf(pdf_file)
        return self.embeddings(text)
