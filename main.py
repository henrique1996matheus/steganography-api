from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.analise_router import router as analise_router
from routers.relatorio_router import router as relatorio_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analise_router)
app.include_router(relatorio_router)