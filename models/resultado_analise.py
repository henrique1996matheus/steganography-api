from pydantic import BaseModel


class ResultadoAnalise(BaseModel):
    classificacao: str
    deteccao_estatistica: bool
    valor_qui: float
    feature: str
    limiar: float
    direcao: str
    mensagem_recuperada: bool
    mensagem: str | None = None
    crc: str | None = None
    erro_extracao: str | None = None