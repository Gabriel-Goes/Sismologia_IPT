from pyrocko.snuffling import Snuffling, Param, Switch, Choice
import os
import pandas as pd

class SeletorEventoSnuffling(Snuffling):
    def setup(self):
        self.set_name('Seletor de Eventos, Redes e Estações')
        self.add_parameter(Param('Limiar de Prob. Natural', 'prob_nat_limiar', 0.5, 0, 1))
        self.add_parameter(Switch('Alta Probabilidade', 'alta_probabilidade', False))
        self.projeto_dir = os.environ['HOME'] + '/projetos/ClassificadorSismologico'
        self.files_path = os.path.join(self.projeto_dir, 'files/output/non_commercial')
        self.df = pd.read_csv(os.path.join(self.files_path, "validation_network_level.csv"))

        eventos = self.df.sort_values(by='prob_nat', ascending=False)['event'].unique()
        if eventos.size > 0:
            self.add_parameter(Choice('Escolha o Evento', 'evento_selecionado', eventos[0], eventos))
        else:
            self.log('Nenhum evento encontrado no arquivo CSV.')


    def call(self):
        # Aplicar filtro se 'alta_probabilidade' estiver marcado
        if self.alta_probabilidade:
            self.df = self.df[self.df['prob_nat'] > self.prob_nat_limiar]

        df_selecionado = self.df[self.df['event'] == self.evento_selecionado]
        # Log de informações do evento selecionado
        for _, row in df_selecionado.iterrows():
            self.log(f"Evento: {row['event']}, Probabilidade: {row['prob_nat']}")

        # Carregar automaticamente arquivos mseed para o evento filtrado
        mseed_path = self._find_mseed_for_event(self.evento_selecionado)
        if mseed_path:
            self._load_mseed(mseed_path)


    def _find_mseed_for_event(self, event):
        mseed_dir = os.path.join(self.files_path, 'mseed')
        for file_name in os.listdir(mseed_dir):
            if event in file_name:
                return os.path.join(mseed_dir, file_name)
        return None

    def _load_mseed(self, mseed_path):
        # Carrega o arquivo mseed no Snuffler
        self.pile_viewer().load_pile(mseed_path)

def __snufflings__():
    return [SeletorEventoSnuffling()]
