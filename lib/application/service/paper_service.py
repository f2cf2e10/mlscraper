from typing import IO, List
from lib.application.dto.model import PaperChunkCreateDto, PaperChunkDto, PaperCreateDto, PaperDto, SearchScorePaperDto
from lib.application.ports.inbound.embedding_usecase import EmbeddingUseCase
from lib.application.ports.inbound.paper_crud_usecase import PaperCrudUseCase
from lib.application.ports.inbound.paper_store_usecase import PaperStoreUseCase
from lib.application.ports.outbound.paper_repository import PaperRepository
from lib.application.ports.outbound.paper_storage import PaperStorage


class PaperService(PaperCrudUseCase, PaperStoreUseCase):
    def __init__(self, paper_repo: PaperRepository, paper_store: PaperStorage, embedding_service: EmbeddingUseCase):
        self.paper_repo = paper_repo
        self.paper_store = paper_store
        self.embedding_service = embedding_service

    def add(self, metadata: PaperCreateDto) -> PaperDto:
        entity = metadata.to_entity()
        saved_entity = self.paper_repo.create(entity)
        return PaperDto.from_entity(saved_entity)

    def get_by_id(self, paper_id: str) -> PaperDto:
        entity = self.paper_repo.get_by_id(paper_id)
        return PaperDto.from_entity(entity)

    def search(self, query: str) -> List[SearchScorePaperDto]:
        entities = self.paper_repo.text_search(query)
        return [SearchScorePaperDto.from_entity(e.paper) for e in entities]

    def find_similar(self, text: str) -> List[SearchScorePaperDto]:
        text_embeddings = self.embedding_service.embeddings(text)
        # TODO: what if there are many embedding chuncks?
        entities = self.paper_repo.similarity_search(text_embeddings[0])
        return [SearchScorePaperDto.from_entity(e.paper) for e in entities]

    def add_embedding(self, chunk=PaperChunkCreateDto) -> PaperChunkDto:
        entity = chunk.to_entity()
        saved_entity = self.paper_repo.add_embedding(entity)
        return PaperChunkDto.from_entity(saved_entity)

    def upload(self, key: str, file: IO[bytes]) -> bool:
        return self.paper_store.upload_file(key, file)

    def download(self, key: str) -> IO[bytes]:
        return self.paper_store.get_file(key)
