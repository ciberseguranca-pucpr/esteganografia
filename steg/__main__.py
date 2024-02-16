from argparse import ArgumentParser
from .stego import LSB, Tipo
from pathlib import Path

import cv2

def _caminho_existe(caminho) -> bool:
    caminho = Path(caminho)
    return caminho.exists()

PARSER = ArgumentParser("steg")
PARSER.add_argument("-i", dest="imagem_entrada", help="Caminho para a imagem original", type=str, required=True)
PARSER.add_argument("-o", dest="imagem_saida", help="Caminho para a imagem com texto escondido", type=str)
PARSER.add_argument("-f", dest="funcao", choices=["esconder", "revelar"], help="Ação que deseja realizar", required=True)
PARSER.add_argument("-t", dest="eh_texto", action='store_true', default=False, help="Flag que especifica se deseja esconder um texto ou imagem")

ARGS = PARSER.parse_args()
lsb = LSB(ARGS.imagem_entrada, ARGS.imagem_saida, tipo=Tipo.TEXTO if ARGS.eh_texto else Tipo.IMAGEM)

if ARGS.funcao == "esconder":
    if ARGS.eh_texto:
        texto = input("Digite o texto que deseja esconder: ")
        lsb.esconder(texto)
    else:
        caminho_img = input("Digite o caminho da imagem que deseja esconder: ")

        if not _caminho_existe(caminho_img):
            print(f"O caminho que você especificou ({caminho_img}) é inválido.")
            exit(1)

        img = cv2.imread(caminho_img)
        lsb.esconder(img)

elif ARGS.funcao == "revelar":
    lsb.revelar()