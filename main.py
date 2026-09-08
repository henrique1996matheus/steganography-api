from fastapi import FastAPI

from routers.analise_router import router as analise_router
from routers.relatorio_router import router as relatorio_router

app = FastAPI()

app.include_router(analise_router)
app.include_router(relatorio_router)