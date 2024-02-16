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
    altura, largura, _ = imagem.shape
    resultado = int_para_bin(altura) + int_para_bin(largura)

    for i in range(largura):
        for j in range(altura):
            for ch in range(3):
                resultado += int_para_bin(imagem[i, j, ch])
    
    return resultado

class Tipo(Enum):
    IMAGEM = 1
    TEXTO = 2

class LSB:
    def __init__(self, imagem_original: str, imagem_escondida: str, tipo: Tipo=Tipo.IMAGEM) -> None:
        self._imagem_original = imagem_original
        self._imagem_escondida = imagem_escondida
        self._tipo = tipo

    def _converte_dados(self, dados) -> object:
        if self._tipo == Tipo.IMAGEM:
            l = imagem_para_bits(dados)
            return l
        
        return texto_para_bits(dados)

    def _revelar_imagem(self) -> None:
        imagem = cv2.imread(self._imagem_original)

        # Recupera as dimensões da imagem (primeiros dois bytes)
        altura_bin, largura_bin = "", ""
        _, largura_orig, _ = imagem.shape
        ch = 0
        for i in range(16):
            pixel = imagem[0, i, ch]

            bit = str(pixel & 1)
            if i < 8:
                altura_bin += bit
            else:
                largura_bin += bit

            if i % 8 == 0:
                ch += 1


        altura = int(altura_bin,base=2)
        largura = int(largura_bin,base=2)
        x = 16
        y = 0
        bits = ""

        # Mantemos a contagem de ch (canal) para continuar iterando
        for i in range(altura*largura*8*3):
            if x == largura_orig - 1:
                x = 0
                y += 1
            
            if ch == 3:
                ch = 0

            if x < largura_orig - 1:
                pixel = imagem[y, x, ch]
                bits += str(pixel & 1)
                x += 1
            
            if i % 8 == 0:
                ch += 1
        
        # Converte subconjuntos de 8 em 8 bits para bytes e converte para base decimal
        _bytes = [int(bits[i:i+8], base=2) for i in range(0, len(bits), 8)]
        resultado = np.asarray(_bytes).reshape((altura, largura, 3)).astype(np.uint8)

        # Salva imagem
        cv2.imwrite(self._imagem_escondida, resultado)

    def revelar(self):
        if self._tipo == Tipo.IMAGEM:
            self._revelar_imagem()
        else:
            self._revelar_texto()

    def _revelar_texto(self):
        # Carrega a imagem com (potencial) texto escondido
        imagem = cv2.imread(self._imagem_original)
        
        # Armazena a quantidade de caracteres que se deseja recuperar o valor original
        qtde_caracter = trata_entrada("Digite a quantidade de caracteres que deseja recuperar: ", int)

        # Variáveis para denotar qual pixel iremos alterar
        x = 0
        y = 0
        ch = 0
        bits = "" # Armazena os bits recuperados

        altura, largura, _ = imagem.shape
        for i in range(qtde_caracter * 8):
            # Se x for igual a largura da imagem, então passe para a próxima linha
            # e redefina x para 0
            if x == largura - 1:
                y += 1
                x = 0
            
            if x < largura-1:
                if ch == 3:
                    ch = 0

                # Recupera pixel na coluna x, linha y e canal 0
                pixel = imagem[y, x, ch]

                # Recupera bit menos significativo
                bits += str(pixel & 1)

                if i % 8 == 0:
                    ch += 1

                # Incrementa as colunas visitadas
                x += 1

            # Indica que todos os pixeis foram visitados
            if y == altura:
                print("A imagem acabou! Abortando.")
                exit(1)
        
        print(bits)
        print(f"Texto revelado: {converte_bits_texto(bits)}")

    def esconder(self, dados) -> None:
        if self._tipo == Tipo.IMAGEM and not isinstance(dados, np.ndarray):
            print("O tipo dos dados de entrada está incorreto. Forneça uma imagem!")
            exit(1)
        
        # Carregando imagem na memória
        imagem = cv2.imread(self._imagem_original)

        # Obtém dimensões da imagem
        altura, largura, _ = imagem.shape

        # Converte os dados de entrada em uma lista de bits
        bits = self._converte_dados(dados)

        # Variáveis para denotar qual pixel iremos alterar
        x = 0
        y = 0
        ch = 0
        for i in range(len(bits)):
            # Recupera bit da lista de bits e converte em inteiro
            bit = int(bits[i])

            # Se x for igual a largura da imagem, então passe para a próxima linha
            # e redefina x para 0
            if x == largura-1:
                y += 1
                x = 0

            if x < largura-1:

                if ch == 3:
                    ch = 0

                if bit == 1:
                    # Adicione um bit no pixel na coluna x, linha y e canal 0
                    imagem[y, x, ch] = imagem[y, x, ch] | 1
                else:
                    # Remova um bit no pixel na coluna x, linha y e canal 0
                    imagem[y, x, ch] = imagem[y, x, ch] & 0xFFFFFFFE

                if i % 8 == 0:
                    ch += 1

                x += 1
            
            # Indica que todos os pixeis foram visitados
            if y == altura - 1:
                print("A imagem acabou! Abortando.")
                exit(1)

        print(f"Mensagem escondida: {dados} ({bits})")
        cv2.imwrite(self._imagem_escondida, imagem)