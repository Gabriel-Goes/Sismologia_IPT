import pandas as pd



# Read mseed file
def get_true_false(validation: str):
    # leitura dos arquivos csv files/output/non_commercial/validation_network_level.csv
    df_val = pd.read_csv('files/output/' + validation)
    print(f' - non_comm_net: {df_val.shape}')

    sismo_natural = df_val[df_val['label_cat'] == 0]
    sismo_antropico = df_val[df_val['label_cat'] == 1]

    print(f' - sismo_natural: {sismo_natural.shape}')
    print(f' - sismo_antropico: {sismo_antropico.shape}')

    return sismo_natural, sismo_antropico


# ----------------- Main -----------------
def main():
    get_true_false('non_commercial/validation_network_level.csv')


if __name__ == '__main__':
    main()
