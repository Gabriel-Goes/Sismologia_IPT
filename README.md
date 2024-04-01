# Classificador Sismológico

## Pŕoximos Passos
### Eventos 100% Naturais ( Catálogo do IAG-USP )

- [x] Olhar o catálogo do IAG;
- [x] Primeira rodada separada; (100% Natural)
- [x] Passa-Alta 2Hz;
- [x] Histograma geral dia e horários de ocorrências; [UTC]
- [x] Sinais fora de horário Comercial;
- [ ] Olhar forma de onde no Snuffler;
    - Procurar por eventos apenas ruído. 
- [ ] Plotar no mapa;
    - Adicionar mapas no plot visualizacao.py.
- [ ] Localizações de pedreiras já conhecidas;
    - Utilizar shapefiles da ANM.
- [ ] Segunda rodada com todos os eventos sem filtrar por horário.
- [ ] Olhar se as formas de onda estão nos catálogos do IPT; [SC/RS/PR]

## Foco

Utilizando redes neurais convolucionais para classificar espectrogramas de sismos
entre eventos naturais e antropogênicos. Algoritmo desenvolvido em Python pelo
Laboratório de Planetologia e Geociências da Universidade de Nantes, França 
disponível no [GitLab](https://univ-nantes.io/E181658E/discrimination_eq_q).

O objetivo deste projeto é construir um sistema que possibilite a utilização do
algoritmo francês de forma dinâmica e eficiente, a fim, inicialmente, de aferir
a eficácia deste em eventos sismológicos brasileiros, e, caso positivo,  revisar
o catálogo de sismos do IAG-USP e do IPT.

## Instalação

### Clone do Repositório

```bash
mkdir ~/projetos/
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
pip install -r requirements.txt
```

## Utilização

### Adiquirindo Dados Sismológicos
O primeiro passo é adquirir os dados dos eventos sismológicos. Para isso, foi construída
uma pipeline que automatiza o processo de filtragem e download dos dados. Existem 
até agora duas formas de iniciar o processo de filtragem, a primeira é utilizando
um intervalo de tempo e a segunda é utilizando uma lista de eventos sismológicos.

¡Por padrão, a pipeline irá baixar _**apenas os 100 primeiros eventos**_ do catálogo de eventos
da MOHO, adquiridos no [site](http://moho.iag.usp.br/) e acessíveis no diretório
['./files/catalogo geo/catalogo-moho.csv'](https://github.com/Gabriel-Goes/sismologia_ipt/blob/main/files/catalogo/catalogo-moho.csv)
do repositório!


```bash
# Recomenda-se utilizar o tmux para executar a pipeline.
sudo chmod +x ./Sismo_Pipeline.sh
./Sismo_Pipeline.sh
```

Este processo criará um diretório ./files/mseed/ com subdiretórios nomeados pelo
código do evento no formato 'YYYYMMDDTHHMMSS'. Cada subdiretório conterá os arquivos
.mseed com 60 segundos de dados sismológicos, com 200Hz de taxa de amostragem.

A janela de aquisição do dado é iniciada com um valor aleatório entre 5 e 25 segundos
antes da onda 'P', mantendo sempre 60 segundos de janela total.


### Testando o Classificador
Coms os dados sismológicos adquiridos, podemos prosseguir para a classificação
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
sudo systemctl enable docker
sudo systemctl start docker

sudo usermod -aG docker $USER

DOCKER_BUILDKIT=1 docker build -t discrim:0.1.0 ./dotfiles
docker run -it --rm -v $HOME/projetos:/app discrim:0.1.0
```

### Testando o Discriminador
Dentro do contêiner, podemos testar o algoritmo com nossos dados sismológicos.
```bash 
export CS_files=../projetos/ClassificadorSismologico/files
python run.py\
    --data_dir $CS_files/mseed \
    --spectro_dir $CS_files/spectro \
    --output_dir $CS_files/output/non_commercial/ \
    --csv_dir $CS_files/predcsv/pred_not_commercial.csv \
    --valid
```
