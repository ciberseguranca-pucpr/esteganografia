import cv2

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
        

def esconder(imagem_original: str, imagem_com_texto: str):
    # Carregando imagem na memória
    imagem = cv2.imread(imagem_original)

    # Obtém dimensões da imagem
    altura, largura, _ = imagem.shape

    # Armazena entrada do usuário
    texto = trata_entrada("Digite o texto que deseja esconder: ", str)

    # Converte o texto recebido em uma lista de bits
    bits = converte_texto_bits(texto)

    # Variáveis para denotar qual pixel iremos alterar
    x = 0
    y = 0
    for i in range(len(bits)):
        # Recupera bit da lista de bits e converte em inteiro
        bit = int(bits[i])

        if x < largura:
            if bit == 1:
                # Adicione um bit no pixel na coluna x, linha y e canal 0
                imagem[x, y, 0] = imagem[x, y, 0] | 1
            else:
                # Remova um bit no pixel na coluna x, linha y e canal 0
                imagem[x, y, 0] = imagem[x, y, 0] & 0xFFFFFFFE
        
        # Se x for igual a largura da imagem, então passe para a próxima linha
        # e redefina x para 0
        if x == largura - 1:
            y += 1
            x = 0
        
        # Indica que todos os pixeis foram visitados
        if y == altura:
            print("A imagem acabou! Abortando.")
            exit(1)

        # Incrementa as colunas visitadas
        x += 1
    print(f"Mensagem escondida: {texto} ({bits})")
    cv2.imwrite(imagem_com_texto, imagem)

def revelar(imagem_com_texto: str):
    # Carrega a imagem com (potencial) texto escondido
    imagem = cv2.imread(imagem_com_texto)
    
    # Armazena a quantidade de caracteres que se deseja recuperar o valor original
    qtde_caracter = trata_entrada("Digite a quantidade de caracteres que deseja recuperar: ", int)

    # Variáveis para denotar qual pixel iremos alterar
    x = 0
    y = 0
    bits = "" # Armazena os bits recuperados

    altura, largura, _ = imagem.shape
    for _ in range(qtde_caracter * 8):
        if x < largura:
            # Recupera pixel na coluna x, linha y e canal 0
            pixel = imagem[x, y, 0]

            # Recupera bit menos significativo
            bits += str(pixel & 1)

        # Se x for igual a largura da imagem, então passe para a próxima linha
        # e redefina x para 0
        if x == largura - 1:
            y += 1
            x = 0

        # Indica que todos os pixeis foram visitados
        if y == altura:
            print("A imagem acabou! Abortando.")
            exit(1)

        # Incrementa as colunas visitadas
        x += 1
    
    print(f"Texto revelado: {converte_bits_texto(bits)}")
