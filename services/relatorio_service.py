from io import BytesIO

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle
)

from reportlab.lib import colors


def gerar_relatorio_txt(id_analise: str, analise: dict) -> BytesIO:
    buffer = BytesIO()

    linhas = [
        "RELATÓRIO DE ESTEGANÁLISE",
        "=" * 40,
        f"ID da análise: {id_analise}",
        f"Status: {analise['status']}",
        f"Arquivos analisados: {analise['total']}",
        "",
        "Arquivos:"
    ]

    for arquivo in analise["arquivos"]:
        linhas.append(
            f"- {arquivo['nome']} : {arquivo['status']}"
        )

    buffer.write("\n".join(linhas).encode("utf-8"))
    buffer.seek(0)

    return buffer


def gerar_relatorio_pdf(id_analise: str, analise: dict) -> BytesIO:
    buffer = BytesIO()

    documento = SimpleDocTemplate(buffer)
    estilos = getSampleStyleSheet()

    elementos = []

    elementos.append(Paragraph(
        "<b>RELATÓRIO DE ESTEGANÁLISE</b>",
        estilos["Title"]
    ))

    elementos.append(Paragraph(
        f"ID da análise: {id_analise}",
        estilos["Normal"]
    ))

    elementos.append(Paragraph(
        f"Status: {analise['status']}",
        estilos["Normal"]
    ))

    elementos.append(Paragraph(
        f"Arquivos analisados: {analise['total']}",
        estilos["Normal"]
    ))

    elementos.append(Paragraph("<br/>", estilos["Normal"]))

    # ---------- TABELA ----------
    dados_tabela = [["Imagem", "Status"]]

    for arquivo in analise["arquivos"]:
        dados_tabela.append([
            arquivo["nome"],
            arquivo["status"]
        ])

    tabela = Table(dados_tabela, colWidths=[260, 120])

    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1F4E79")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BOTTOMPADDING", (0,0), (-1,0), 8),
        ("TOPPADDING", (0,1), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [
            colors.whitesmoke,
            colors.beige
        ]),
    ]))

    elementos.append(tabela)

    documento.build(elementos)

    buffer.seek(0)
    return buffer

