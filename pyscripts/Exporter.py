# -*- coding: utf-8 -*-
# Python 3.10
# ./Classificador_Sismologico/pyscripts/Exporter.py


# ----------------------------  DESCRIPTION  -----------------------------------
# Script para processar dados sismicos
# Autor: Gabriel Góes Rocha de Lima (adaptado de Bianchi)
# Original: fdsnwscsv.py (por Bianchi)
# Funções de utilidade para Processar_Dados_Sismicos.py
# Versão: 0.1
# Data: 2024-02-27
# Ultima modificação: 2024-03-05


# ---------------------------- IMPORTS ----------------------------------------
import sys
import utm


# ---------------------------- CLASSES ----------------------------------------
# Classe Exporter
class Exporter(object):
    def __init__(self, sep=";", where=sys.stderr):
        self._ = False
        if isinstance(where, str):
            where = open(where, "w")
            self._iopen = True
        self._where = where
        self._gotheader = False
        self._sep = sep
        self.fformat = "{:8.4f}"

    def __enter__(self):
        if self._iopen:
            print(" -> Writing to file: {}".format(self._where.name))
        return self

    def __exit__(self, type, value, tb):
        if self._iopen:
            print(" -> Closing file {}.".format(self._where.name))
            self._where.close()

    def translate(self, evtype):
        evlist = {
            'earthquake': 'E',
            'quarry blast': 'Q',
            'induced or triggered event': 'I'
        }
        if evtype not in evlist:
            # Alterei None para esta string
            return 'Not defined in the list'
        return evlist[evtype]

    def flushheader(self):
        if self._gotheader:
            return
        headers = ['ID', 'Hora de Origem (UTC)', 'Longitude', 'Latitude',
                   'UTM X', 'UTM Y', 'MLv', 'Energia', 'Cat']
        headersu = ['', '', '(°)', '(°)', '(m)', '(m)', '', '(J)', '']
        print(self._sep.join(headers), file=self._where)
        print(self._sep.join(headersu), file=self._where)
        self._gotheader = True

    def feed(self, e, o, m, network_id):
        if e.event_type not in ['earthquake', 'quarry blast',
                                'induced or triggered event']:
            print("Event type not supported: {}".format(e.event_type))
            return False
        self.flushheader()
        data = []
        if e.resource_id.id.split("/")[-1].split("_")[0] == ID or\
                e.resource_id.id.split("/")[-1].split("z")[0] == 'gf' or\
                e.resource_id.id.split("/")[-1][:3] == 'usp':
            # Id
            data.append(e.resource_id.id.split("/")[-1])
            # Origin Time
            t = e.preferred_origin().time
            data.append(t.strftime("%Y-%m-%dT%H:%M:%S"))
            # Coords
            data.append(self.fformat.format(o.longitude))
            data.append(self.fformat.format(o.latitude))
            # UTM
            if o.latitude <= 84 and o.latitude >= -84:
                (ux, uy, _, _) = utm.from_latlon(o.latitude, o.longitude)
                data.append("{}".format(ux))
                data.append("{}".format(uy))
            else:
                data.extend([None, None])
            # Magnitude
            try:
                data.append("{:3.1f}".format(m.mag))
            except AttributeError:
                print("Event has no magnitude --- {}".format(e.resource_id.id))
                return False
            E = 10 ** (9.9 + 1.9 * m.mag - 0.0024 * m.mag ** 2) / 1.0E7
            data.append("{:g}".format(E))
            data.append(self.translate(e.event_type))
            print(self._sep.join(map(str, data)), file=self._where)
            return True
