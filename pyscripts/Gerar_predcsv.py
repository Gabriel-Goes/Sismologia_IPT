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

        # Adicionando ao DataFrame
        dados_pred.append({'time': nome_pasta, 'label_cat': label_cat})

    # DataFrame com os nomes das pastas ignoradas
    df_erros = pd.DataFrame(pastas_ignoradas, columns=['pastas_ignoradas'])
    # Criando um DataFrame a partir dos dados coletados
    df_pred = pd.DataFrame(dados_pred)
    print(f' -> {len(pastas_ignoradas)} pasta(s) ignorada(s)')
    print(f' -> {len(df_pred)} sismo(s) encontrados')

    return df_pred, df_erros


# ------------------------------ MAIN -----------------------------------------
if __name__ == '__main__':
    df_pred, df_erros = constroi_dados_pred()
    # Salva os erros de pastas ignoradas em um csv
    df_erros.to_csv('./files/erros.csv', index=False)
    # Salvando o DataFrame em um arquivo CSV
    df_pred.to_csv('./files/pred.csv', index=False)
