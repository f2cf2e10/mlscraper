from fastapi import FastAPI
from lib.infrastructure.inbound import paper_web_api


app = FastAPI()
app.include_router(paper_web_api.router)
