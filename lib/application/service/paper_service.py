from lib.application.ports.inbound.paper_crud_usecase import PaperCrudUseCase
from lib.application.ports.inbound.paper_store_usecase import PaperStoreUseCase
from lib.application.ports.outbound.paper_repository import PaperRepository
from lib.application.ports.outbound.paper_storage import PaperStorage


class PaperService(PaperCrudUseCase, PaperStoreUseCase):
    def __init__(self, paper_repo: PaperRepository, paper_store: PaperStorage):
        self.paper_repo = paper_repo
        self.paper_store = paper_store

    
