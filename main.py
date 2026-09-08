import asyncio
import uuid
import sys

from fastapi import FastAPI, UploadFile, File, HTTPException
from enums.status_analise import StatusAnalise

app = FastAPI()

analises = {}


@app.get("/analises")
def analises():
    return {
        "bytes": sys.getsizeof(analises),
        "tamanho": len(analises)
    }


@app.post("/analisar-imagens")
async def analisar_imagens(files: list[UploadFile] = File(...)):

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

    return {
        "id_analise": id_analise
    }


@app.get("/analisar/{id_analise}/progresso")
def progresso(id_analise: str):

    analise = analises.get(id_analise)

    if analise is None:
        raise HTTPException(
            status_code=404,
            detail="Análise não encontrada"
        )

    total = analise["total"]
    concluidas = analise["concluidas"]

    porcentagem = int((concluidas / total) * 100)

    return {
        "total": total,
        "concluidas": concluidas,
        "progresso": porcentagem,
        "status": analise["status"],
        "arquivos": analise["arquivos"]
    }


async def processar_imagens(
    id_analise: str,
    files: list[UploadFile]
):
    try:
        analise = analises[id_analise]

        for index, file in enumerate(files):
            try:

                analise["arquivos"][index]["status"] = StatusAnalise.PROCESSANDO

                print(
                    f"{id_analise} - index {index} - arquivo {file.filename}"
                )

                # Futuramente:
                # resultado = analisar_dct(file)

                await asyncio.sleep(10)

                if index == 1:
                    raise Exception()

                analise["arquivos"][index]["status"] = StatusAnalise.CONCLUIDO
                analise["concluidas"] += 1
            except Exception as e:
                analise["arquivos"][index]["status"] = StatusAnalise.ERRO
                analise["concluidas"] += 1

        analise["status"] = StatusAnalise.CONCLUIDO

    except Exception as e:
        analise["status"] = StatusAnalise.ERRO
        analise["erro"] = str(e)
