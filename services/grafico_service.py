from io import BytesIO
import json
from pathlib import Path

import matplotlib

# Backend para geração de imagens em memória (sem interface gráfica)
matplotlib.use("Agg")

import matplotlib.pyplot as plt

import numpy as np

BASE = Path(__file__).resolve().parent.parent
REFERENCIA = BASE / "config" / "distribuicao_referencia.json"


def gerar_grafico_distribuicao(
    valor_imagem: float,
    nome_imagem: str,
    classificacao: str,
    mensagem_recuperada: bool,
) -> BytesIO:
    """
    Gera o gráfico da análise e devolve um BytesIO (PNG em memória).
    """

    with open(REFERENCIA, "r", encoding="utf-8") as arquivo:
        referencia = json.load(arquivo)

    cover = np.asarray(referencia["cover"], dtype=float)
    stego = np.asarray(referencia["stego"], dtype=float)

    feature = referencia["feature"]
    limiar = float(referencia["limiar"])
    direcao = referencia["direcao_stego"]

    todos = np.concatenate([cover, stego])

    minimo = float(np.percentile(todos, 0.5))
    maximo = float(np.percentile(todos, 99.5))

    minimo = min(minimo, valor_imagem, limiar)
    maximo = max(maximo, valor_imagem, limiar)

    margem = max((maximo - minimo) * 0.05, 1.0)
    minimo -= margem
    maximo += margem

    fig, ax = plt.subplots(figsize=(10, 6))

    if direcao == "menor":
        ax.axvspan(minimo, limiar, color="crimson", alpha=0.07)
        ax.axvspan(limiar, maximo, color="royalblue", alpha=0.07)
    else:
        ax.axvspan(minimo, limiar, color="royalblue", alpha=0.07)
        ax.axvspan(limiar, maximo, color="crimson", alpha=0.07)

    intervalo = (minimo, maximo)

    ax.hist(
        cover,
        bins=55,
        range=intervalo,
        density=False,
        alpha=0.5,
        color="royalblue",
        edgecolor="white",
        linewidth=0.3,
        label=f"COVER ({len(cover)})",
    )

    ax.hist(
        stego,
        bins=55,
        range=intervalo,
        density=False,
        alpha=0.5,
        color="crimson",
        edgecolor="white",
        linewidth=0.3,
        label=f"STEGO ({len(stego)})",
    )

    ax.axvline(
        limiar,
        color="black",
        linestyle="--",
        linewidth=2,
        label=f"Limiar: {limiar:.2f}",
    )

    ax.axvline(
        valor_imagem,
        color="darkgreen",
        linewidth=3,
        label=f"Imagem: {valor_imagem:.2f}",
    )

    ax.set_xlim(minimo, maximo)
    ax.set_xlabel("Valor da estatística qui-quadrado")
    ax.set_ylabel("Quantidade de imagens do conjunto de treinamento")
    ax.set_title("Distribuição de imagens do conjunto de treinamento (COVER x STEGO)")
    ax.grid(axis="y", alpha=0.2, linestyle=":")
    ax.legend(fontsize=9)

    plt.tight_layout()

    buffer = BytesIO()

    plt.savefig(
        buffer,
        format="png",
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    buffer.seek(0)

    return buffer