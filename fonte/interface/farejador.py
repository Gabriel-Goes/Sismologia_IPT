import sys
import subprocess
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

from nucleo.utils import DELIMT


class SeletorEventoApp(QMainWindow):
    def __init__(self):
        print(' ---------------- Iniciando SeletorEventoApp ---------------- ')
        super().__init__()
        self.setWindowTitle('Seletor de Eventos, Redes e Estações')
        self.setGeometry(50, 50, 400, 300)

        self.df = pd.read_csv("arquivos/resultados/ncomercial/df_nc_pos.csv")
        print(self.df.columns)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.titulo = QLabel('Seletor de Eventos')
        self.titulo.setAlignment(Qt.AlignCenter)
        self.titulo.setStyleSheet('font-size: 18px; font-weight: bold')
        self.layout.addWidget(self.titulo)

        ev = self.get_EventsSorted()
        self.eventos_cre, self.eventos_dec, self.numb_eventos = ev

        self.initUI()
        print(' ---------------- SeletorEventoApp Iniciado ---------------- ')

    def initUI(self):
        self.eventSelector = QComboBox()
        self.networkSelector = QComboBox()
        self.stationSelector = QComboBox()

        self.numb_Eventos = QLabel(f'Número de Eventos: {self.numb_eventos}')
        self.layout.addWidget(self.numb_Eventos)
        self.layout.addWidget(QLabel('Evento:'))
        self.layout.addWidget(self.eventSelector)
        self.layout.addWidget(QLabel('Rede:'))
        self.layout.addWidget(self.networkSelector)
        self.layout.addWidget(QLabel('Estação:'))
        self.layout.addWidget(self.stationSelector)

        self.eventSelector.currentIndexChanged.connect(self.updateNetworkAndStationSelectors)
        self.networkSelector.currentIndexChanged.connect(self.updateStationSelector)
        self.stationSelector.currentIndexChanged.connect(self.updateMseedAttributes)

        self.loadButton = QPushButton('Carregar mseed')
        self.loadButton.clicked.connect(self.loadMseed)
        self.layout.addWidget(self.loadButton)

        self.mseedText = QLabel('Mseed selecionado: ')
        self.layout.addWidget(self.mseedText)
        self.eventText = QLabel('Evento: ')
        self.layout.addWidget(self.eventText)
        self.predText = QLabel('Predição: ')
        self.layout.addWidget(self.predText)
        self.labelText = QLabel('Rótulo: ')
        self.layout.addWidget(self.labelText)
        self.probNatText = QLabel('Prob. Natural: ')
        self.layout.addWidget(self.probNatText)
        self.distanceText = QLabel('Distância: ')
        self.layout.addWidget(self.distanceText)

        self.autoselectCheckbox = QCheckBox('Seleção automática')
        self.layout.addWidget(self.autoselectCheckbox)
        self.autoselectCheckbox.stateChanged.connect(self.updateAutoSelection)

        self.invertCheckbox = QCheckBox('Alta Probabilidade')
        self.layout.addWidget(self.invertCheckbox)
        self.invertCheckbox.stateChanged.connect(self.updateEventSelector)

        self.updateEventSelector(Qt.Checked)
        self.updateNetworkAndStationSelectors()

    def updateAutoSelection(self, state):
        if state == Qt.Checked:
            self.eventSelector.currentIndexChanged.connect(self.loadMseed)
            self.networkSelector.currentIndexChanged.connect(self.loadMseed)
            self.stationSelector.currentIndexChanged.connect(self.loadMseed)
        else:
            self.eventSelector.currentIndexChanged.disconnect(self.loadMseed)
            self.networkSelector.currentIndexChanged.disconnect(self.loadMseed)
            self.stationSelector.currentIndexChanged.disconnect(self.loadMseed)

    def get_EventsSorted(self):
        eventos = self.df['Event'].unique()
        numb_eventos = len(eventos)
        eventos_cre = sorted(
            eventos, key=lambda x: self.df.loc[self.df['Event'] == x, 'prob_nat'].iloc[0]
        )
        eventos_dec = eventos_cre[::-1]
        print(' ---------------- Eventos ordenados ---------------- ')
        print(DELIMT)
        return eventos_cre, eventos_dec, numb_eventos

    def updateEventSelector(self, state):
        self.eventSelector.clear()
        if state == Qt.Checked:
            self.eventSelector.addItems(self.eventos_dec)
        else:
            self.eventSelector.addItems(self.eventos_cre)

    def updateNetworkAndStationSelectors(self):
        self.networkSelector.clear()
        self.stationSelector.clear()
        selected_event = self.eventSelector.currentText()
        event_folder = os.path.join('arquivos/mseed', selected_event)
        networks, stations = self.getNetworksAndStationsFromEventFolder(event_folder)
        self.networkSelector.addItems(sorted(networks))
        self.updateStationSelector()

    def updateStationSelector(self):
        self.stationSelector.clear()
        selected_event = self.eventSelector.currentText()
        selected_network = self.networkSelector.currentText()
        event_folder = os.path.join('arquivos/mseed', selected_event)
        _, stations = self.getNetworksAndStationsFromEventFolder(event_folder, selected_network)
        self.stationSelector.addItems(sorted(stations))
        self.updateMseedAttributes()

    def getNetworksAndStationsFromEventFolder(self, event_folder, filter_network=None):
        arquivos = os.listdir(event_folder)
        networks = set()
        stations = set()
        for file in arquivos:
            if file.endswith('.mseed'):
                match = re.match(r'(\w+)_(\w+)_(\w+).mseed', file)
                if match:
                    network, station, _ = match.groups()
                    if not filter_network or filter_network == network:
                        networks.add(network)
                        stations.add(station)
        return list(networks), list(stations)

    def updateMseedAttributes(self):
        event = self.eventSelector.currentText()
        network = self.networkSelector.currentText()
        station = self.stationSelector.currentText()
        mseed = f'{network}_{station}_{event}'
        self.mseedText.setText(f'Arquivo: {mseed}')
        self.eventText.setText(f'Evento: {event}')
        self.mseed_file_path = os.path.join('arquivos/mseed', event, f'{network}_{station}_{event}.mseed')

        filtered_df = self.df.loc[self.df['Event'] == event]
        if not filtered_df.empty:
            prediction = filtered_df['pred'].iloc[0]
        else:
            prediction = 'Evento não encontrado ou sem predição'

        label = filtered_df['label_cat'].iloc[0] if not filtered_df.empty else 'N/A'
        prob_nat = filtered_df['prob_nat'].iloc[0] if not filtered_df.empty else 'N/A'
        codigos = {0: 'Natural', 1: 'Antropogênico'}

        predito = codigos.get(prediction, 'Desconhecido')
        if prediction != label:
            self.predText.setStyleSheet('font-weight: bold; color: red')
        else:
            self.predText.setStyleSheet('color: black')

        self.predText.setText(f'Predição: {predito}')
        rotulo = codigos.get(label, 'Não classificado')
        self.labelText.setText(f'Rótulo: {rotulo}')
        self.probNatText.setText(f'Prob. Natural: {prob_nat}')

        distancia = filtered_df['Distance'].iloc[0] if not filtered_df.empty else 'N/A'
        self.distanceText.setText(f'Distância: {distancia}')

    def loadMseed(self):
        try:
            if not os.path.isfile(self.mseed_file_path):
                raise FileNotFoundError
            subprocess.Popen(['snuffler', self.mseed_file_path])
            print(f"Snuffler iniciado com {self.mseed_file_path}")
        except FileNotFoundError:
            print(f"Erro: Arquivo {self.mseed_file_path} não encontrado.")
        except Exception as e:
            print(f"Erro ao iniciar o Snuffler: {e}")


def main():
    app = QApplication(sys.argv)
    ex = SeletorEventoApp()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
