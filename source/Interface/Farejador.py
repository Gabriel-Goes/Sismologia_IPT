import sys

import os
import re

import pandas as pd

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtCore import Qt

from Core.utils import delimt

sys.path.append('/home/ipt/projetos/Classificador_Sismologico/source/')


# -------------------------------- Classe SeletorEventoApp ------------------- #
class SeletorEventoApp(QMainWindow):
    def __init__(self):
        print(' ---------------- Iniciando SeletorEventoApp ---------------- ')
        super().__init__()
        self.setWindowTitle('Seletor de Eventos, Redes e Estações')
        self.setGeometry(50, 50, 200, 150)
        self.files_path = '/home/ipt/projetos/Classificador_Sismologico/files/'
        self.df = pd.read_csv(self.files_path + "output/non_commercial/validation_network_level.csv")
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.titulo = QLabel('Seletor de Eventos')
        self.titulo.setAlignment(Qt.AlignCenter)
        self.titulo.setStyleSheet('font-size: 18px')
        self.titulo.setStyleSheet('font-weight: bold')
        self.layout.addWidget(self.titulo)
        self.eventos_cre, self.eventos_dec, self.numb_eventos = self.get_EventsSorted()
        self.initUI()
        print(' ---------------- SeletorEventoApp Iniciado ---------------- ')

    def initUI(self):
        self.eventSelector = QComboBox()
        self.networkSelector = QComboBox()
        self.stationSelector = QComboBox()
        # Popula os ComboBox com dados iniciais
        self.updateEventSelector(Qt.Checked)
        self.updateNetworkAndStationSelectors()
        self.numb_Eventos = QLabel(f'Número de Eventos: {self.numb_eventos}')
        self.layout.addWidget(self.numb_Eventos)
        # Adiciona os widgets ao layout
        self.layout.addWidget(QLabel('Evento:'))
        self.layout.addWidget(self.eventSelector)
        self.layout.addWidget(QLabel('Rede:'))
        self.layout.addWidget(self.networkSelector)
        self.layout.addWidget(QLabel('Estação:'))
        self.layout.addWidget(self.stationSelector)
        # Conecta os sinais dos selectors às funções de atualização
        self.eventSelector.currentIndexChanged.connect(self.updateNetworkAndStationSelectors)
        # Botão para imprimir o mseed selecionado
        self.loadButton = QPushButton('Carregar mseed')
        self.loadButton.clicked.connect(self.loadMseed)
        self.layout.addWidget(self.loadButton)
        # Add output text to show the selected mseed,
        self.mseedText = QLabel('Mseed selecionado: ')
        self.layout.addWidget(self.mseedText)
        self.eventText = QLabel('Evento: ')
        self.layout.addWidget(self.eventText)
        # Add output text to show the predicted of the selected event
        self.predText = QLabel('Predição: ')
        self.layout.addWidget(self.predText)
        # Add output text to show the label of the selected event
        self.labelText = QLabel('Rótulo: ')
        self.layout.addWidget(self.labelText)
        # Output text prob natural of selected event
        self.probNatText = QLabel('Prob. Natural: ')
        self.layout.addWidget(self.probNatText)
        # Checkbox para ativar ou desativar seleção automática de mseed
        self.autoselectCheckbox = QCheckBox('Seleção automática')
        self.layout.addWidget(self.autoselectCheckbox)
        self.autoselectCheckbox.stateChanged.connect(self.updateAutoSelection)
        # Checkbox para inverter ordem de eventos
        self.invertCheckbox = QCheckBox('Alta Probabilidade')
        self.layout.addWidget(self.invertCheckbox)
        self.invertCheckbox.stateChanged.connect(self.updateEventSelector)

    def updateAutoSelection(self, state):
        if state == Qt.Checked:
            self.eventSelector.currentIndexChanged.connect(self.loadMseed)
            self.networkSelector.currentIndexChanged.connect(self.loadMseed)
            self.stationSelector.currentIndexChanged.connect(self.loadMseed)
        else:
            self.eventSelector.currentIndexChanged.disconnect(self.loadMseed)
            self.networkSelector.currentIndexChanged.disconnect(self.loadMseed)
            self.stationSelector.currentIndexChanged.disconnect(self.loadMseed)

    # Create a list of events sorted crescent or decrescent by prob_nat and save
    # it to use in the eventSelector
    def get_EventsSorted(self):
        eventos = self.df['event'].unique()
        self.numb_eventos = len(eventos)
        self.eventos_cre = sorted(eventos, key=lambda x:
                                  self.df.loc[self.df['event'] == x, 'prob_nat'].iloc[0])
        # eventos_descescente é eventos_crescente invertido
        self.eventos_dec = self.eventos_cre[::-1]
        print(' ---------------- Eventos ordenados ---------------- ')
        print(delimt)
        return self.eventos_cre, self.eventos_dec, self.numb_eventos

    def updateEventSelector(self, state):
        if state == Qt.Checked:
            self.eventSelector.clear()
            self.eventSelector.addItems(self.eventos_dec)
        else:
            self.eventSelector.addItems(self.eventos_cre)

    def updateNetworkAndStationSelectors(self):
        self.networkSelector.clear()
        self.stationSelector.clear()
        selected_event = self.eventSelector.currentText()
        event_folder = os.path.join(self.files_path, 'mseed', selected_event)
        networks, stations = self.getNetworksAndStationsFromEventFolder(event_folder)
        self.networkSelector.addItems(sorted(networks))
        self.stationSelector.addItems(sorted(stations))

    def getNetworksAndStationsFromEventFolder(self, event_folder):
        files = os.listdir(event_folder)
        networks = set()
        stations = set()
        for file in files:
            if file.endswith('.mseed'):
                match = re.match(r'(\w+)_(\w+)_(\w+).mseed', file)
                if match:
                    network, station, _ = match.groups()
                    networks.add(network)
                    stations.add(station)
        return list(networks), list(stations)

    # Botão para imprimir o mseed selecionado
    def loadMseed(self):
        event = self.eventSelector.currentText()
        network = self.networkSelector.currentText()
        station = self.stationSelector.currentText()
        mseed = f'{network}_{station}_{event}'
        self.mseedText.setText(f'Arquivo: {mseed}')
        self.eventText.setText(f'Evento: {event}')
        selected_event = self.eventSelector.currentText()
        filtered_df = self.df.loc[self.df['event'] == selected_event, 'pred']
        if not filtered_df.empty:
            prediction = filtered_df.iloc[0]
        else:
            # Lidar com o caso de não encontrar o evento
            prediction = 'Evento não encontrado ou sem predição'
        label = self.df.loc[self.df['event'] == selected_event, 'label_cat'].iloc[0]
        prob_nat = self.df.loc[self.df['event'] == selected_event, 'prob_nat'].iloc[0]
        codigos = {0: 'Natural',
                   1: 'Antropogênico'}
        # Predições: 0 - Natural, 1 - Antropogênico
        predito = codigos[prediction]
        if prediction not in codigos:
            label = f'filtered_df é vazio: {prediction}'
        if prediction != label:
            # Texto em bold e vermelho
            self.predText.setStyleSheet('font-weight: bold')
            self.predText.setStyleSheet('color: red')
        else:
            # Texto em bold e verde
            self.predText.setStyleSheet('color: black')
        self.predText.setText(f'Predição: {predito}')
        # Rótulos: 0 - Natural, 1 - Antropogênico
        rotulo = codigos[label]
        if label not in codigos:
            rotulo = f'Não classificado: {label}'
        self.labelText.setText(f'Rótulo: {rotulo}')
        self.probNatText.setText(f'Prob. Natural: {prob_nat}')


# --------------------------------- Função main ------------------------------ #
def main():
    app = QApplication(sys.argv)
    ex = SeletorEventoApp()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
