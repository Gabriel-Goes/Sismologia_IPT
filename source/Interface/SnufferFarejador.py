from pyrocko.snuffling import Snuffling, Param, Switch, Choice
import os
import pandas as pd
from pyrocko import io


class SeletorEventoSnuffling(Snuffling):
    def setup(self):
        self.set_name('Seletor de Eventos, Redes e Estações')
        self.add_parameter(Param('Limiar de Prob. Natural', 'prob_nat_limiar',
                                 0.5, 0, 1))
        self.add_parameter(Switch('Alta Probabilidade', 'alta_probabilidade',
                                  False))
        self.files_path = os.environ['HOME'] +\
            '/projetos/ClassificadorSismologico/files'
        self.df = pd.read_csv(
            self.files_path +
            "/output/non_commercial/validation_network_level.csv")

        eventos = self.df.sort_values(by='prob_nat',
                                      ascending=False)['event'].unique()
        if eventos.size > 0:
            self.add_parameter(Choice('Escolha o Evento',
                                      'evento_selecionado',
                                      eventos[0], eventos))
        else:
            # self.add_message('Nenhum evento encontrado')
            None

    def _find_mseed_for_event(self, event):
        mseed_dir = self.files_path + '/mseed'
        for file_name in os.listdir(mseed_dir):
            if event in file_name:
                return os.path.join(mseed_dir, file_name)
        return None

    def call(self):
        # Aplicar filtro de alta probabilidade se necessário
        if self.alta_probabilidade:
            self.df = self.df[self.df['prob_nat'] > self.prob_nat_limiar]

        df_selecionado = self.df[self.df['event'] == self.evento_selecionado]
        # Registrar informações do evento selecionado
        for _, row in df_selecionado.iterrows():
            # self.add_message(
            # f"Rede: {row['network']} Estação: {row['station']}\
            # Prob. Natural: {row['prob_nat']}")
            None

        mseed_path = self._find_mseed_for_event(self.evento_selecionado)
        if mseed_path:
            traces = io.load(mseed_path)

            for tr in traces:
                self.add_trace(tr)
        else:
            # self.add_message('Arquivo mseed não encontrado')
            None

    def __init__(self):
        Snuffling.__init__(self)


def __snufflings__():
    return [SeletorEventoSnuffling()]
