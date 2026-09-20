from pydantic import BaseModel

class ArquivoUpload(BaseModel):
    nome: str
    content_type: str | None = None
    conteudo: bytes