from enum import Enum


class StatusAnalise(str, Enum):
    AGUARDANDO = "aguardando"
    PROCESSANDO = "processando"
    CONCLUIDO = "concluido"
    ERRO = "erro"