# Classificador Sismológico

Utilizando redes neurais convolucionais para classificar espectrogramas de sismos
entre eventos naturais e antropogênicos. Algoritmo desenvolvido em Python pelo
Laboratório de Planetologia e Geociências da Universidade de Nantes, França 
disponível no [GitLab](https://univ-nantes.io/E181658E/discrimination_eq_q).

Este repositório armazena os códigos desenvolvidos por G.G., Rocha de Lima em 
conjunto com o setor de Sismologia do IPT comandado por L. A., Schirbel. Este
código possibilita a automação do algoritmo de classificação de Houcard, dede
a etapa de aquisição, armazenamento e pré-processamento até a análise das 
métricas de seu modelo.

# Sumário
- [Foco](#foco)
- [Instalação](#instalação)
- [Utilização](#utilização)
    - [Adiquirindo Dados Sismológicos](#adiquirindo-dados-sismológicos)
    - [Testando o Classificador](#testando-o-classificador)
        - [Ambiente virtual do 'discrimination_eq_q'](#ambiente-virtual-do-discrimination_eq_q)
    - [Testando o Discriminador](#testando-o-discriminador)
- [Referências](#referências)

## Primeiros-Passos

### Testando Algoritmo com Eventos Naturais
A ideia inicial é utilizar o catálogo do MOHO ( IAG-USP ) para adquirir apenas 
dados sismicos de eventos naturais para testar a eficiencia do algoritmo em 
discriminar eventos antrópicos dos naturais do território brasileiro.

Além de adquirir apenas dados que foram rotulados por especialistas, nós
separamos os eventos em duas categorias, os que ocorreram em horário comercial
e não-comercial. Sendo a janela de separação 11:00 UTC até 23:00 UTC, visto que
o território brasileiro abrange a zona do -3 UTC à -5 UTC.

- [x] Adquirir [catálogo](https://github.com/Gabriel-Goes/sismologia_ipt/blob/main/files/catalogo/catalogo-moho.csv) de eventos naturais do IAG-USP;
- [x] Seperar eventos entre comericias e não-comerciais;
- [ ] Olhar forma de onde no Snuffler;
    - Desenvolvimento de [Snuffling](www.pyrocko.com). 
- [ ] Plotar no mapa;
    - Adicionar mapas no plot visualizacao.py.
- [ ] Localizações de pedreiras já conhecidas;
    - Utilizar shapefiles da ANM.
- [ ] Segunda rodada com todos os eventos sem filtrar por horário.
- [ ] Olhar se as formas de onda estão nos catálogos do IPT; [SC/RS/PR]

## Foco

O objetivo deste projeto é construir um sistema que possibilite a utilização do
algoritmo francês de forma dinâmica e eficiente, a fim, inicialmente, aferir a
eficácia deste em eventos sismológicos brasileiros, e, caso positivo,  revisar
o catálogo de sismos do IAG-USP e do IPT.

## Instalação

Siga os tópicos abaixo copiando e colando os códigos em seu terminal. Este 
roteiro, tem compatibilidade testada para as distribuições GNU/Linux que utilizam
os gerenciadores de pacotes APT (Debian e derivados) e PACMAN ( Arch Linux e
derivados).

### Clone do Repositório
```bash
mkdir ~/projetos/  # CRIE ESTE DIRETÓRIO PARA MELHOR ORGANIZAÇÃO
git clone git@github.com:Gabriel-Goes/sismologia_ipt.git\
    ~/projetos/ClassificadorSismologico && cd projetos/ClassificadorSismologico
git switch desenvolvimento  # Ainda não houve merge com a branch main
```

### Crie e ative o Ambiente Virtual e Instale as Dependências
Com este script de instalação, temos automatizado o processo de criação de
ambientes virtuais python para cada um de nossos projetos. Execute o modo padrão
para criar e instalar o python 3.11.
```bash
sudo chmod +x ./dotfiles/install.sh
source ./dotfiles/install.sh
pyenv local sismologia

# DEVO REDUZIR O NÚMERO DE DEPENDÊÊCIAS PARA O AMBIENTE VIRTUAL.
# E TALVEZ CRIAR UMA IMAGEM DOCKER PARA ESTE CÓDIGO TAMBÉM.
pip install -r ./dotfiles/requirements.txt
```

## Utilização
Com o repositório instalado e o ambiente virtual python configurado, basta seguir
os passos a seguir.

### Adiquirindo Dados Sismológicos
Primeiro vamos adquirir os dados dos eventos sismológicos. Para isso, foi
construída uma pipeline que automatiza o processo de filtragem e armazenamento 
dos dados. Por enquanto, temos apenas uma forma de executar a (pipeline](https://github.com/Gabriel-Goes/sismologia_ipt/blob/main/)

**Atenção:**
Por padrão, a pipeline irá baixar _**apenas os 100 primeiros eventos**_ do
catálogo de eventos da MOHO, adquiridos no [site](http://moho.iag.usp.br/) e
acessíveis no diretório ['./files/catalogo geo/catalogo-moho.csv'](https://github.com/Gabriel-Goes/sismologia_ipt/blob/main/files/catalogo/catalogo-moho.csv)
do repositório.

```bash
# Execute o script de pipeline
sudo chmod +x ./Sismo_Pipeline.sh
./Sismo_Pipeline.sh
```

Este processo criará um dietório ./files/mseed/ com subdiretórios nomeados pelo
código do evento no formato `'YYYYMMDDTHHMMSS'`. Cada subdiretório conterá os arquivos
.mseed com 60 segundos de dados sismológicos, com 200Hz de taxa de amostragem.

A janela de aquisição do dado é iniciada com um valor aleatório entre 5 e 25 segundos
antes da chegada da onda 'P', mantendo sempre 60 segundos de janela total.

Para relizar análises de razões de sinal-ruído, será necessário, talvez, adquirir
janelas de tempo maiores, assim como adquirir a chegada da onda 'S'.


### Testando o Classificador
Com os dados sismológicos adquiridos, podemos prosseguir para a classificação
dos eventos sismológicos utilizando o algoritmo de redes neurais convolucionais.

```bash
# Clone o repositório em nossa pasta '~/projetos'
git clone https://gitlab.univ-nantes.fr/E181658E/discrimination_eq_q.git \
    ~/projetos/discrimination_eq_q
```

#### Ambiente virtual do 'discrimination_eq_q'
Como o algoritmo foi escrito em pytho3.7 e utilizamos o python3 mais recente para
o desenvolvimento do ClassificadorSismologico, é necessário criar um novo ambiente
virtual com compatibilidade de versão. Para isto, está disponibilizado um dockerfile
que cria o ambiente virtual contêinerizado e instala as dependências necessárias.

```bash
# Failed to enable unit: Unit file docker.service does not exist.
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

Para efetivar a adição do grupo, é necessário executar o login novamente.
No mesmo terminal, você pode executar estes comandos:

```bash
sudo login $USER
cd ~/projetos/ClassificadorSismologico
DOCKER_BUILDKIT=1 docker build -t discrim:0.1.0 ./dotfiles
docker run -it --rm -v $HOME/projetos:/app discrim:0.1.0
``` 

### Testando o Discriminador
Dentro do contêiner, podemos testar o algoritmo com nossos dados sismológicos.

```bash 
export CS_files=./ClassificadorSismologico/files
python ./discrimination_eq_q/run.py\
    --data_dir $CS_files/mseed \
    --spectro_dir $CS_files/spectro \
    --output_dir $CS_files/output/non_commercial/ \
    --csv_dir $CS_files/predcsv/pred_not_commercial.csv \
    --valid
```

## Referências
- [Laboratório de Planetologia e Geociências da Universidade de Nantes](https://univ-nantes.io/E181658E/discrimination_eq_q)
