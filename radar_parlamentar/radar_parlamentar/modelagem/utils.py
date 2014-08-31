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
             Note: beginning of each term is always on January 1st
        """
        if esfera == MUNICIPAL:
            return self._get_mandatos(ini_date, end_date, 2009)
        elif esfera in [ESTADUAL, FEDERAL]:
            return self._get_mandatos(ini_date, end_date, 2011)

    def _get_mandatos(self, ini_date, end_date, ano_inicio_de_algum_mandato):
        ANO_DE_REFERENCIA = ano_inicio_de_algum_mandato - \
            4 * 500  # suficientemente no passado
        defasagem = (abs(ANO_DE_REFERENCIA - ini_date.year)) % 4
        y = ini_date.year - defasagem
        mandatos = []
        while y <= end_date.year:
            date_ini_mandato = datetime.date(y, 1, 1)
            mandatos.append(date_ini_mandato)
            y += 4
        return mandatos


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
         1) Periods annual, biennial and quadrennial always begin on January 1.
             Six-month period begins on January 1 or July 1.
             Bimonthly period begins on the first day of the initial month of the period.
         2) The beginning of the first period with a beginning always coincidi
             a mandate. Thus, it is guaranteed that each period is
             entirely within one term. Municipal mandates are groups
             4 years starting in 2009 + 4 * i, i \ in Z
             Federal / state mandates are groups of four years beginning
             in 2011 * 4 + i, i \ in Z
             WARNING: Brazil dependent code!
    """

    def __init__(self, casa_legislativa, periodicidade,
                 data_da_primeira_votacao=None, data_da_ultima_votacao=None,
                 numero_minimo_de_votacoes=1):
        self.casa_legislativa = casa_legislativa
        self.periodicidade = periodicidade
        self.data_da_primeira_votacao = data_da_primeira_votacao
        self.data_da_ultima_votacao = data_da_ultima_votacao
        self.numero_minimo_de_votacoes = numero_minimo_de_votacoes

    def get_periodos(self):
        if (self.data_da_primeira_votacao is None):
            # TODO a query abaixo poderia usar um ORDER BY
            votacao_datas = [votacao.data for votacao in Votacao.objects.filter(
                proposicao__casa_legislativa=self.casa_legislativa)]
            if not votacao_datas:
                return []
            self.data_da_primeira_votacao = min(votacao_datas)
            self.data_da_ultima_votacao = max(votacao_datas)
        data_inicial = self._inicio_primeiro_periodo()
        periodos_candidatos = []
        while data_inicial < self.data_da_ultima_votacao:
            data_inicial_prox_periodo = self._data_inicio_prox_periodo(
                data_inicial)
            data_final = data_inicial_prox_periodo - datetime.timedelta(days=1)
            quantidade_votacoes = self.casa_legislativa.num_votacao(
                data_inicial, data_final)
            periodo = PeriodoCasaLegislativa(
                data_inicial, data_final, quantidade_votacoes)
            periodos_candidatos.append(periodo)
            data_inicial = data_inicial_prox_periodo
        periodos_aceitos = self._filtra_periodos_com_minimo_de_votos(
            periodos_candidatos)
        return periodos_aceitos

    def _filtra_periodos_com_minimo_de_votos(self, periodos_candidatos):
        return [p for p in periodos_candidatos
                if p.quantidade_votacoes >= self.numero_minimo_de_votacoes]

    def _inicio_primeiro_periodo(self):
        # TODO extrair e fazer teste de unidade só pra esse método
        # day
        dia_inicial = 1
        # month
        if self.periodicidade == MES:
            mes_inicial = self.data_da_primeira_votacao.month
        elif self.periodicidade in [ANO, BIENIO, QUADRIENIO]:
            mes_inicial = 1
        elif self.periodicidade == SEMESTRE:
            primeiro_de_julho = datetime.date(
                self.data_da_primeira_votacao.year, 7, 1)
            if (self.data_da_primeira_votacao < primeiro_de_julho):
                mes_inicial = 1
            else:
                mes_inicial = 7
        # year
        mandatos_lists = MandatoLists()
        esfera = self.casa_legislativa.esfera
        mandatos = mandatos_lists.get_mandatos(
            esfera, self.data_da_primeira_votacao, self.data_da_ultima_votacao)
        i = 0
        while i < len(mandatos) and mandatos[i] < self.data_da_primeira_votacao:
            ano_inicial = mandatos[i].year
            i += 1
        inicio_primeiro_periodo = datetime.date(
            ano_inicial, mes_inicial, dia_inicial)
        return inicio_primeiro_periodo

    def _data_inicio_prox_periodo(self, data_inicio_periodo):
        # TODO tb extrair e fazer testes
        # day
        dia_inicial = 1
        # month
        if self.periodicidade == MES:
            mes_inicial = data_inicio_periodo.month + 1
            if mes_inicial == 13:
                mes_inicial = 1
        elif self.periodicidade in [ANO, BIENIO, QUADRIENIO]:
            mes_inicial = 1
        elif self.periodicidade == SEMESTRE:
            if data_inicio_periodo.month == 1:
                mes_inicial = 7
            elif data_inicio_periodo.month == 7:
                mes_inicial = 1
        # year
        if self.periodicidade == MES:
            if data_inicio_periodo.month < 12:
                ano_inicial = data_inicio_periodo.year
            else:
                ano_inicial = data_inicio_periodo.year + 1
        elif self.periodicidade == SEMESTRE:
            if data_inicio_periodo.month < 7:
                ano_inicial = data_inicio_periodo.year
            else:
                ano_inicial = data_inicio_periodo.year + 1
        elif self.periodicidade == ANO:
            ano_inicial = data_inicio_periodo.year + 1
        elif self.periodicidade == BIENIO:
            ano_inicial = data_inicio_periodo.year + 2
        elif self.periodicidade == QUADRIENIO:
            ano_inicial = data_inicio_periodo.year + 4
        inicio_prox_periodo = datetime.date(
            ano_inicial, mes_inicial, dia_inicial)
        return inicio_prox_periodo


class StringUtils():

    @staticmethod
    def transforma_texto_em_lista_de_string(texto):
        lista_de_string = []
        if texto is not None and texto != "":
            lista_de_string = texto.split(", ")
        return lista_de_string
