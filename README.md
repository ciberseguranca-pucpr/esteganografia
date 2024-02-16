# Esteganografia com método do bit menos significativo (LSB)
Algoritmo de substituição do bit menos significativo de imagens para esconder texto/imagem dentro de outra imagem. Implementação feita em Python utilizando a biblioteca [```opencv-python```](https://github.com/opencv/opencv-python) para a manipulação das imagens.

## Dependências
- Python (versão >= 3.8)
- [```opencv-python```](https://github.com/opencv/opencv-python)

## Baixando o projeto
Para baixar o projeto você pode fazer de duas maneiras: utilizando ```git``` ou baixando direto o código fonte.

### ```git```
1. Abra um terminal/cmd
2. Digite ```git clone https://github.com/ciberseguranca-pucpr/esteganografia.git```
3. Acesse o diretório ```esteganografia``` (digite: ```cd esteganografia```)
4. Prossiga para a seção [Preparação do ambiente](#preparação-do-ambiente)

### Código fonte
1. Clique no botão ```Code```
2. Clique no botão ```Download ZIP```
3. Extraia para um diretório qualquer
4. Prossiga para a seção [Preparação do ambiente](#preparação-do-ambiente).

## Preparação do ambiente
Para mantermos nosso sistema limpo, sugiro a criação de um ambiente virtual em Python. Para isso, siga os passos a seguir. Caso não deseje, prossiga para a seção [Instalação de dependências](#instalação-de-dependências).

### Criação do ambiente virtual
Assumindo que você já possua o Python instalado no seu sistema, a própria instalação da linguagem permitirá você criar o ambiente virtual. Para isso, digite o comando a seguir (no mesmo diretório do projeto):
```sh
python -m venv venv
```

Para você ativá-lo, digite: 

#### Windows
```powershell
.\venv\Scripts\activate
```

#### MacOS ou Linux
```sh
source venv/bin/activate
```

Como resultado desse comando, deve aparecer o texto ```(venv)``` ao lado do seu prompt de comando. Uma vez ativado o ambiente virtual, siga para a próxima seção para a instalação das dependências.

### Instalação de dependências
Com o seu ambiente virtual ativado, digite o comando:
```sh
pip install -r requirements.txt
```

Ele irá instalar a biblioteca [```opencv-python```](https://github.com/opencv/opencv-python) e suas dependências no projeto. Após instalada as dependências, a seção seguinte irá demonstrar como utilizar a ferramenta.

# Como usar
Com o ambiente virtual ativado e as dependências instaladas, vamos prosseguir com a utilização da ferramenta. Para utilizar corretamente, sempre executaremos ela com o seguinte comando:

```sh
python -m steg [FLAGS]
```

Onde ```[FLAGS]``` são as opções disponíveis da ferramenta. Vamos dar uma olhada em todas elas.

```text
usage: steg [-h] -i IMAGEM_ENTRADA [-o IMAGEM_SAIDA] -f {esconder,revelar} [-t]

options:
  -h, --help            show this help message and exit
  -i IMAGEM_ENTRADA     Caminho para a imagem original
  -o IMAGEM_SAIDA       Caminho para a imagem com texto escondido
  -f {esconder,revelar}
                        Ação que deseja realizar
  -t                    Flag que especifica se deseja esconder um texto ou imagem
```
## Texto

### Escondendo texto em uma imagem
Para esconder algum texto em uma imagem você deverá fornecer uma imagem como base presente no seu computador. Assim, ele irá inserir o texto digitado na imagem resultante. Veja o comando a seguir:

```sh
python -m steg -i exemplos/original.png -o exemplos/escondido.png -f esconder
Digite o texto que deseja esconder: ola
Mensagem escondida: ola (011011110110110001100001)
```

| Flag | Valor                  | Descrição                                                                                           |
|------|------------------------|-----------------------------------------------------------------------------------------------------|
| ```-i```   | ```exemplos/original.png```  | Caminho para a imagem original, ou seja, naquela que se deseja esconder um determinado texto/imagem |
| ```-o```   | ```exemplos/escondido.png```| Caminho para a imagem resultante, ou seja, onde e com qual nome salvarei a imagem resultante        |
| ```-f```   | ```esconder```               | Procedimento de esconder o texto na imagem                                                          |
| ```-t```   |             | Indica que irá esconder um texto                                                          |

Após o comando executado, você verá que no diretório ```exemplos``` uma imagem ```escondido.png``` foi gerada,onde contém o texto que escondemos.

### Recuperando texto de uma imagem
Para recuperar uma imagem é bastante simples. Veja o exemplo a seguir:

| Flag | Valor                  | Descrição                                                                                           |
|------|------------------------|-----------------------------------------------------------------------------------------------------|
| ```-i```   | ```exemplos/escondido.png```  | Caminho para a imagem com texto escondido, ou seja, naquela que se deseja revelar um determinado texto/imagem |
| ```-f```   | ```revelar```               | Procedimento de revelar o texto da imagem                                                          |
| ```-t```   |             | Indica que irá esconder um texto                                                          |

```sh
python -m steg -i exemplos/original.png -f revelar
Digite a quantidade de caracteres que deseja recuperar: 3 
Texto revelado: ola
```

Assim recuperamos o texto que escondemos!

## Imagem
### Escondendo uma imagem em outra imagem
Para esconder uma imagem, você precisa ter uma imagem de no máximo 255x255. Nesse exemplo será utilizada uma imagem 50x50. Veja o comando a seguir:
```sh
python -m steg -i exemplos/original.png -o imagem_escondida.png -f esconder
Digite o caminho da imagem que deseja esconder: exemplos/saitama.png
Mensagem escondida: ... (bits removido por ser muito longo)
```

| Flag | Valor                  | Descrição                                                                                           |
|------|------------------------|-----------------------------------------------------------------------------------------------------|
| ```-i```   | ```exemplos/original.png```  | Caminho para a imagem original, ou seja, naquela que se deseja esconder um determinado texto/imagem |
| ```-o```   | ```imagem_escondida.png```| Caminho para a imagem resultante, ou seja, onde e com qual nome salvarei a imagem resultante        |
| ```-f```   | ```esconder```               | Procedimento de esconder o texto na imagem                                                          |

Após o comando executado, você verá que no diretório do projeto haverá uma imagem ```imagem_escondida.png```, onde contém a imagem que escondemos.

### Recuperando uma imagem de outra imagem
Para recuperar uma imagem que foi escondida, é só trocar a ordem dos valores que foram inseridos na etapa anterior. Veja o comando a seguir:
```sh
python -m steg -i imagem_escondida.png -o imagem_revelada.png -f revelar 
```

| Flag | Valor                  | Descrição                                                                                           |
|------|------------------------|-----------------------------------------------------------------------------------------------------|
| ```-i```   | ```imagem_escondida.png```  | Caminho para a imagem original, ou seja, naquela que se deseja esconder um determinado texto/imagem |
| ```-o```   | ```imagem_revelada.png```| Caminho para a imagem resultante, ou seja, onde e com qual nome salvarei a imagem resultante        |
| ```-f```   | ```esconder```               | Procedimento de esconder o texto na imagem                                                          |

Após o comando executado, você verá que no diretório do projeto haverá uma imagem ```imagem_revelada.png```, sendo a imagem original que havíamos escondido.


# Referências
- [What is Least significant bit algorithm in Information Security? (INGLÊS)](https://www.tutorialspoint.com/what-is-least-significant-bit-algorithm-in-information-security)
- [LSB: Least Significant Bits](https://wiki.imesec.ime.usp.br/books/ctf-starter-pack/page/lsb-least-significant-bits)