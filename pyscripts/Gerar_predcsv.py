import os
import pandas as pd
from utils import mseed_folder
from datetime import datetime

# Caminho para a pasta mseed_demo/ e para o arquivo events-all.csv
caminho_csv = './files/events-all.csv'

# Lendo o arquivo events-all.csv
df_events = pd.read_csv(caminho_csv, sep=';')  # Lendo com o separador correto

# Mapeando categorias para números
mapeamento_cat = {'Q': 1, 'E': 0, 'I': 0, 'N': 2}

# Criando um dicionário para mapear ID para label_cat
id_para_label = {row['ID']: mapeamento_cat.get(row['Cat'], 0) for _, row in df_events.iterrows()}

# Inicializando a lista para o novo DataFrame
commercial_pred = []
notcommercial_pred = []
pastas_ignoradas = []


# Constroi a lista com os dados da predição
# time, label_cat
def constroi_dados_pred():
    # Lendo os nomes das pastas dentro de mseed_demo/
    for nome_pasta in os.listdir(mseed_folder):
        # Verificando se o nome da pasta tem o comprimento esperado
        if len(nome_pasta) == 15:
            # Formatando o nome da pasta para corresponder ao formato no dicionário
            id_sismo = nome_pasta
        else:
            # Se não, usa um valor padrão ou ignora esta pasta
            print(f'! {nome_pasta} não é um nome de pasta válido')
            pastas_ignoradas.append(nome_pasta)
            continue

        label_cat = id_para_label.get(id_sismo, 0)  # Usando X como padrão para IDs não encontrados
        # Verificando se o sismo ocorreu em horário comercial
        print(id_sismo)
        id_datetime = datetime.strptime(id_sismo, '%Y%m%dT%H%M%S')
        if 11 <= id_datetime.hour < 22:
            commercial_pred.append({'time': nome_pasta, 'label_cat': label_cat})

        else:
            notcommercial_pred.append({'time': nome_pasta, 'label_cat': label_cat})

    # DataFrame com os nomes das pastas ignoradas
    df_erros = pd.DataFrame(pastas_ignoradas, columns=['pastas_ignoradas'])
    # Criando um DataFrame a partir dos dados coletados
    commercial_df = pd.DataFrame(commercial_pred)
    notcommercial_df = pd.DataFrame(notcommercial_pred)
    print(f' -> {len(pastas_ignoradas)} pasta(s) ignorada(s)')
    print(f' -> {len(commercial_df)} sismo(s) encontrados em  horário comercial')
    print(f' -> {len(notcommercial_df)} sismo(s) encontrados fora do horário comercial')

    return commercial_df, notcommercial_df, df_erros


# ------------------------------ MAIN -----------------------------------------
if __name__ == '__main__':
    commercial_df, notcommercial_df, df_erros = constroi_dados_pred()
    # Salva os erros de pastas ignoradas em um csv
    df_erros.to_csv('./files/erros.csv', index=False)
    # Salvando o DataFrame em um arquivo CSV
    commercial_df.to_csv('./files/commercial_pred.csv', index=False)
    notcommercial_df.to_csv('./files/notcommercial_pred.csv', index=False)
