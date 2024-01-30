import cv2
import numpy as np

def converte_texto_bits(texto: str) -> str:
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
        

def esconde(imagem_original: str, imagem_com_texto: str):
    imagem = cv2.imread(imagem_original)
    print("Texto para esconder: ")
    texto = trata_entrada(">>> ", str)

    altura, largura, _ = imagem.shape
    bits = converte_texto_bits(texto)

    x = 0
    y = 0
    for i in range(len(bits)):
        bit = int(bits[i])

        if x < largura:
            if bit == 1:
                imagem[x, y, :] = imagem[x, y, :] | 1
            else:
                imagem[x, y, :] = imagem[x, y, :] & 0xFFFFFFFE
            
        if x == largura - 1:
            y += 1
            x = 0
        
        if y == altura:
            print("A imagem acabou! Abortando.")
            exit(1)

        x += 1
    print(f"Mensagem escondida: {texto} ({bits})")
    cv2.imwrite(imagem_com_texto, imagem)

def revelar(imagem_com_texto: str):
    imagem = cv2.imread(imagem_com_texto)
    qtde_caracter = trata_entrada(">>> ", int)

    x = 0
    y = 0
    bits = ""
    _, largura, _ = imagem.shape
    for _ in range(qtde_caracter * 8):
        if x < largura:
            pixel = imagem[x, y, 0]
            bits += str(pixel & 1)

        if x == largura - 1:
            y += 1
            x = 0

        x += 1
    
    print(f"Texto revelado: {converte_bits_texto(bits)}")
    
esconde()
revelar()