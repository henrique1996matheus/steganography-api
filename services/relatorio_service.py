from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from services.grafico_service import gerar_grafico_distribuicao


# ============================================================
# RELATÓRIO TXT
# ============================================================

def gerar_relatorio_txt(id_analise: str, analise) -> BytesIO:
    buffer = BytesIO()

    linhas = [
        "RELATÓRIO DE ESTEGANÁLISE",
        "=" * 60,
        f"ID da análise: {id_analise}",
        f"Status geral: {analise.status}",
        f"Arquivos analisados: {analise.total}",
        "",
    ]

    for arquivo in analise.arquivos:

        linhas.append("-" * 60)
        linhas.append(f"Arquivo: {arquivo.nome}")
        linhas.append(f"Status: {arquivo.status}")

        if arquivo.resultado is not None:
            resultado = arquivo.resultado

            linhas.append(f"Característica utilizada: {resultado.feature}")
            linhas.append(f"Qui-quadrado calculado: {resultado.valor_qui}")
            linhas.append(f"Limiar do detector: {resultado.limiar}")
            linhas.append(f"Classificação: {resultado.classificacao}")

            linhas.append(
                "Detecção estatística: "
                + (
                    "Positiva para STEGO"
                    if resultado.deteccao_estatistica
                    else "Negativa para STEGO"
                )
            )

            linhas.append(
                "Mensagem recuperada: "
                + ("Sim" if resultado.mensagem_recuperada else "Não")
            )

            if resultado.mensagem_recuperada:
                linhas.append(f"CRC: {resultado.crc}")

                if resultado.mensagem:
                    linhas.append("")
                    linhas.append("Mensagem recuperada:")
                    linhas.append(resultado.mensagem)

            elif resultado.erro_extracao:
                linhas.append(f"Detalhe da extração: {resultado.erro_extracao}")

        if arquivo.erro:
            linhas.append(f"Erro durante a análise: {arquivo.erro}")

        linhas.append("")

    buffer.write("\n".join(linhas).encode("utf-8"))
    buffer.seek(0)

    return buffer


# ============================================================
# RELATÓRIO PDF
# ============================================================

def gerar_relatorio_pdf(analise) -> BytesIO:

    buffer = BytesIO()

    documento = SimpleDocTemplate(buffer)

    estilos = getSampleStyleSheet()

    titulo_secao = ParagraphStyle(
        name="TituloSecao",
        parent=estilos["Heading2"],
        alignment=1,
        fontSize=14,
        leading=18,
        spaceAfter=10,
        textColor=colors.HexColor("#1F4E79"),
    )

    # Estilo da mensagem extraída
    estilo_codigo = ParagraphStyle(
        name="Mensagem",
        parent=estilos["Code"],
        fontSize=9,
        leading=12,
        backColor=colors.HexColor("#F4F4F4"),
        borderPadding=(8, 8, 8, 8),
    )

    elementos = []

    # ========================================================
    # UMA PÁGINA POR ARQUIVO
    # ========================================================

    for indice, arquivo in enumerate(analise.arquivos):

        # Nova página a partir do segundo arquivo.
        if indice > 0:
            elementos.append(PageBreak())

        resultado = arquivo.resultado

        # ----------------------------------------------------
        # INFORMAÇÕES GERAIS
        # ----------------------------------------------------

        elementos.append(
            Paragraph("INFORMAÇÕES GERAIS", titulo_secao)
        )

        elementos.append(
            Paragraph(
                f"<b>Arquivo analisado:</b> {arquivo.nome}",
                estilos["Normal"],
            )
        )

        # Caso tenha ocorrido erro durante a análise.
        if resultado is None:

            elementos.append(Spacer(1, 10))

            elementos.append(
                Paragraph(
                    f"<b>Erro durante a análise:</b> {arquivo.erro}",
                    estilos["Normal"],
                )
            )

            continue

        # ----------------------------------------------------
        # CARACTERÍSTICAS DA ANÁLISE
        # ----------------------------------------------------

        elementos.append(Spacer(1, 16))

        elementos.append(
            Paragraph(
                f"<b>Característica utilizada:</b> {resultado.feature}",
                estilos["Normal"],
            )
        )

        elementos.append(
            Paragraph(
                f"<b>Valor da estatística qui-quadrado:</b> {resultado.valor_qui}",
                estilos["Normal"],
            )
        )

        elementos.append(
            Paragraph(
                f"<b>Limiar do detector:</b> {resultado.limiar}",
                estilos["Normal"],
            )
        )

        elementos.append(
            Paragraph(
                f"<b>Direção STEGO:</b> {resultado.direcao}",
                estilos["Normal"],
            )
        )

        # ----------------------------------------------------
        # RESULTADO DA DETECÇÃO
        # ----------------------------------------------------

        elementos.append(Spacer(1, 20))

        elementos.append(
            Paragraph("RESULTADO DA DETECÇÃO", titulo_secao)
        )

        elementos.append(
            Paragraph(
                f"<b>Classificação final:</b> {resultado.classificacao}",
                estilos["Normal"],
            )
        )

        elementos.append(
            Paragraph(
                "<b>Detecção estatística:</b> "
                + (
                    "Positiva para STEGO"
                    if resultado.deteccao_estatistica
                    else "Negativa para STEGO"
                ),
                estilos["Normal"],
            )
        )

        elementos.append(
            Paragraph(
                "<b>Mensagem recuperada:</b> "
                + (
                    "Sim"
                    if resultado.mensagem_recuperada
                    else "Não"
                ),
                estilos["Normal"],
            )
        )

        if resultado.mensagem_recuperada:

            elementos.append(
                Paragraph(
                    f"<b>CRC válido:</b> {resultado.crc}",
                    estilos["Normal"],
                )
            )

            if resultado.mensagem:

                elementos.append(Spacer(1, 10))

                elementos.append(
                    Paragraph(
                        "<b>Mensagem extraída:</b>",
                        estilos["Heading3"],
                    )
                )

                elementos.append(Spacer(1, 6))

                elementos.append(
                    Paragraph(
                        resultado.mensagem.replace("\n", "<br/>"),
                        estilo_codigo,
                    )
                )

        elif resultado.erro_extracao:

            elementos.append(
                Paragraph(
                    f"<b>Detalhe da extração:</b> {resultado.erro_extracao}",
                    estilos["Normal"],
                )
            )

        # ----------------------------------------------------
        # GRÁFICO DA DISTRIBUIÇÃO
        # ----------------------------------------------------

        elementos.append(Spacer(1, 20))

        elementos.append(
            Paragraph(
                "DISTRIBUIÇÃO ESTATÍSTICA E POSICIONAMENTO",
                titulo_secao,
            )
        )

        grafico = gerar_grafico_distribuicao(
            valor_imagem=resultado.valor_qui,
            nome_imagem=arquivo.nome,
            classificacao=resultado.classificacao,
            mensagem_recuperada=resultado.mensagem_recuperada,
        )

        elementos.append(
            Image(
                grafico,
                width=450,
                height=270,
            )
        )

    # ========================================================
    # GERA O PDF
    # ========================================================

    documento.build(elementos)

    buffer.seek(0)

    return buffer