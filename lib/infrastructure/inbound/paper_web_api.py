import mimetypes
from typing import List
from fastapi import APIRouter, File, HTTPException, Depends, Request, Response, UploadFile
from app.container import Container
from lib.application.dto.model import PaperCreateDto, PaperDto
from lib.application.ports.inbound.embedding_usecase import EmbeddingUseCase
from lib.application.ports.inbound.paper_crud_usecase import PaperCrudUseCase
from lib.application.ports.inbound.paper_store_usecase import PaperStoreUseCase

router = APIRouter()
container = Container()


@router.post("/paper", response_model=PaperDto)
async def add(paper: PaperCreateDto,
              file: UploadFile = File(...),
              paper_service: PaperCrudUseCase = Depends(lambda: container.paper_service())) -> PaperDto:
    try:
        entity = paper_service.add(paper)
        saved = paper_service.upload(paper.id, file)
        if saved:
            return entity
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper/{paper_id}", response_model=PaperDto)
async def get(paper_id: str,
              paper_service: PaperCrudUseCase = Depends(lambda: container.paper_service())) -> PaperDto:
    try:
        entity = paper_service.get_by_id(paper_id)
        return entity
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper/{paper_id}/download", response_model=PaperDto)
async def get_file(paper_id: str,
                   paper_service: PaperStoreUseCase = Depends(lambda: container.paper_service())) -> Response:
    try:
        file = paper_service.download(paper_id)

        # Return as a streamed response
        return Response(
            content=file,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{paper_id}.pdf"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper/process", response_model=List[float])
async def process_file(request: Request,
                       paper_service: PaperCrudUseCase = Depends(
                           lambda: container.paper_service()),
                       embedding_service: EmbeddingUseCase = Depends(
                           lambda: container.embedding_service())) -> Response:
    prefix = "papers/"
    payload = await request.json()
    records = payload.get("Records", [])

    for record in records:
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        file = paper_service.download(key)
        paper_id = key[len(prefix):] if key.startswith(prefix) else key
        embeddings = embedding_service.get_embeddings(file)
        for i, embedding in enumerate(embeddings):
            _ = paper_service.add_embeddings(paper_id, embedding, i)
        print(f"New file uploaded: bucket={bucket}, key={key}")

    return Response({"status": "ok"}, status_code=200)
