from io import BytesIO
import struct
import zlib

import numpy as np
from PIL import Image
from scipy.fft import dct, idct

# ============================================================
# CONFIGURAÇÕES DO ALGORITMO DCT-QIM
# ============================================================

# Mesmas posições utilizadas no experimento.
COEFICIENTES = [
    (2, 3),
    (3, 2),
    (3, 3),
    (2, 4),
]

# Distância entre níveis de quantização.
DELTA = 32

# Cada bit é gravado várias vezes e recuperado por maioria.
REPETICOES = 9

# Cabeçalho da mensagem.
MAGIC = b"STG1"


# ============================================================
# UTILITÁRIOS DE IMAGEM
# ============================================================

def imagem_para_array(imagem_bytes: bytes) -> np.ndarray:
    """
    Converte os bytes de uma imagem recebida pela API para um
    array NumPy em escala de cinza.
    """

    imagem = Image.open(BytesIO(imagem_bytes)).convert("L")

    imagem = np.asarray(
        imagem,
        dtype=np.float64,
    )

    if imagem.shape != (512, 512):
        raise ValueError(
            f"A imagem possui tamanho {imagem.shape}. "
            "O analisador espera uma imagem 512x512."
        )

    return imagem


def array_para_bytes(imagem: np.ndarray, formato: str = "PNG") -> BytesIO:
    """
    Converte um array NumPy para BytesIO.
    Útil caso futuramente a API precise devolver a imagem STEGO.
    """

    buffer = BytesIO()

    Image.fromarray(imagem.astype(np.uint8)).save(
        buffer,
        format=formato,
    )

    buffer.seek(0)

    return buffer


# ============================================================
# DCT / IDCT
# ============================================================

def dct_blocos(imagem: np.ndarray) -> np.ndarray:
    h, w = imagem.shape

    blocos = imagem.reshape(
        h // 8,
        8,
        w // 8,
        8,
    ).transpose(0, 2, 1, 3)

    return dct(
        dct(blocos, axis=2, norm="ortho"),
        axis=3,
        norm="ortho",
    )


def idct_blocos(blocos: np.ndarray) -> np.ndarray:
    pixels = idct(
        idct(blocos, axis=3, norm="ortho"),
        axis=2,
        norm="ortho",
    )

    h = blocos.shape[0] * 8
    w = blocos.shape[1] * 8

    return pixels.transpose(
        0,
        2,
        1,
        3,
    ).reshape(h, w)


# ============================================================
# PAYLOAD (STG1 + TAMANHO + CRC)
# ============================================================

def criar_payload(texto: str) -> bytes:
    dados = texto.encode("utf-8")

    tamanho = struct.pack(">I", len(dados))
    crc = struct.pack(">I", zlib.crc32(dados))

    return MAGIC + tamanho + dados + crc


def payload_para_bits(payload: bytes) -> np.ndarray:
    vetor = np.frombuffer(payload, dtype=np.uint8)

    return np.unpackbits(vetor).astype(np.uint8)


def bits_para_bytes(bits: np.ndarray) -> bytes:
    return np.packbits(
        np.asarray(bits, dtype=np.uint8)
    ).tobytes()


# ============================================================
# POSIÇÕES DOS COEFICIENTES
# ============================================================

def listar_posicoes(blocos: np.ndarray) -> list[tuple]:
    posicoes = []

    for i in range(blocos.shape[0]):
        for j in range(blocos.shape[1]):
            for u, v in COEFICIENTES:
                posicoes.append((i, j, u, v))

    return posicoes


# ============================================================
# QIM
# ============================================================

def forcar_bit_qim(coeficiente: float, bit: int) -> float:
    """
    Quantiza o coeficiente em múltiplos de DELTA e força
    a paridade do índice quantizado.
    """

    indice_central = int(np.rint(coeficiente / DELTA))

    candidatos = [
        indice
        for indice in range(
            indice_central - 2,
            indice_central + 3,
        )
        if abs(indice) % 2 == bit
    ]

    melhor = min(
        candidatos,
        key=lambda indice: abs(
            coeficiente - indice * DELTA
        ),
    )

    return float(melhor * DELTA)


def ler_bit_qim(coeficiente: float) -> int:
    indice = int(np.rint(coeficiente / DELTA))

    return abs(indice) % 2


# ============================================================
# INSERÇÃO DE MENSAGEM
# ============================================================

def inserir_mensagem(
    imagem: np.ndarray,
    texto: str,
):
    """
    Recebe uma imagem em memória e devolve:

    - imagem STEGO (numpy.ndarray)
    - informações da inserção
    """

    if imagem.shape != (512, 512):
        raise ValueError(
            f"A imagem deve ser 512x512, mas possui {imagem.shape}."
        )

    blocos = dct_blocos(imagem - 128.0)

    posicoes = listar_posicoes(blocos)

    payload = criar_payload(texto)
    bits = payload_para_bits(payload)

    bits_repetidos = np.repeat(bits, REPETICOES)

    capacidade_bits = len(posicoes) // REPETICOES
    capacidade_bytes = capacidade_bits // 8

    if len(bits) > capacidade_bits:
        raise ValueError(
            "Mensagem grande demais.\n"
            f"Necessário: {len(payload)} bytes\n"
            f"Capacidade aproximada: {capacidade_bytes} bytes"
        )

    for indice, bit in enumerate(bits_repetidos):
        i, j, u, v = posicoes[indice]

        blocos[i, j, u, v] = forcar_bit_qim(
            blocos[i, j, u, v],
            int(bit),
        )

    stego = idct_blocos(blocos) + 128.0

    stego = np.clip(
        np.rint(stego),
        0,
        255,
    ).astype(np.uint8)

    informacoes = {
        "payload_bytes": len(payload),
        "mensagem_bytes": len(texto.encode("utf-8")),
        "bits_originais": len(bits),
        "bits_gravados": len(bits_repetidos),
        "capacidade_bytes": capacidade_bytes,
    }

    return stego, informacoes


# ============================================================
# EXTRAÇÃO DE MENSAGEM
# ============================================================

def recuperar_bits(blocos: np.ndarray) -> np.ndarray:
    posicoes = listar_posicoes(blocos)

    bits_lidos = []

    quantidade_grupos = len(posicoes) // REPETICOES

    for grupo in range(quantidade_grupos):

        inicio = grupo * REPETICOES

        votos = []

        for deslocamento in range(REPETICOES):

            i, j, u, v = posicoes[inicio + deslocamento]

            votos.append(
                ler_bit_qim(blocos[i, j, u, v])
            )

        bit_final = 1 if sum(votos) >= (REPETICOES // 2 + 1) else 0

        bits_lidos.append(bit_final)

    return np.asarray(bits_lidos, dtype=np.uint8)


def extrair_mensagem(imagem: np.ndarray):
    """
    Extrai uma mensagem STG1 de uma imagem em memória.

    Retorna:
        texto, crc
    """

    blocos = dct_blocos(imagem - 128.0)

    bits = recuperar_bits(blocos)

    cabecalho_bits = 8 * 8

    cabecalho = bits_para_bytes(
        bits[:cabecalho_bits]
    )

    magic = cabecalho[:4]

    if magic != MAGIC:
        raise ValueError(
            f"Cabeçalho inválido: {magic!r}. "
            "A mensagem não foi reconhecida."
        )

    tamanho = struct.unpack(
        ">I",
        cabecalho[4:8],
    )[0]

    total_bytes = 4 + 4 + tamanho + 4
    total_bits = total_bytes * 8

    if total_bits > len(bits):
        raise ValueError(
            "O tamanho declarado ultrapassa a capacidade da imagem."
        )

    payload = bits_para_bytes(bits[:total_bits])

    dados = payload[8:8 + tamanho]

    crc_salvo = struct.unpack(
        ">I",
        payload[8 + tamanho:12 + tamanho],
    )[0]

    crc_calculado = zlib.crc32(dados)

    if crc_salvo != crc_calculado:
        raise ValueError(
            "CRC inválido: a mensagem foi corrompida."
        )

    texto = dados.decode("utf-8")

    return texto, crc_salvo


# ============================================================
# MÉTRICAS
# ============================================================

def calcular_psnr(
    cover: np.ndarray,
    stego: np.ndarray,
) -> float:
    """
    Calcula o PSNR entre duas imagens em memória.
    """

    mse = np.mean((cover - stego) ** 2)

    if mse == 0:
        return float("inf")

    return 10 * np.log10((255 ** 2) / mse)