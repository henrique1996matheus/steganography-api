from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from repositories.analise_repository import analises

from services.relatorio_service import gerar_relatorio_txt
from services.relatorio_service import gerar_relatorio_pdf


router = APIRouter(tags=["Relatórios"])

@router.get("/relatorio/{id_analise}/{formato}")
def relatorio_pdf(id_analise: str, formato: str):

    analise = analises.get(id_analise)

    if analise is None:
        raise HTTPException(404, "Análise não encontrada")
    

    if formato == "txt":
        txt = gerar_relatorio_txt(id_analise, analise)

        return StreamingResponse(
            txt,
            media_type="text/plain; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename=relatorio-{id_analise}.txt"
            }
        )
    
    elif formato == "pdf":
        pdf = gerar_relatorio_pdf(id_analise, analise)

        return StreamingResponse(
            pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=relatorio-{id_analise}.pdf"
            }
        )