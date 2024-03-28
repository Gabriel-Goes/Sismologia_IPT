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
Laboratório de Planetologia e Geociências da Universidade de Nantes, França disponível
no [GitLab](https://univ-nantes.io/E181658E/discrimination_eq_q).

O objetivo deste projeto é construir um sistema que possibilite a utilização do
algoritmo francês de forma dinâmica e eficiente, a fim, inicialmente, de aferir
a eficácia deste em eventos sismológicos brasileiros, e, caso positivo,  revisar
o catálogo de sismos do IAG-USP e do IPT.

## Instalação

### Clone o Repositório

```bash
git clone git@github.com:Gabriel-Goes/sismologia_ipt.git projetos/ClassificadorSismologico && cd projetos/ClassificadorSismologico
git switch desenvolvimento  # Ainda não houve merge com a branch main
```

### Crie e ative o Ambiente Virtual e Instale as Dependências

```bash
python3 -m venv geo 
pip install -r ./dotfiles/requirements.txt
source venv/bin/activate
# Instale o ClassificadorSismologico como um pacote em desenvolvimento. 
pip install -e .
```

## Utilização

### Adiquirindo Dados Sismológicos
O primeiro passo é adquirir os dados dos eventos sismológicos. Para isso, foi construída
uma pipeline que automatiza o processo de filtragem e download dos dados. Existem 
até agora duas formas de iniciar o processo de filtragem, a primeira é utilizando
um intervalo de tempo e a segunda é utilizando uma lista de eventos sismológicos.

Por padrão, a pipeline irá baixar os 100 primeiros eventos do catálogo de eventos
da MOHO, adquiridos no [site](http://moho.iag.usp.br/) e acessíveis no diretório
['./files/catalogo geo/catalogo-moho.csv'](https://github.com/Gabriel-Goes/sismologia_ipt/blob/main/files/catalogo/catalogo-moho.csv)
do repositório.


```bash
# Recomenda-se utilizar o tmux para executar a pipeline.
sudo chmod +x ./Sismo_Pipeline.sh
./Sismo_Pipeline.sh
```

### Testando o Classificador

```bash
mkdir ~/projetos/
git clone git@gitlab.univ-nantes.fr:E181658E/discrimination_eq_q.git \
    ~/projetos/discrimination_eq_q
```

#### Ambiente virtual do 'discrimination_eq_q'

Como o algoritmo foi escrito em pytho3.7 e utilizamos o python3 mais recente para
o desenvolvimento do ClassificadorSismologico, é necessário criar um novo ambiente
virtual com compatibilidade de versão. Para isto, está disponibilizado um bash script
que cria o ambiente virtual e instala as dependências necessárias.

Este processo utilizará todos os núcleos disponíveis do processador para compilar
o python3.7, o que deve levar um tempo considerável e deixar sua máquina lenta,
pode ser um bom momento para se alongar. 

```bash
sudo chmod +x ./dotfiles/install.sh
./install.sh
cd ~/projetos/discrimination_eq_q
source .config/discrim/bin/activate
```

### Testando o Discriminador

```bash 
export CS_files=~/projetos/ClassificadorSismologico/files
python run.py\
    --data_dir $CS_files/mseed \
    -spectro_dir $CS_files/spectro \
    --output_dir $CS_files/output/non_commercial/ \
    --csv_dir $CS_files/predcsv/test.csv \
    --valid
```
