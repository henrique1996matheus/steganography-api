import asyncio
import uuid
import sys

from fastapi import HTTPException, UploadFile

from enums.status_analise import StatusAnalise
from repositories.analise_repository import analises
from services.processamento_service import processar_imagens

def listar_analises():
    return {
        "bytes": sys.getsizeof(analises),
        "tamanho": len(analises)
    }

async def iniciar_analise(files: list[UploadFile]):

    if len(files) > 15:
        raise HTTPException(
            status_code=422,
            detail="Não é possível enviar mais que 15 arquivos"
        )

    id_analise = str(uuid.uuid4())

    analises[id_analise] = {
        "total": len(files),
        "concluidas": 0,
        "status": StatusAnalise.PROCESSANDO,
        "arquivos": [
            {
                "nome": file.filename,
                "status": StatusAnalise.AGUARDANDO
            }
            for file in files
        ]
    }

    asyncio.create_task(
        processar_imagens(id_analise, files)
    )

    return {"id_analise": id_analise}

def consultar_progresso(id_analise: str):

    analise = analises.get(id_analise)

    if analise is None:
        raise HTTPException(
            status_code=404,
            detail="Análise não encontrada"
        )

    porcentagem = int(
        (analise["concluidas"] / analise["total"]) * 100
    )

    return {
        "total": analise["total"],
        "concluidas": analise["concluidas"],
        "progresso": porcentagem,
        "status": analise["status"],
        "arquivos": analise["arquivos"]
    }