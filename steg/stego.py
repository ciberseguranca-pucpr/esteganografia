from enum import Enum

import cv2
import numpy as np

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

    if not _verifica_tamanho_correto(imagem):
        altura, largura, _ = imagem.shape
        print(f"Redimensionando imagem para 255x255 (antes: {altura}x{largura})")
        imagem = cv2.resize(imagem, (255, 255), interpolation = cv2.INTER_AREA)

    altura, largura, _ = imagem.shape
    resultado = int_para_bin(altura) + int_para_bin(largura)

    for ch in range(3):
        for j in range(altura):
            for i in range(largura):
                resultado += int_para_bin(imagem[i, j, ch])
    
    return resultado

def _verifica_tamanho_correto(imagem: np.ndarray) -> bool:
    altura, largura, _ = imagem.shape
    
    return not (altura > 255 or largura > 255)

def _verifica_qtde_bits(imagem: np.ndarray, bits: list) -> bool:
    """ Função para verificar se a imagem original possui tamanho suficiente para esconder uma cadeia de bits """
    altura, largura, canais = imagem.shape

    return altura * largura * canais * 8 > len(bits)

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
            l = imagem_para_bits(dados)
            return l
        
        return texto_para_bits(dados)

    def _revelar_imagem(self, *args) -> None:
        imagem = cv2.imread(self._imagem_original)

        # Recupera as dimensões da imagem (primeiros dois bytes)
        altura_bin, largura_bin = "", ""
        altura_orig, largura_orig, _ = imagem.shape

        ch = 0
        x  = 0
        y  = 0
        for i in range(16):
            pixel = imagem[0, i, ch]

            bit = str(pixel & 1)
            if i < 8:
                altura_bin += bit
            else:
                largura_bin += bit
            x += 1

        altura = int(altura_bin,base=2)
        largura = int(largura_bin,base=2)
        bits = ""

        # Mantemos a contagem de ch (canal) para continuar iterando
        for i in range(altura*largura*8*3):
            if y == altura_orig - 1 and x == largura_orig - 1:
                ch += 1

            if x == largura_orig - 1:
                x = 0
                y += 1
            
            if y == altura_orig - 1:
                y = 0

            if x < largura_orig - 1:
                pixel = imagem[y, x, ch]
                bits += str(pixel & 1)
                x += 1
        
        # Converte subconjuntos de 8 em 8 bits para bytes e converte para base decimal
        _bytes = [int(bits[i:i+8], base=2) for i in range(0, len(bits), 8)]
        resultado = np.asarray(_bytes).reshape((altura, largura, 3)).astype(np.uint8)

        # Salva imagem
        cv2.imwrite(self._imagem_escondida, resultado)

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
            if y == altura - 1 and x == largura - 1:
                ch += 1

            # Se x for igual a largura da imagem, então passe para a próxima linha
            # e redefina x para 0
            if x == largura - 1:
                y += 1
                x = 0

            if y == altura - 1:
                y = 0
                ch += 1
            
            if x < largura-1:

                # Recupera pixel na coluna x, linha y e canal 0
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
        for i in range(len(bits)):
            # Recupera bit da lista de bits e converte em inteiro
            bit = int(bits[i])

            if y == altura - 1 and x == largura - 1:
                ch += 1
            
            # Se x for igual a largura da imagem, então passe para a próxima linha
            # e redefina x para 0
            if x == largura-1:
                y += 1
                x = 0

            if y == altura - 1:
                y = 0

            if x < largura-1:

                if bit == 1:
                    # Adicione um bit no pixel na coluna x, linha y e canal 0
                    imagem[y, x, ch] = imagem[y, x, ch] | 1
                else:
                    # Remova um bit no pixel na coluna x, linha y e canal 0
                    if imagem[y,x,ch] > 0:
                        imagem[y, x, ch] = imagem[y, x, ch] & 0xFFFFFFFE
                    else:
                        imagem[y, x, ch] = imagem[y, x, ch] | 1

                x += 1
            
            total_bits_hidden += 1
            
            # Indica que todos os pixeis foram visitados
            if y == altura - 1 and ch == 3 and x == largura - 1:
                print("A imagem acabou! Abortando.")
                exit(1)

        if self._tipo == Tipo.IMAGEM:
            print("Imagem escondida com sucesso")
        else:
            print(f"Mensagem escondida: {dados} ({bits})")
        
        print(f"Total de bits escondidos: {total_bits_hidden:,}")
        cv2.imwrite(self._imagem_escondida, imagem)
