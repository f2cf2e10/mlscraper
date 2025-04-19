import logging
from typing import List, Literal
from fastapi import APIRouter, File, HTTPException, Depends, Request, Response, UploadFile
from app.container import conferences, Container
from lib.application.dto.model import PaperChunkDto, PaperCreateDto, PaperDto
from lib.application.ports.inbound.embedding_usecase import EmbeddingUseCase
from lib.application.ports.inbound.paper_crud_usecase import PaperCrudUseCase

router = APIRouter()
container = Container()

logger = logging.getLogger("uvicorn")


@router.post("/paper", response_model=PaperDto)
async def add(paper: PaperCreateDto,
              paper_service: PaperCrudUseCase = Depends(
                  lambda: container.paper_service())) -> PaperDto:
    try:
        entity = paper_service.add(paper)
        return entity
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper/{paper_id}", response_model=PaperDto)
async def get(paper_id: str,
              paper_service: PaperCrudUseCase = Depends(
                  lambda: container.paper_service())) -> PaperDto:
    try:
        entity = paper_service.get_by_id(paper_id)
        return entity
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper/{paper_id}/upload", response_model=PaperDto)
async def add_file(paper_id: str,
                   file: UploadFile = File(...),
                   paper_service: PaperCrudUseCase = Depends(
                       lambda: container.paper_service())) -> PaperDto:
    try:
        entity = paper_service.get_by_id(paper_id)
        if not entity:
            raise HTTPException(
                status_code=404, detail=f"Paper {paper_id} not found.")
        content = await file.read()
        saved = paper_service.upload(entity.id, content)
        if saved:
            return entity
        return entity
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper/{paper_id}/download", response_model=PaperDto)
async def get_file(paper_id: str,
                   paper_service: PaperCrudUseCase = Depends(
                       lambda: container.paper_service())) -> Response:
    try:
        file = paper_service.download(f"{paper_id}.pdf")

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
    suffix = ".pdf"
    payload = await request.json()
    records = payload.get("Records", [])

    for record in records:
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        logger.info(f"New file uploaded: bucket={bucket}, key={key}")
        paper_id = key[len(prefix):] if key.startswith(prefix) else key
        paper_id = paper_id[:-len(suffix)
                            ] if paper_id.endswith(suffix) else paper_id
        paper = paper_service.get_by_id(paper_id)
        # COMMENTED: Not doing the whole file, this is too large, instead do the abstract only
        # file = paper_service.download(key)
        # embeddings = embedding_service.get_embeddings(file)
        if not paper:
            raise HTTPException(
                status_code=404, detail=f"Paper {paper_id} not found.")
        embeddings = embedding_service.embeddings(paper.abstract)
        _ = paper_service.clean_embeddings(paper_id)
        for i, embedding in enumerate(embeddings):
            _ = paper_service.add_embedding(PaperChunkDto(
                paper_id=paper_id,
                chunk_index=i,
                embedding=embedding))
        logger.info(f"File processed: bucket={bucket}, key={key}")

    return Response("ok", status_code=200)
