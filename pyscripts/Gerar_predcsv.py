import os
import pandas as pd
from utils import mseed_folder

# Caminho para a pasta mseed_demo/ e para o arquivo events-all.csv
caminho_csv = './files/events-all.csv'

# Lendo o arquivo events-all.csv
df_events = pd.read_csv(caminho_csv, sep=';')  # Lendo com o separador correto

# Mapeando categorias para números
mapeamento_cat = {'Q': 1, 'E': 0, 'I': 0, 'N': 2}

# Criando um dicionário para mapear ID para label_cat
id_para_label = {row['ID']: mapeamento_cat.get(row['Cat'], 0) for _, row in df_events.iterrows()}

# Inicializando a lista para o novo DataFrame
dados_pred = []

# Lendo os nomes das pastas dentro de mseed_demo/
for nome_pasta in os.listdir(mseed_folder):
    # Verificando se o nome da pasta tem o comprimento esperado
    if len(nome_pasta) == 15:
        # Formatando o nome da pasta para corresponder ao formato no dicionário
        id_sismo = "IT_" + nome_pasta[:8] + "_" + nome_pasta[9:]
    else:
        # Se não, usa um valor padrão ou ignora esta pasta
        continue

    print(f' - {id_sismo}')
    label_cat = id_para_label.get(id_sismo, 'X')  # Usando X como padrão para IDs não encontrados

    # Adicionando ao DataFrame
    dados_pred.append({'time': nome_pasta, 'label_cat': label_cat})

# Criando um DataFrame a partir dos dados coletados
df_pred = pd.DataFrame(dados_pred)

print(f' -> {len(df_pred)} sismo(s) encontrados')
# Salvando o DataFrame em um arquivo CSV
df_pred.to_csv('./files/pred.csv', index=False)
