from pydantic import BaseModel

from enums.status_analise import StatusAnalise
from models.resultado_analise import ResultadoAnalise


class ArquivoAnalise(BaseModel):
    nome: str
    status: StatusAnalise
    resultado: ResultadoAnalise | None = None
    erro: str | None = None