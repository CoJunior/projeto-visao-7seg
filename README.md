🔍 Sistema de Inspeção Visual QA com OpenCV e MQTT

Sistema de inspeção visual automatizada desenvolvido em Python 3, utilizando OpenCV, NumPy e MQTT.

O projeto utiliza uma câmera para analisar placas eletrônicas e identificar automaticamente o estado de LEDs, displays e indicadores visuais. Os resultados da inspeção são exibidos em tempo real e também enviados pela rede através do protocolo MQTT.

O sistema foi desenvolvido como base para aplicações de controle de qualidade (QA), visão computacional, IoT e automação industrial.

<p align="center">
  <img src="images/sistema_qa.png" width="78%" alt="Sistema QA em execução">
</p>

<p align="center">
  <em>Interface principal do sistema durante a inspeção.</em>
</p>

📑 Índice

Objetivo do projeto

O que o sistema faz

Demonstração do sistema

Modelos de inspeção

Como o sistema funciona

Estrutura do projeto

Tecnologias utilizadas

Pré-requisitos

Instalação passo a passo

Configurando a câmera

Configurando o Mosquitto MQTT

Executando o projeto

Configurando o MQTTX

Tópicos MQTT

Alterando o modelo remotamente

Formato das mensagens

Ajustando a detecção

Problemas comuns

Como modificar e continuar o projeto

🎯 Objetivo do projeto

Em uma bancada de testes, verificar manualmente se LEDs, displays e indicadores estão funcionando pode ser uma tarefa repetitiva e sujeita a erros humanos.

A proposta deste projeto é utilizar visão computacional para automatizar parte desse processo.

A câmera observa a placa e o software:

captura a imagem;

seleciona a região de interesse;

identifica determinadas cores;

analisa os LEDs e segmentos;

determina quais componentes estão ligados ou apagados;

apresenta o resultado na tela;

envia os resultados através de MQTT.

Dessa forma, outros sistemas também podem receber e utilizar os resultados da inspeção.

📌 O que o sistema faz?

Atualmente o projeto possui suporte para dois modelos de inspeção.

Modelo 1 — Displays de 7 segmentos

O sistema consegue:

analisar 3 displays de 7 segmentos (D1, D2 e D3);

verificar individualmente os segmentos A, B, C, D, E, F e G;

indicar quais segmentos estão ON ou OFF;

detectar o indicador de Bateria;

detectar o indicador de Floco de Neve;

aplicar filtros para diminuir interferências entre LEDs;

apresentar visualmente as regiões analisadas;

publicar o resultado da inspeção via MQTT.

Modelo 2 — Placa circular

O segundo modo analisa uma placa contendo LEDs distribuídos em dois grupos.

O sistema:

detecta LEDs vermelhos;

detecta LEDs amarelos;

conta os LEDs detectados;

verifica o estado do anel interno;

verifica o estado do anel externo;

envia as contagens e estados através de MQTT.

🖥️ Demonstração do sistema

1. Interface principal de inspeção

<p align="center">
  <img src="images/sistema_qa.png" width="78%" alt="Sistema QA">
</p>

<p align="center">
  <em>A interface principal mostra o estado dos displays e dos indicadores Floco e Bateria em tempo real.</em>
</p>

2. Gabarito e detecção individual dos segmentos

<p align="center">
  <img src="images/gabarito_inspecao.png" width="72%" alt="Gabarito de inspeção">
</p>

<p align="center">
  <em>Cada display é dividido em sete regiões correspondentes aos segmentos A, B, C, D, E, F e G.</em>
</p>

O gabarito facilita o alinhamento da placa com a câmera e também ajuda durante a calibração das regiões de interesse.

3. Envio dos resultados via MQTT

<p align="center">
  <img src="images/mqttx.png" width="95%" alt="Mensagens MQTT no MQTTX">
</p>

<p align="center">
  <em>Os resultados são enviados em formato JSON e podem ser acompanhados pelo MQTTX.</em>
</p>

🔄 Modelos de inspeção

O sistema possui uma variável interna chamada:

modo_operacao

Ela determina qual algoritmo será executado.

Modelo

Inspeção

1

Displays de 7 segmentos + Floco + Bateria

2

Placa circular com LEDs vermelhos e amarelos

Por padrão, o programa inicia no Modelo 1.

A mudança de modelo pode ser feita remotamente através de uma mensagem MQTT. Isso permite que outro programa, supervisório ou dispositivo IoT controle qual tipo de placa deve ser analisado.

🧠 Como o sistema funciona

O processamento principal é realizado utilizando a biblioteca OpenCV.

Fluxo simplificado:

Câmera
   ↓
Captura do frame
   ↓
Região de Interesse (ROI)
   ↓
Conversão BGR → HSV
   ↓
Criação de máscaras de cor
   ↓
Filtros morfológicos
   ↓
Análise dos LEDs / segmentos
   ↓
Determinação do estado
   ↓
Interface OpenCV
   ↓
MQTT
   ↓
Outras aplicações

🎨 Por que utilizar HSV?

A câmera normalmente fornece imagens no formato BGR. O programa converte a imagem para HSV:

H — Hue (Matiz)

S — Saturation (Saturação)

V — Value (Brilho)

Esse formato facilita a separação de cores e é muito útil para detectar LEDs vermelhos, azuis e amarelos.

🔲 ROI — Região de Interesse

Em vez de analisar toda a imagem capturada pela câmera, o Modelo 1 utiliza uma região específica chamada ROI — Region of Interest.

Isso ajuda a:

diminuir o processamento;

ignorar partes desnecessárias da imagem;

manter os displays sempre em posições conhecidas;

melhorar a confiabilidade da detecção.

💡 Detecção dos 7 segmentos

Cada display é dividido em sete pequenas regiões:

       A
     -----
  F |     | B
    |  G  |
     -----
  E |     | C
    |     |
     -----
       D

O programa analisa cada região separadamente e determina se o segmento está ON ou OFF.

📂 Estrutura do projeto

Uma estrutura recomendada é:

PROJETO_VISAO_7SEG/
│
├── images/
│   ├── sistema_qa.png
│   ├── gabarito_inspecao.png
│   └── mqttx.png
│
├── comunicacao_mqtt.py
├── main_inspecao.py
├── requirements.txt
├── README.md
└── .gitignore

Durante o desenvolvimento também podem existir:

venv/
__pycache__/

Essas pastas são geradas localmente e não precisam ser enviadas para o GitHub.

main_inspecao.py

É o programa principal. Ele é responsável por:

abrir a câmera;

capturar as imagens;

processar os frames;

criar máscaras de cor;

analisar as regiões de interesse;

detectar os displays;

detectar os LEDs;

desenhar informações na tela;

selecionar o algoritmo correspondente ao modelo atual;

enviar os resultados para o módulo MQTT.

comunicacao_mqtt.py

É responsável pela comunicação MQTT.

Ele:

conecta ao broker;

publica os resultados;

recebe comandos;

controla o modelo de inspeção selecionado.

requirements.txt

Contém as bibliotecas Python necessárias:

opencv-python
numpy
paho-mqtt

🛠️ Tecnologias utilizadas

Python 3

OpenCV

NumPy

Paho MQTT

MQTT

Mosquitto

Visão Computacional

Processamento Digital de Imagens

IoT

⚙️ Pré-requisitos

Hardware

computador;

webcam USB ou câmera compatível com OpenCV;

placa ou painel que será analisado.

Software

Recomendado:

Python 3
pip3
python3-venv
Mosquitto MQTT Broker
MQTTX
Git

O MQTTX é recomendado para visualizar e testar as mensagens MQTT, mas não é obrigatório para o funcionamento do algoritmo.

🚀 Instalação passo a passo

Esta seção foi escrita pensando também em quem possui pouca experiência com Python ou Git.

1. Instalar o Git

No Ubuntu/Debian:

sudo apt update
sudo apt install git

Verifique:

git --version

2. Instalar Python 3

No Ubuntu/Debian:

sudo apt update
sudo apt install python3 python3-pip python3-venv

Confira a instalação:

python3 --version

Confira também o pip:

pip3 --version

Este projeto utiliza Python 3. Por isso, neste README os comandos são apresentados utilizando python3.

3. Clonar o repositório

Abra um terminal e escolha uma pasta onde deseja salvar o projeto.

git clone URL_DO_REPOSITORIO

Exemplo:

git clone https://github.com/SEU_USUARIO/PROJETO_VISAO_7SEG.git

Depois entre na pasta:

cd PROJETO_VISAO_7SEG

Para verificar os arquivos:

ls

Você deverá encontrar pelo menos:

main_inspecao.py
comunicacao_mqtt.py
requirements.txt
README.md

🐍 Criando o ambiente virtual

É altamente recomendado utilizar um ambiente virtual.

Dentro da pasta do projeto:

python3 -m venv venv

Ativando no Linux/macOS

source venv/bin/activate

Quando estiver ativo, normalmente aparecerá algo parecido com:

(venv) usuario@computador:~/PROJETO_VISAO_7SEG$

Ativando no Windows

Prompt de Comando:

venv\Scripts\activate

PowerShell:

.\venv\Scripts\Activate.ps1

Como sair do ambiente virtual?

deactivate

📦 Instalando as dependências

Com o ambiente virtual ativo:

python3 -m pip install --upgrade pip

Depois:

python3 -m pip install -r requirements.txt

Você pode conferir as bibliotecas instaladas com:

python3 -m pip list

📷 Configurando a câmera

No arquivo main_inspecao.py existe a configuração:

CAMERA_INDEX = 1

O número representa a câmera que o OpenCV deverá utilizar.

Dependendo do computador, pode ser necessário utilizar:

CAMERA_INDEX = 0

ou:

CAMERA_INDEX = 2

Se o programa abrir mas nenhuma imagem aparecer, este é um dos primeiros parâmetros que deve ser verificado.

No Linux também é possível verificar os dispositivos de vídeo com:

ls /dev/video*

📡 Configurando o Mosquitto MQTT

O projeto está configurado por padrão para procurar um broker MQTT em:

localhost:1883

Isso significa que o Mosquitto deve estar rodando no mesmo computador do programa, a menos que você altere essa configuração.

Instalando no Ubuntu/Debian

sudo apt update
sudo apt install mosquitto mosquitto-clients

Inicie o serviço:

sudo systemctl start mosquitto

Para iniciar automaticamente com o sistema:

sudo systemctl enable mosquitto

Verifique:

systemctl status mosquitto

Se estiver funcionando corretamente, deverá aparecer algo semelhante a:

active (running)

Usando um broker em outro computador

Abra comunicacao_mqtt.py.

Por padrão:

BROKER = "localhost"
PORTA = 1883

Se o Mosquitto estiver em outro computador, substitua localhost pelo endereço IP correspondente.

Exemplo:

BROKER = "192.168.0.100"
PORTA = 1883

▶️ Executando o projeto

Entre na pasta do projeto:

cd PROJETO_VISAO_7SEG

Ative o ambiente virtual:

source venv/bin/activate

Certifique-se de que o Mosquitto está funcionando:

systemctl status mosquitto

Depois execute:

python3 main_inspecao.py

No terminal deverá aparecer uma mensagem semelhante a:

--- SISTEMA DE INSPEÇÃO QA MULTI-MODELO ---
Pressione 'q' na janela do vídeo para encerrar.

Encerrando o programa

Clique em uma das janelas do OpenCV e pressione:

q

O programa encerrará a câmera, a conexão MQTT e as janelas do OpenCV.

📡 Configurando o MQTTX

Crie uma conexão com os seguintes dados:

Campo

Valor

Name

qualquer nome, por exemplo Bancada

Host

localhost

Port

1883

Username

vazio

Password

vazio

Depois clique em Connect.

📬 Tópicos MQTT

A versão atual utiliza dois tópicos principais.

Resultados da inspeção

qa/bancada/status

O programa publica os resultados da inspeção nesse tópico.

No MQTTX, crie uma subscription para:

qa/bancada/status

Comandos

qa/bancada/comando

O programa fica inscrito nesse tópico para receber comandos.

🔄 Alterando o modelo remotamente

Para selecionar o Modelo 1, publique no tópico:

qa/bancada/comando

esta mensagem:

{
  "modelo": 1
}

Para selecionar o Modelo 2:

{
  "modelo": 2
}

Essa arquitetura permite que futuramente uma interface web, ESP32 ou outro sistema escolha automaticamente qual inspeção deve ser realizada.

📤 Formato das mensagens

Os dados são enviados em JSON.

Estrutura geral:

{
  "Timestamp": "AAAA-MM-DD HH:MM:SS",
  "Modelo_Atual": 1,
  "Inspecao": {}
}

Exemplo — Modelo 1

{
  "Timestamp": "2026-06-17 10:45:00",
  "Modelo_Atual": 1,
  "Inspecao": {
    "Displays": {
      "D1": {
        "A": "OFF",
        "B": "ON",
        "C": "ON",
        "D": "OFF",
        "E": "OFF",
        "F": "OFF",
        "G": "OFF"
      }
    },
    "Icones": {
      "Floco": "LIGADO",
      "Bateria": "APAGADA"
    }
  }
}

Exemplo — Modelo 2

{
  "Timestamp": "2026-06-17 10:45:00",
  "Modelo_Atual": 2,
  "Inspecao": {
    "Anel_Interno": "LIGADO",
    "Anel_Externo": "LIGADO",
    "Contagem_Vermelhos": 3,
    "Contagem_Amarelos": 9
  }
}

🎛 Ajustando a detecção

Os principais parâmetros estão no arquivo main_inspecao.py.

Índice da câmera

CAMERA_INDEX = 1

Resolução

CAM_WIDTH = 640
CAM_HEIGHT = 480

Tamanho da região de inspeção

ROI_W = 560
ROI_H = 260

Limiar de detecção azul

LIMIAR_AZUL = 0.45

Se segmentos ligados não forem detectados, pode ser necessário diminuir o valor.

Se segmentos apagados forem identificados incorretamente como ligados, pode ser necessário aumentar o valor.

Faça alterações pequenas e teste novamente.

Faixas HSV

Por exemplo, para azul:

lower_blue = np.array([95, 120, 120])
upper_blue = np.array([135, 255, 255])

Esses valores podem precisar de calibração caso:

a câmera seja trocada;

a iluminação mude;

os LEDs tenham tonalidade diferente;

exista muita luz ambiente.

🔧 Problemas comuns

python: command not found

Este projeto utiliza Python 3.

python3 --version

Execute o projeto com:

python3 main_inspecao.py

No module named cv2

Ative o ambiente virtual:

source venv/bin/activate

Depois:

python3 -m pip install -r requirements.txt

No module named paho

python3 -m pip install paho-mqtt

A câmera não abre

Altere:

CAMERA_INDEX = 1

para:

CAMERA_INDEX = 0

Depois execute novamente:

python3 main_inspecao.py

MQTT não conecta

Verifique:

systemctl status mosquitto

Caso esteja parado:

sudo systemctl start mosquitto

Também confirme no comunicacao_mqtt.py:

BROKER = "localhost"
PORTA = 1883

MQTTX conecta, mas não aparecem mensagens

Confira se a inscrição foi feita no tópico atual:

qa/bancada/status

Depois verifique se o programa Python está executando.

O programa detecta segmentos incorretamente

Isso normalmente está relacionado a:

posição da placa;

iluminação;

reflexos;

configuração HSV;

valor do LIMIAR_AZUL;

posição das ROIs;

distância entre câmera e placa.

Tente manter a placa alinhada com o gabarito mostrado pelo programa.

👨‍💻 Como modificar e continuar o projeto

Os dois arquivos mais importantes são:

main_inspecao.py
comunicacao_mqtt.py

Para alterar visão computacional

Modifique main_inspecao.py.

Aqui ficam:

câmera;

ROIs;

máscaras HSV;

filtros;

detecção dos displays;

detecção dos LEDs;

interface visual.

Para alterar comunicação MQTT

Modifique comunicacao_mqtt.py.

Aqui ficam:

endereço do broker;

porta;

tópicos;

publicação;

recebimento de comandos;

seleção do modelo.

➕ Adicionando novos modelos

A estrutura atual permite continuar expandindo o sistema.

Atualmente:

Modelo 1 → Display de 7 segmentos
Modelo 2 → Placa circular

Uma futura versão poderia adicionar novos modelos e continuar utilizando MQTT para selecionar qual algoritmo será executado.

🔃 Atualizando o projeto pelo Git

Caso você já tenha clonado o projeto anteriormente:

git pull

Se as dependências tiverem sido alteradas:

python3 -m pip install -r requirements.txt

🌱 Criando uma branch para trabalhar no projeto

git checkout -b minha-funcionalidade

Depois das alterações:

git status
git add .
git commit -m "Adiciona nova funcionalidade"

🗑️ Arquivos que não devem ir para o GitHub

É recomendado manter no .gitignore:

venv/
__pycache__/
*.pyc

A pasta venv pode ser recriada com:

python3 -m venv venv

🚀 Possíveis melhorias futuras

adicionar novos modelos de placas;

criar calibração automática das ROIs;

desenvolver interface web;

integrar com ESP32;

armazenar resultados em banco de dados;

gerar histórico das inspeções;

registrar peças aprovadas e reprovadas;

criar dashboard de produção;

adicionar identificação automática do modelo da placa;

gerar relatórios;

utilizar Machine Learning para classificação;

integrar com sistemas industriais;

executar o processamento em Raspberry Pi;

adicionar configuração externa sem precisar alterar o código.

👨‍💻 Autor

Junior Co

Estudante de Engenharia de Computação.

Projeto desenvolvido envolvendo conceitos de:

Visão Computacional;

Processamento Digital de Imagens;

Python 3;

Internet das Coisas (IoT);

MQTT;

Automação;

Controle de Qualidade.

🤝 Contribuições

Contribuições são bem-vindas.

Caso queira utilizar este projeto como base para estudos ou desenvolver novas funcionalidades, faça um fork do repositório e trabalhe em uma branch separada.

⭐ Projeto

Se este projeto foi útil para seus estudos ou desenvolvimento, considere deixar uma ⭐ no repositório.

Isso ajuda outras pessoas a encontrarem o projeto e incentiva a continuidade do desenvolvimento.