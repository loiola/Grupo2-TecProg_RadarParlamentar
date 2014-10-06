# coding=utf8

# Copyright (C) 2013, Leonardo Leite, Eduardo Hideo
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

from __future__ import unicode_literals
from models import MUNICIPAL, ESTADUAL, FEDERAL, MES
from models import SEMESTRE, ANO, BIENIO, QUADRIENIO
from models import Votacao, PeriodoCasaLegislativa
import datetime


class MandatoLists:

    def get_mandatos(self, esfera, ini_date, end_date):
        """Return dates for the start of each term in the period
             between ini_date and end_date
             arguments:
                 ini_date, end_date - date type
             return:
                 list of type date
             Note: beginning of each term is always on January 1st"""

        if esfera == MUNICIPAL:
            return self._get_mandatos(ini_date, end_date, 2009)
        elif esfera in [ESTADUAL, FEDERAL]:
            return self._get_mandatos(ini_date, end_date, 2011)

    def _get_mandatos(self, ini_date, end_date, ano_inicio_de_algum_mandato):

        # Receives a reference year sufficiently in the past
        past_reference_year = ano_inicio_de_algum_mandato - \
            4 * 500

        # Receives the absolute value of the subtraction of the ini_date.year by
        # ANO_DE_REFERENCIA
        lag = (abs(past_reference_year - ini_date.year)) % 4

        # Receives the value of the subtraction of delay by ini_date.year
        y = ini_date.year - lag

        # Receives a list of mandates with its initial date
        mandates_list = []

        while y <= end_date.year:
            date_ini_mandato = datetime.date(y, 1, 1)
            mandates_list.append(date_ini_mandato)
            y += 4
        return mandates_list


class PeriodosRetriever:

    """Retrieves periods with a minimum of a legislative house polls
         between data_da_primeira_votacao and data_da_ultima_votacao
         arguments:
           casa_legislativa - CasaLegislativa one object.
           periodicity - a constant in PERIODS (ex YEAR PERIOD.).
           data_da_primeira_votacao, data_da_ultima_votacao:
               datetime objects. If not specified,
               uses the entire history of the house.
           numero_minimo_de_votacoes - periods with less votes
           are excluded from the list. Default is 1.
         returns:
             A list of objects of type PeriodoCasaLegislativa.
         Details:
         1) Periods annual, biennial and quadrennial always begin on
         January 1.
             Six-month period begins on January 1 or July 1.
             Bimonthly period begins on the first day of the initial
             month of the period.
         2) The beginning of the first period with a beginning always coincidi
             a mandate. Thus, it is guaranteed that each period is
             entirely within one term. Municipal mandates are groups
             4 years starting in 2009 + 4 * i, i \ in Z
             Federal / state mandates are groups of four years beginning
             in 2011 * 4 + i, i \ in Z
             WARNING: Brazil dependent code!"""

    def __init__(self, casa_legislativa, periodicidade,
                 data_da_primeira_votacao=None, data_da_ultima_votacao=None,
                 numero_minimo_de_votacoes=1):

        # Receives an object from CasaLegislativa
        self.casa_legislativa = casa_legislativa

        # Receives a constant from Periodos
        self.periodicidade = periodicidade

        # Receives the date of first vote in a legislative house
        self.data_da_primeira_votacao = data_da_primeira_votacao

        # Receives the date of last vote in a legislative house
        self.data_da_ultima_votacao = data_da_ultima_votacao

        # Receives the minimum number of votes a period, being default equal to 1
        self.numero_minimo_de_votacoes = numero_minimo_de_votacoes

    def get_periodos(self):
        if (self.data_da_primeira_votacao is None):

            # Receives the object filter (dates) Voting of a legislative house
            voting_dates = [votacao.data for votacao in Votacao.objects.filter(
                proposicao__casa_legislativa=self.casa_legislativa)]

            if not voting_dates:
                return []

            # Receives the date of first vote in a legislative house
            self.data_da_primeira_votacao = min(voting_dates)

            # Receives the date of last vote in a legislative house
            self.data_da_ultima_votacao = max(voting_dates)

        # Receives the result of inicio_primeiro_periodo() method
        initial_date = self._inicio_primeiro_periodo()

        # Receives the result of PeriodoCasaLegislativa method that
        # pass as a parameter initial_date, data_final and quantidade_votacoes
        candidate_period = []

        while initial_date < self.data_da_ultima_votacao:
            initial_date_next_period = self._data_inicio_prox_periodo(
                initial_date)

            # Receives the final date of a period of voting on a legislative house
            data_final = initial_date_next_period - datetime.timedelta(days=1)

            # Receives total number of votes in a given period
            votings_amount = self.casa_legislativa.num_votacao(
                initial_date, data_final)

            # Receives the result of PeriodoCasaLegislativa method, passing
            # as a parameter initial_date, data_final and votings_amount
            period = PeriodoCasaLegislativa(
                initial_date, data_final, votings_amount)

            candidate_period.append(period)

            # Assigns the date of the next period to the start date
            initial_date = initial_date_next_period

        # Receives the result of _filtra_periodo_com_minimo_de_votos() method, that
        # pass as a parameter the list of periodos_candidatos
        accepted_period = self._filtra_periodos_com_minimo_de_votos(candidate_period)

        return accepted_period

    def _filtra_periodos_com_minimo_de_votos(self, periodos_candidatos):

        # min_votes_period: temporary variable loop _filtra_periodos_com_minimo_de_votos()
        # method
        return [min_votes_period for min_votes_period in periodos_candidatos
                if min_votes_period.quantidade_votacoes >=
                self.numero_minimo_de_votacoes]

    def _inicio_primeiro_periodo(self):
        # Is the first day of the month of the date of the initial period
        # Default is 1
        initial_day = 1

        # Month
        if self.periodicidade == MES:

            # Is the month of the date of the initial period of the first vote
            initial_month = self.data_da_primeira_votacao.month

        elif self.periodicidade in [ANO, BIENIO, QUADRIENIO]:
            initial_month = 1
        elif self.periodicidade == SEMESTRE:

            # Receives a date (the year of the date of the first vote with the first
            # day of the month 7)
            july_day_one = datetime.date(
                self.data_da_primeira_votacao.year, 7, 1)

            if (self.data_da_primeira_votacao < july_day_one):
                initial_month = 1
            else:
                initial_month = 7

        # receives mandadoLists() method, which lists the mandates
        mandates_lists = MandatoLists()

        # Receives de spheres of legislative house
        sphere = self.casa_legislativa.esfera

        # Receives the mandates in a sphere by the date of first vote and the day
        # of last vote
        mandates = mandates_lists.get_mandatos(
            sphere, self.data_da_primeira_votacao, self.data_da_ultima_votacao)

        # Temporary variable loop _inicio_primeiro_periodo() method
        i = 0
        while i < len(mandates) and mandates[i] < self.data_da_primeira_votacao:
            initial_year = mandates[i].year
            i += 1

        # Receives the date of the first period with initial_year the initial_month and initial_day
        inicio_primeiro_periodo = datetime.date(
            initial_year, initial_month, initial_day)

        return inicio_primeiro_periodo

    def _data_inicio_prox_periodo(self, data_inicio_periodo):
        # Day
        initial_day = 1

        # Month
        if self.periodicidade == MES:
            initial_month = data_inicio_periodo.month + 1
            if initial_month == 13:
                initial_month = 1
        elif self.periodicidade in [ANO, BIENIO, QUADRIENIO]:
            initial_month = 1
        elif self.periodicidade == SEMESTRE:
            if data_inicio_periodo.month == 1:
                initial_month = 7
            elif data_inicio_periodo.month == 7:
                initial_month = 1
        # Year
        if self.periodicidade == MES:
            if data_inicio_periodo.month < 12:
                initial_year = data_inicio_periodo.year
            else:
                initial_year = data_inicio_periodo.year + 1
        elif self.periodicidade == SEMESTRE:
            if data_inicio_periodo.month < 7:
                initial_year = data_inicio_periodo.year
            else:
                initial_year = data_inicio_periodo.year + 1
        elif self.periodicidade == ANO:
            initial_year = data_inicio_periodo.year + 1
        elif self.periodicidade == BIENIO:
            initial_year = data_inicio_periodo.year + 2
        elif self.periodicidade == QUADRIENIO:
            initial_year = data_inicio_periodo.year + 4

        # Receives the date of the next period with initial_year the initial_month and
        # initial_day
        inicio_prox_periodo = datetime.date(
            initial_year, initial_month, initial_day)

        return inicio_prox_periodo


class StringUtils():
    @staticmethod
    def transforma_texto_em_lista_de_string(texto):

        # Receives a list of strings transforma_texto_em_lista_de_string() method
        string_list = []

        if texto is not None and texto != "":
            string_list = texto.split(", ")
        return string_list
