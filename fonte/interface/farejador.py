#
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# --------------------------------- Farejador ---------------------------------
# Autor: Gabriel Góes Rocha de Lima
# Universidade de São Paulo - Instituto de Geociências

# ------------------------------- Descrição ----------------------------------


# --------------------------------- Imports ---------------------------------
import sys
import subprocess
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from PIL import Image
from PIL import ImageOps
from PIL import ImageDraw

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtCore import Qt


# ---------------------------- SeletorEventoApp ------------------------------
class SeletorEventoApp(QMainWindow):
    def __init__(self):
        print(' ---------------- Iniciando SeletorEventoApp ---------------- ')
        super().__init__()
        self.setWindowTitle('Seletor de Eventos, Redes e Estações')
        self.setGeometry(50, 50, 400, 300)

        self.df = pd.read_csv("arquivos/resultados/predito.csv")
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

        self.numb_Eventos = QLabel(f'# Eventos: {self.numb_eventos}')
        self.layout.addWidget(self.numb_Eventos)

        self.layout.addWidget(QLabel('Eventos, Rede e Estação:'))

        hbox_ev_net_sta = QHBoxLayout()
        hbox_ev_net_sta.addWidget(QLabel('Evento:'))
        hbox_ev_net_sta.addWidget(self.eventSelector)
        hbox_ev_net_sta.addWidget(QLabel('Rede:'))
        hbox_ev_net_sta.addWidget(self.networkSelector)
        hbox_ev_net_sta.addWidget(QLabel('Estação:'))
        hbox_ev_net_sta.addWidget(self.stationSelector)
        self.layout.addLayout(hbox_ev_net_sta)

        self.hbox_event_labels = QHBoxLayout()
        self.nb_picksText = QLabel('#Picks: ')
        self.hbox_event_labels.addWidget(self.nb_picksText)
        self.ev_predText = QLabel('Predição: ')
        self.hbox_event_labels.addWidget(self.ev_predText)
        self.probNatText = QLabel('Probabilidade: ')
        self.hbox_event_labels.addWidget(self.probNatText)
        self.layout.addLayout(self.hbox_event_labels)

        # self.layout.addWidget(QLabel('Rede:'))
        # self.layout.addWidget(self.networkSelector)
        # self.layout.addWidget(QLabel('Estação:'))
        # self.layout.addWidget(self.stationSelector)

        self.distanceText = QLabel('Distância: ')
        self.layout.addWidget(self.distanceText)
        self.stPredText = QLabel('Pred. (pick): ')
        self.layout.addWidget(self.stPredText)
        self.stProbText = QLabel('Prob. (pick): ')
        self.layout.addWidget(self.stProbText)

        self.eventSelector.currentIndexChanged.connect(self.updateNetworkAndStationSelectors)
        self.networkSelector.currentIndexChanged.connect(self.updateStationSelector)
        self.stationSelector.currentIndexChanged.connect(self.updateMseedAttributes)

        self.loadButton = QPushButton('Farejar')
        self.loadButton.clicked.connect(self.loadMseed)
        self.layout.addWidget(self.loadButton)

        self.spectreButton = QPushButton('Espectrograma')
        self.spectreButton.clicked.connect(self.loadSpectre)
        self.layout.addWidget(self.spectreButton)

        self.mseedText = QLabel('Mseed selecionado: ')
        self.layout.addWidget(self.mseedText)
        self.eventText = QLabel('Evento: ')
        self.layout.addWidget(self.eventText)

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
            eventos, key=lambda x: self.df.loc[
                self.df['Event'] == x,
                'Event Prob_Nat'
            ].iloc[0]
        )
        eventos_dec = eventos_cre[::-1]
        print(' ---------------- Eventos ordenados ---------------- ')
        print('_____________________________________________________')
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

    def getNetworksAndStationsFromEventFolder(
            self,
            event_folder,
            filter_network=None
            ):
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
        ev = self.eventSelector.currentText()
        net = self.networkSelector.currentText()
        sta = self.stationSelector.currentText()
        mseed = f'{net}_{sta}_{ev}'
        self.mseedText.setText(f'Arquivo: {mseed}')
        self.eventText.setText(f'Evento: {ev}')
        self.mseed_file_path = os.path.join(
            'arquivos/mseed', ev, f'{net}_{sta}_{ev}.mseed'
        )

        filtered_df = self.df[(self.df['Event'] == ev) & (self.df['Station'] == sta)]
        nb_picks  = self.df[(self.df['Event'] == ev)].shape[0]

        if not filtered_df.empty:
            ev_prediction = filtered_df['Event Pred_final'].iloc[0]
            ev_prob_nat = filtered_df['Event Prob_Nat'].iloc[0]
            ev_predito = filtered_df['Event Pred_final'].iloc[0]
            distancia = filtered_df['Distance'].iloc[0]
            st_prediction = filtered_df['Pick Pred_final'].iloc[0]
            st_prob_nat = filtered_df['Pick Prob_Nat'].iloc[0]
            rotulo = filtered_df['Cat'].iloc[0]
        else:
            ev_prediction = 'Evento não encontrado ou sem predição'
            ev_prob_nat = 'N/A'
            ev_predito = 'N/A'
            distancia = 'N/A'
            st_prediction = 'N/A'
            st_prob_nat = 'N/A'
            rotulo = 'N/A'

        rotulo  = filtered_df['Cat'].iloc[0] if not filtered_df.empty else 'N/A'
        ev_prob_nat = filtered_df['Event Prob_Nat'].iloc[0] if not filtered_df.empty else 'N/A'
        ev_predito = filtered_df['Event Pred_final'].iloc[0] if not filtered_df.empty else 'N/A'
        label = 'Natural' if rotulo == 'earthquake' else 'Anthropogenic'

        self.nb_picksText.setText(f'#Picks: {nb_picks}')

        if ev_prediction != label:
            self.ev_predText.setStyleSheet('font-weight: bold; color: red')
        else:
            self.ev_predText.setStyleSheet('color: black')

        self.ev_predText.setText(f'Predição: {ev_predito}')
        self.probNatText.setText(f'Prob. Natural: {ev_prob_nat}')
        self.stPredText.setText(f'Predição (pick): {st_prediction}')
        self.stProbText.setText(f'Prob. Natural (pick): {st_prob_nat}')

        if distancia != 'N/A':
            try:
                self.distanceText.setText(f'Distância: {distancia:.1f} km')
            except Exception as e:
                self.distanceText.setText(f'Distância:{e}')
        else:
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

    def loadSpectre(self):
        try:
            if not os.path.isfile(self.mseed_file_path):
                raise FileNotFoundError
            ev = self.eventSelector.currentText()
            net = self.networkSelector.currentText()
            sta = self.stationSelector.currentText()

            npy = f'{net}_{sta}_{ev}.npy'
            path = os.path.join('arquivos/espectro', ev, npy)
            spectrogram = np.load(path, allow_pickle=True)
            spectrogram = np.moveaxis(spectrogram, 0, 2)

            freqs = list(range(1, 51))
            time = list(np.arange(0.5, 59.75, 0.25))
            psd_mat = np.array(spectrogram[:, :, 0])

            if psd_mat.shape != (len(time), len(freqs)):
                print(f"Dimensões do espectrograma inválidas: {psd_mat.shape}")
                return

            psd_mat_normalized = 255 * (psd_mat - psd_mat.min()) / (psd_mat.max() - psd_mat.min())
            psd_mat_normalized = psd_mat_normalized.astype(np.uint8)

            cmap = plt.get_cmap('viridis')
            color_img = cmap(psd_mat_normalized.T)
            color_img = (color_img[:, :, :3] * 255).astype(np.uint8)

            img = Image.fromarray(color_img)
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            img.save(f'arquivos/figuras/espectros/{ev}_{net}_{sta}.png')
            img.show()

            print(f"Spectrogram iniciado com {self.mseed_file_path}")
        except FileNotFoundError:
            print(f"Erro: Arquivo {self.mseed_file_path} não encontrado.")
            os.makedirs('arquivos/figuras/espectros', exist_ok=True)
        except Exception as e:
            print(f"Erro ao iniciar o Spectrogram: {e}")


def main():
    app = QApplication(sys.argv)
    ex = SeletorEventoApp()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
