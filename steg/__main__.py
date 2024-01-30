from argparse import ArgumentParser
from .stego import revelar, esconder

PARSER = ArgumentParser("steg")
PARSER.add_argument("-i", dest="imagem_entrada", help="Caminho para a imagem original", type=str, required=True)
PARSER.add_argument("-o", dest="imagem_saida", help="Caminho para a imagem com texto escondido", type=str)
PARSER.add_argument("-f", dest="funcao", choices=["esconder", "revelar"], help="Ação que deseja realizar", required=True)

ARGS = PARSER.parse_args()

if ARGS.funcao == "esconder":
    esconder(ARGS.imagem_entrada, ARGS.imagem_saida)
elif ARGS.funcao == "revelar":
    revelar(ARGS.imagem_entrada)