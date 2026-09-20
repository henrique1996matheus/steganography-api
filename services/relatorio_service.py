from io import BytesIO

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    Image,
    Spacer,
)

from services.grafico_service import gerar_grafico_distribuicao

def gerar_relatorio_txt(id_analise: str, analise) -> BytesIO:
    buffer = BytesIO()

    linhas = [
        "RELATÓRIO DE ESTEGANÁLISE",
        "=" * 50,
        f"ID da análise: {id_analise}",
        f"Status: {analise.status}",
        f"Arquivos analisados: {analise.total}",
        "",
    ]

    for arquivo in analise.arquivos:
        linhas.append(f"Arquivo: {arquivo.nome}")
        linhas.append(f"Status: {arquivo.status}")

        if arquivo.resultado:
            linhas.append(
                f"Classificação: {arquivo.resultado.classificacao}"
            )
            linhas.append(
                f"Qui-quadrado: {arquivo.resultado.valor_qui}"
            )

            if arquivo.resultado.mensagem_recuperada:
                linhas.append("Mensagem recuperada: Sim")
                linhas.append(
                    f"CRC: {arquivo.resultado.crc}"
                )
            else:
                linhas.append("Mensagem recuperada: Não")

        if arquivo.erro:
            linhas.append(f"Erro: {arquivo.erro}")

        linhas.append("-" * 50)

    buffer.write("\n".join(linhas).encode("utf-8"))
    buffer.seek(0)

    return buffer

def gerar_relatorio_pdf(id_analise: str, analise) -> BytesIO:
    buffer = BytesIO()

    documento = SimpleDocTemplate(buffer)
    estilos = getSampleStyleSheet()

    elementos = []

    elementos.append(
        Paragraph(
            "<b>RELATÓRIO DE ESTEGANÁLISE</b>",
            estilos["Title"],
        )
    )

    elementos.append(
        Paragraph(f"ID: {id_analise}", estilos["Normal"])
    )

    elementos.append(
        Paragraph(f"Status: {analise.status}", estilos["Normal"])
    )

    elementos.append(
        Paragraph(
            f"Arquivos analisados: {analise.total}",
            estilos["Normal"],
        )
    )

    elementos.append(Spacer(1, 20))

    # ---------------------------
    # TABELA RESUMO
    # ---------------------------

    dados = [["Imagem", "Status"]]

    for arquivo in analise.arquivos:
        dados.append([arquivo.nome, str(arquivo.status)])

    tabela = Table(dados, colWidths=[280, 120])

    tabela.setStyle(
        TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1F4E79")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("BOTTOMPADDING", (0,0), (-1,0), 8),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [
                colors.whitesmoke,
                colors.beige,
            ]),
        ])
    )

    elementos.append(tabela)
    elementos.append(Spacer(1, 20))

    # ---------------------------
    # DETALHES DE CADA IMAGEM
    # ---------------------------

    for arquivo in analise.arquivos:

        elementos.append(
            Paragraph(
                f"<b>{arquivo.nome}</b>",
                estilos["Heading2"],
            )
        )

        elementos.append(
            Paragraph(
                f"Status: {arquivo.status}",
                estilos["Normal"],
            )
        )

        if arquivo.resultado is None:
            elementos.append(
                Paragraph(
                    f"Erro: {arquivo.erro}",
                    estilos["Normal"],
                )
            )

            elementos.append(Spacer(1, 16))
            continue

        r = arquivo.resultado

        elementos.append(
            Paragraph(
                f"Classificação: {r.classificacao}",
                estilos["Normal"],
            )
        )

        elementos.append(
            Paragraph(
                f"Qui-quadrado: {r.valor_qui}",
                estilos["Normal"],
            )
        )

        elementos.append(
            Paragraph(
                f"Limiar: {r.limiar}",
                estilos["Normal"],
            )
        )

        elementos.append(
            Paragraph(
                f"Característica: {r.feature}",
                estilos["Normal"],
            )
        )

        elementos.append(
            Paragraph(
                "Mensagem recuperada: "
                + ("Sim" if r.mensagem_recuperada else "Não"),
                estilos["Normal"],
            )
        )

        if r.mensagem:
            elementos.append(
                Paragraph(
                    f"CRC: {r.crc}",
                    estilos["Normal"],
                )
            )

        # -------- GRÁFICO --------

        grafico = gerar_grafico_distribuicao(
            valor_imagem=r.valor_qui,
            nome_imagem=arquivo.nome,
            classificacao=r.classificacao,
            mensagem_recuperada=r.mensagem_recuperada,
        )

        elementos.append(Image(grafico, width=450, height=270))

        elementos.append(Spacer(1, 24))

    documento.build(elementos)

    buffer.seek(0)

    return buffer
