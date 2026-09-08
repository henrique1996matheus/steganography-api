import asyncio

from fastapi import UploadFile

from enums.status_analise import StatusAnalise
from repositories.analise_repository import analises

async def processar_imagens(
    id_analise: str,
    files: list[UploadFile]
):

    analise = analises[id_analise]

    try:

        for index, file in enumerate(files):

            try:
                analise["arquivos"][index]["status"] = StatusAnalise.PROCESSANDO

                print(
                    f"{id_analise} - {file.filename}"
                )

                await asyncio.sleep(10)

                analise["arquivos"][index]["status"] = StatusAnalise.CONCLUIDO

            except Exception as e:

                analise["arquivos"][index]["status"] = StatusAnalise.ERRO
                analise["arquivos"][index]["erro"] = str(e)

            finally:
                analise["concluidas"] += 1

        tem_erros = any(
            arquivo["status"] == StatusAnalise.ERRO
            for arquivo in analise["arquivos"]
        )

        analise["status"] = (
            StatusAnalise.ERRO
            if tem_erros
            else StatusAnalise.CONCLUIDO
        )

    except Exception as e:
        analise["status"] = StatusAnalise.ERRO
        analise["erro"] = str(e)