from enum import Enum

import cv2
import numpy as np

RESIZE_WIDTH = 50
RESIZE_HEIGHT = 50

def int_para_bin(n: int) -> str:
    # int para binario
    return f"{n:0{8}b}"

def texto_para_bits(texto: str) -> str:
    # char para unicode 
    texto = [ord(i) for i in texto]

    # int para binario
    return "".join(f"{i:0{8}b}" for i in texto)

def converte_bits_texto(bits: str) -> str:
    # Separa conjunto de bits
    bits_separado = [bits[i:i+8] for i in range(0, len(bits), 8)]

    # Converte conjunto de bits para texto
    return "".join(chr(int(c, base=2)) for c in bits_separado)

def trata_entrada(prompt: str, tipo: type):
    if tipo == str:
        return input(prompt)

    if tipo == int:
        dados = input(prompt)

        if not all(i.isdigit() for i in dados):
            print("Só é permitido entrada de números de 0 a 9. Abortando.")
            exit(1)

        return int(dados)

def binario_para_int(n: str) -> int:
    return int(n, base=2)

def imagem_para_bits(imagem: np.ndarray) -> str:
    # Os dois primeiros bytes serão utilizados para representar as dimensões da imagem
    # de saída. Portanto, o tamanho máximo de uma imagem para ser escondida será de 
    # 255x255.

    imagem = cv2.resize(imagem, (RESIZE_WIDTH, RESIZE_HEIGHT), interpolation = cv2.INTER_AREA)

    altura, largura, _ = imagem.shape
    resultado = ""
    for ch in range(3):
        for j in range(altura):
            for i in range(largura):
                resultado += int_para_bin(imagem[j, i, ch])
    
    return resultado

def _verifica_tamanho_correto(imagem: np.ndarray) -> bool:
    altura, largura, _ = imagem.shape
    
    return not (altura > 255 or largura > 255)

def _verifica_qtde_bits(imagem: np.ndarray, bits: list) -> bool:
    """ Função para verificar se a imagem original possui tamanho suficiente para esconder uma cadeia de bits """
    altura, largura, canais = imagem.shape

    return (altura * largura * canais * 8) > len(bits)

class Tipo(Enum):
    IMAGEM = 1
    TEXTO = 2

class LSB:
    def __init__(self, imagem_original: str, imagem_escondida: str, tipo: Tipo=Tipo.IMAGEM, api=True) -> None:
        self._imagem_original = imagem_original
        self._imagem_escondida = imagem_escondida
        self._tipo = tipo
        self._api = api

    def _converte_dados(self, dados) -> object:
        if self._tipo == Tipo.IMAGEM:
            return imagem_para_bits(dados)
        
        return texto_para_bits(dados)
    
    def _extrai_dimensoes(self, imagem) -> tuple:
        return imagem[0, 0, 0].astype(np.uint8), imagem[0, 1, 0].astype(np.uint8)

    def _revelar_imagem(self, *args) -> None:
        imagem = cv2.imread(self._imagem_original)

        bits = ""
        x = 2 # Inicia com 3, pois assume-se que os dois primeiros bytes são as dimensões
        y = 0
        ch = 0
        altura, largura = self._extrai_dimensoes(imagem)
        altura_orig, largura_orig, _ = imagem.shape
        res = np.zeros((altura, largura, 3))
        n_bytes = 0
        bytes = []

        # Mantemos a contagem de ch (canal) para continuar iterando
        for i in range(int(altura) * int(largura) * 8 * 3):
            if x == largura_orig:
                x = 0
                y += 1

            if y == altura_orig:
                y = 0
                x = 0
                ch += 1

            if x < largura_orig:
                pixel = imagem[y, x, ch]
                bits += str(pixel & 1)
                x += 1
            
            n_bytes += 1

            if n_bytes == 8:
                bytes += [int(bits, base=2)]
                bits = ""
                n_bytes = 0

        c = 0
        for ch in range(3):
            for j in range(largura):
                for i in range(altura):
                    res[j, i, ch] = bytes[c]
                    c += 1

        # Salva imagem
        cv2.imwrite(self._imagem_escondida, res)

    def revelar(self, *args):
        if self._tipo == Tipo.IMAGEM:
            return self._revelar_imagem(*args)
        else:
            return self._revelar_texto(*args)

    def _revelar_texto(self, qtde_caracter: int):
        # Carrega a imagem com (potencial) texto escondido
        imagem = cv2.imread(self._imagem_original)
        
        # Variáveis para denotar qual pixel iremos alterar
        x = 0
        y = 0
        ch = 0
        bits = "" # Armazena os bits recuperados

        altura, largura, _ = imagem.shape
        for _ in range(qtde_caracter * 8):
            # Se x for igual a largura da imagem, então passe para a próxima linha
            # e redefina x para 0
            if x == largura:
                y += 1
                x = 0

            if y == altura:
                y = 0
                x = 0
                ch += 1
            
            if x < largura:

                # Recupera pixel na coluna x, linha y e canal ch
                pixel = imagem[y, x, ch]

                # Recupera bit menos significativo
                bits += str(pixel & 1)

                # Incrementa as colunas visitadas
                x += 1

            # Indica que todos os pixeis foram visitados
            if y == altura and ch == 3 and x == largura:
                print("A imagem acabou! Abortando.")
                exit(1)
        
        print(f"Texto revelado: {converte_bits_texto(bits)}")
        if self._api:
            return converte_bits_texto(bits)

    def esconder(self, dados) -> None:
        if self._tipo == Tipo.IMAGEM and not isinstance(dados, np.ndarray):
            print("O tipo dos dados de entrada está incorreto. Forneça uma imagem!")
            exit(1)
        
        # Carregando imagem na memória
        imagem = cv2.imread(self._imagem_original)

        # Removendo canal alpha
        imagem = cv2.cvtColor(imagem, cv2.COLOR_RGBA2RGB)

        # Obtém dimensões da imagem
        altura, largura, _ = imagem.shape

        # Converte os dados de entrada em uma lista de bits
        bits = self._converte_dados(dados)

        if not _verifica_qtde_bits(imagem, bits):
            print(f"O tamanho da imagem original ({altura * largura * 3 * 8:,} bits) não é o suficiente para esconder {len(bits):,} bits.")
            exit(1)

        # Variáveis para denotar qual pixel iremos alterar
        x = 0
        y = 0
        ch = 0
        total_bits_hidden = 0

        # 2 primeiros bytes são o tamanho da imagem escondida
        if self._tipo == Tipo.IMAGEM:
            imagem[y, 0, ch] = RESIZE_WIDTH
            imagem[y, 1, ch] = RESIZE_HEIGHT
            x = 2

        for bit in bits:
            # Recupera bit da lista de bits e converte em inteiro
            bit = int(bit)

            # Se x for igual a largura da imagem, então passe para a próxima linha
            # e redefina x para 0

            if x == largura:
                x = 0
                y += 1

            if y == altura:
                y = 0
                x = 0
                ch += 1

            # Indica que todos os pixeis foram visitados
            if ch == 3:
                print("A imagem acabou! Abortando.")
                exit(1)

            if x < largura:
                if bit == 1:
                    # Adicione um bit no pixel na coluna x, linha y e canal 0
                    imagem[y, x, ch] |= 0b00000001
                else:
                    # Remova um bit no pixel na coluna x, linha y e canal 0
                    imagem[y, x, ch] &= 0b11111110

                x += 1
            
            total_bits_hidden += 1
            

        if self._tipo == Tipo.IMAGEM:
            print("Imagem escondida com sucesso")
        else:
            print(f"Mensagem escondida: {dados} ({bits})")
        
        print(f"Total de bits escondidos: {total_bits_hidden:,}")
        cv2.imwrite(self._imagem_escondida, imagem)

        return imagem
