from fastapi import APIRouter, UploadFile, File

from services.analise_service import (
    iniciar_analise,
    consultar_progresso,
    listar_analises
)

router = APIRouter(tags=["Análises"])


@router.get("/listar-analises")
def listar():
    return listar_analises()


@router.post("/analisar-imagens")
async def analisar(files: list[UploadFile] = File(...)):
    return await iniciar_analise(files)


@router.get("/analisar/{id_analise}/progresso")
def progresso(id_analise: str):
    return consultar_progresso(id_analise)