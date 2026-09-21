import asyncio
import uuid
import sys

from fastapi import HTTPException, UploadFile

from enums.status_analise import StatusAnalise
from repositories.analise_repository import analise_repository
from services.processamento_service import processar_imagens

from models.analise import Analise
from models.arquivo_analise import ArquivoAnalise
from models.arquivo_upload import ArquivoUpload
from pathlib import Path

EXTENSOES_PERMITIDAS = {".jpg", ".jpeg"}
CONTENT_TYPES_PERMITIDOS = {
    "image/jpeg",
    "image/jpg",
}

def listar_analises():
    return {
        "bytes": analise_repository.tamanho_memoria(),
        "tamanho": analise_repository.quantidade(),
        "analises": analise_repository.listar()
    }

def validar_arquivo(file: UploadFile):
    extensao = Path(file.filename).suffix.lower()

    if extensao not in EXTENSOES_PERMITIDAS:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Arquivo '{file.filename}' possui formato inválido. "
                "Apenas imagens JPEG (.jpg e .jpeg) são permitidas."
            ),
        )

    if file.content_type not in CONTENT_TYPES_PERMITIDOS:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Arquivo '{file.filename}' não é uma imagem JPEG válida "
                f"(content-type: {file.content_type})."
            ),
        )

async def iniciar_analise(files: list[UploadFile]):

    if len(files) > 14:
        raise HTTPException(
            status_code=422,
            detail="Não é possível enviar mais que 14 arquivos"
        )

    id_analise = str(uuid.uuid4())

    arquivos_upload = []

    analise = Analise(
        id=id_analise,
        total=len(files),
        concluidas=0,
        status=StatusAnalise.PROCESSANDO,
        arquivos=[]
    )

    for file in files:
        # validar_arquivo(file)

        conteudo = await file.read()

        analise.arquivos.append(
            ArquivoAnalise(
                nome=file.filename,
                status=StatusAnalise.AGUARDANDO
            )
        )

        arquivos_upload.append(
            ArquivoUpload(
                nome=file.filename,
                content_type=file.content_type,
                conteudo=conteudo
            )
        )

    analise_repository.salvar(analise)

    asyncio.create_task(
        processar_imagens(id_analise, arquivos_upload)
    )

    return {"id_analise": id_analise}

def consultar_progresso(id_analise: str):

    analise = analise_repository.buscar(id_analise)

    if analise is None:
        raise HTTPException(404, "Análise não encontrada")

    porcentagem = int(
        analise.concluidas / analise.total * 100
    )

    return {
        "total": analise.total,
        "concluidas": analise.concluidas,
        "progresso": porcentagem,
        "status": analise.status,
        "arquivos": analise.arquivos,
    }