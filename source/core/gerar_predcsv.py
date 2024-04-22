import pandas as pd


def gerar_predcsv():
    # Criar Lista de Eventos para Predição
    csv_events = './files/events/events.csv'
    df_events = pd.read_csv(csv_events, sep=',')

    # Se IDs iguais possuem Cat diferentes adicionar em uma lista de erros
    erros = []
    for id in df_events['ID'].unique():
        if len(df_events[df_events['ID'] == id]['Cat'].unique()) > 1:
            erros.append(id)

    # Remover IDs com Cat diferentes
    df_events_clean = df_events[~df_events['ID'].isin(erros)]
    df_pred = df_events_clean[['Event', 'Cat']]

    # Transforma 'earthquake' em 0 e qualquer outra coisa em 0
    df_pred['Cat'] = df_pred['Cat'].apply(lambda x: 0 if x == 'earthquake' else 1)

    # rename columns
    df_pred.columns = ['ID', 'Label']

    # Remove os IDs duplicados
    df_pred = df_pred.drop_duplicates()

    # Salvar o DataFrame em um arquivo CSV
    df_pred.to_csv('./files/predcsv/pred.csv', index=False)

    df_erros = pd.DataFrame(erros, columns=['ID'])
    df_erros.to_csv('./files/predcsv/erros.csv', index=False)



# ------------------------------ MAIN -----------------------------------------
if __name__ == '__main__':
    gerar_predcsv()
    print('Pred.csv criado com sucesso')
    print('Erros.csv criado com sucesso')
