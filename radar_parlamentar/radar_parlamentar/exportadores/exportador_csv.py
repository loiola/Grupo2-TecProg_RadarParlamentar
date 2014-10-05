# !/usr/bin/python
# coding=utf8

# Copyright (C) 2013, Leonardo Leite
#
# This file is part of Radar Parlamentar.
#
# Radar Parlamentar is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Radar Parlamentar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Radar Parlamentar.  If not, see <http://www.gnu.org/licenses/>.

""" Export to CSV for our analyzes in R.
    To read the csv file in R: read.csv('votes.csv', sep=',', as.is=T)
    The last argument prevents the strings are imported as "factors"."""

import os
import csv
from modelagem import models
from django.utils.dateparse import parse_datetime
import logging
logger = logging.getLogger("radar")

MODULE_DIR = os.path.abspath(os.path.dirname(__file__))

COALITION_PARTIES = ['PT', 'PCdoB', 'PSB', 'PP', 'PMDB', 'PTB']
# PR, PDT are not coalition?
ROLLCALL = 'rollcall'
VOTER_ID = 'voter_id'
NAME = 'name'
PARTY = 'party'
COALITION = 'coalition'
VOTE = 'vote'

LABELS = [ROLLCALL, VOTER_ID, NAME, PARTY, COALITION, VOTE]

CSV_FILE = 'votes.csv'

class ExportadorCSV:

    def __init__(self, nome_curto_casa_legislativa, data_ini, data_fim):
        self.nome_curto = nome_curto_casa_legislativa
        self.ini = data_ini
        self.fim = data_fim
        self.votacoes = None
        self.csv_rows = []

    # Retrieving, transforming and writing CSV:
    def exportar_csv(self):
        self.retrieve_votacoes()
        self.transform_data()
        self.write_csv()

    def retrieve_votacoes(self):
        legislative_house = models.CasaLegislativa.objects.get(nome_curto=self.nome_curto)

        if self.ini is None and self.fim is None:
            self.votacoes = models.Votacao.objects.filter(
                proposicao__casa_legislativa=legislative_house).order_by('data')
        if self.ini is None and self.fim is not None:
            self.votacoes = models.Votacao.objects.filter(
                proposicao__casa_legislativa=legislative_house
            ).filter(data__lte=self.fim).order_by('data')
        if self.ini is not None and self.fim is None:
            self.votacoes = models.Votacao.objects.filter(
                proposicao__casa_legislativa=legislative_house
            ).filter(data__gte=self.ini).order_by('data')
        if self.ini is not None and self.fim is not None:
            self.votacoes = models.Votacao.objects.filter(
                proposicao__casa_legislativa=legislative_house
            ).filter(data__gte=self.ini, data__lte=self.fim).order_by('data')

    def transform_data(self):
        self.csv_rows.append(LABELS)

        for voting in self.votacoes:
            votes = voting.votos()

            for vote in votes:
                legislature = vote.legislatura
                parliamentary = legislature.parlamentar
                party = legislature.partido
                csv_row = []
                csv_row.append(voting.id_vot)
                csv_row.append(legislature.id)
                csv_row.append(parliamentary.nome.encode('UTF-8'))
                csv_row.append(party.nome)
                csv_row.append(self.coalition(party.nome))

                try:
                    csv_row.append(self.voto(vote.opcao))
                    self.csv_rows.append(csv_row)
                except:
                    print 'Ignorando voto ', vote.opcao
                    logger.info("Ignorando voto: %s" % vote.opcao)

    def coalition(self, nome_partido):
        return '1' if nome_partido in COALITION_PARTIES else '0'

    # Options of votes:
    def voto(self, option):
        if option == models.SIM:
            return 1
        elif option == models.NAO:
            return -1
        elif option == models.ABSTENCAO:
            return 0
        elif option == models.OBSTRUCAO:
            return 0
        elif option == models.AUSENTE:
            return 0
        else:
            raise ValueError()

    # Writing CSV:
    def write_csv(self):
        filepath = os.path.join(MODULE_DIR, 'dados', CSV_FILE)
        with open(filepath, 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(self.csv_rows)


def main():
    initial_date = parse_datetime('2010-06-09 0:0:0')
    finish_date = parse_datetime('2010-06-09 23:59:0')
    exporter = ExportadorCSV('sen', initial_date, finish_date)
    exporter.exportar_csv()
