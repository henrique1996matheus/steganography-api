import asyncio
import traceback

from fastapi import UploadFile
from models.arquivo_upload import ArquivoUpload

from enums.status_analise import StatusAnalise
from repositories.analise_repository import analise_repository
from services.esteganalise_service import analisar_imagem


async def processar_imagens(id_analise: str, arquivos_upload: list[ArquivoUpload]):
    analise = analise_repository.buscar(id_analise)

    if analise is None:
        return

    try:
        for index, arquivo_upload in enumerate(arquivos_upload):
            arquivo = analise.arquivos[index]

            try:
                arquivo.status = StatusAnalise.PROCESSANDO

                print(f"{id_analise} - {arquivo.nome}")

                resultado = await analisar_imagem(arquivo_upload)

                arquivo.resultado = resultado
                arquivo.status = StatusAnalise.CONCLUIDO

            except Exception as e:
                traceback.print_exc()  # imprime a stack completa no terminal

                arquivo.status = StatusAnalise.ERRO
                arquivo.erro = str(e)

            finally:
                analise.concluidas += 1

        tem_erros = any(
            arquivo.status == StatusAnalise.ERRO
            for arquivo in analise.arquivos
        )

        analise.status = (
            StatusAnalise.ERRO
            if tem_erros
            else StatusAnalise.CONCLUIDO
        )

    except Exception as e:
        traceback.print_exc()  # imprime a stack completa no terminal

        arquivo.status = StatusAnalise.ERRO
        arquivo.erro = str(e)