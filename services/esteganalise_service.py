import json
from pathlib import Path

import numpy as np
from models.arquivo_upload import ArquivoUpload

from core.esteg_dct import (
    COEFICIENTES,
    DELTA,
    dct_blocos,
    extrair_mensagem,
    imagem_para_array,
)

from models.resultado_analise import ResultadoAnalise

# Caminho da configuração do detector.
BASE = Path(__file__).resolve().parent.parent
CONFIGURACAO = BASE / "config" / "detector_qui_quadrado.json"


# ============================================================
# SERVIÇO PRINCIPAL DE ESTEGANÁLISE
# ============================================================

async def analisar_imagem(arquivo: ArquivoUpload) -> ResultadoAnalise:
    imagem = imagem_para_array(arquivo.conteudo)

    """
    Analisa uma única imagem enviada para a API.

    Retorna todas as informações necessárias para:
    - endpoint de progresso;
    - relatório TXT;
    - relatório PDF.
    """

    # Carrega a configuração do detector.
    with open(CONFIGURACAO, "r", encoding="utf-8") as arquivo_config:
        configuracao = json.load(arquivo_config)

    feature = configuracao["feature"]
    limiar = float(configuracao["limiar"])
    direcao = configuracao["direcao_stego"]

    # Calcula o teste estatístico.
    valor_qui = extrair_valor_qui_quadrado(imagem, feature)

    indicio_estatistico = classificar(
        valor_qui,
        limiar,
        direcao,
    )

    # Tenta recuperar uma mensagem STG1.
    mensagem = None
    crc = None
    erro_extracao = None

    try:
        mensagem, crc = extrair_mensagem(imagem)
    except Exception as erro:
        erro_extracao = str(erro)

    mensagem_recuperada = mensagem is not None

    # Classificação final.
    if mensagem_recuperada:
        classificacao = (
            "MENSAGEM DCT-QIM RECONHECIDA E RECUPERADA"
        )

    elif indicio_estatistico:
        classificacao = (
            "POSSÍVEIS INDÍCIOS DE ESTEGANOGRAFIA"
        )

    else:
        classificacao = (
            "SEM INDÍCIOS RELEVANTES DE ESTEGANOGRAFIA"
        )

    return ResultadoAnalise(
        nome=arquivo.nome,
        classificacao=classificacao,
        deteccao_estatistica=indicio_estatistico,
        valor_qui=round(valor_qui, 4),
        feature=feature,
        limiar=limiar,
        direcao=direcao,
        mensagem_recuperada=mensagem_recuperada,
        mensagem=mensagem,
        crc=formatar_crc(crc) if crc is not None else None,
        erro_extracao=erro_extracao,
    )


# ============================================================
# TESTE DE QUI-QUADRADO
# ============================================================

def calcular_qui_quadrado(valores: np.ndarray) -> float:
    valores = np.asarray(valores, dtype=np.int64)

    if valores.size == 0:
        return 0.0

    unicos, frequencias = np.unique(
        valores,
        return_counts=True,
    )

    contagens = dict(
        zip(unicos.tolist(), frequencias.tolist())
    )

    bases = np.unique(2 * (unicos // 2))

    estatistica = 0.0

    for base in bases:

        quantidade_par = contagens.get(int(base), 0)
        quantidade_impar = contagens.get(int(base + 1), 0)

        total = quantidade_par + quantidade_impar

        if total == 0:
            continue

        esperado = total / 2.0

        estatistica += (
            ((quantidade_par - esperado) ** 2) / esperado
            + ((quantidade_impar - esperado) ** 2) / esperado
        )

    return float(estatistica)


def extrair_valor_qui_quadrado(
    imagem: np.ndarray,
    feature: str,
) -> float:
    """
    Calcula a característica utilizada pelo detector de
    esteganografia (qui-quadrado sobre coeficientes DCT).
    """

    blocos = dct_blocos(imagem - 128.0)

    u = [coef[0] for coef in COEFICIENTES]
    v = [coef[1] for coef in COEFICIENTES]

    coeficientes = blocos[:, :, u, v].reshape(-1)

    quantizados = np.rint(
        coeficientes / DELTA
    ).astype(np.int64)

    proporcoes = {
        "chi2_25": 0.25,
        "chi2_50": 0.50,
        "chi2_100": 1.00,
    }

    if feature not in proporcoes:
        raise ValueError(
            f"Característica desconhecida: {feature}"
        )

    quantidade = int(
        len(quantizados) * proporcoes[feature]
    )

    return calcular_qui_quadrado(
        quantizados[:quantidade]
    )


# ============================================================
# CLASSIFICAÇÃO
# ============================================================

def classificar(
    valor: float,
    limiar: float,
    direcao: str,
) -> bool:
    """
    Verifica se o valor calculado indica uma imagem STEGO
    de acordo com a configuração do detector.
    """

    if direcao == "menor":
        return valor <= limiar

    return valor >= limiar


# ============================================================
# UTILITÁRIOS
# ============================================================

def formatar_crc(crc) -> str:
    if isinstance(crc, (int, np.integer)):
        return f"{int(crc):08X}"

    return str(crc)