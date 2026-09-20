from models.analise import Analise


class AnaliseRepository:

    def __init__(self):
        self._analises: dict[str, Analise] = {}

    def salvar(self, analise: Analise) -> None:
        self._analises[analise.id] = analise

    def buscar(self, id_analise: str) -> Analise | None:
        return self._analises.get(id_analise)

    def listar(self) -> list[Analise]:
        return list(self._analises.values())

    def quantidade(self) -> int:
        return len(self._analises)

    def tamanho_memoria(self) -> int:
        import sys
        return sys.getsizeof(self._analises)

    def remover(self, id_analise: str) -> bool:
        if id_analise in self._analises:
            del self._analises[id_analise]
            return True

        return False

    def existe(self, id_analise: str) -> bool:
        return id_analise in self._analises


analise_repository = AnaliseRepository()