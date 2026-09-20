from pydantic import BaseModel

from enums.status_analise import StatusAnalise
from models.arquivo_analise import ArquivoAnalise


class Analise(BaseModel):
    id: str
    total: int
    concluidas: int
    status: StatusAnalise
    arquivos: list[ArquivoAnalise]
    erro: str | None = None