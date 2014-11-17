# !/usr/bin/python
# coding=utf8

# Copyright (C) 2012, Leonardo Leite, Saulo Trento, Diego Rabatone
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
# TemasTest
# You should have received a copy of the GNU General Public License
# along with Radar Parlamentar.  If not, see <http://www.gnu.org/licenses/>.

"""Chart Module
Responsible for taking care of things related to the presentation of the PrincipalComponentAnalysis
to the end user, since the PrincipalComponentAnalysis calculations have been performed"""

from __future__ import unicode_literals
import json
import logging
from math import sqrt, isnan

# To debug number of query, using
# db.reset_queries() and print len(db.connection.queries)
from django import db 

import time

logger = logging.getLogger("radar")


class JsonAnaliseGenerator:

    def __init__(self, analise_temporal):

        self.CONSTANT_SIZE_SCALE = 120
        self.temporal_analysis = analise_temporal
        self.scale_period = None
        self.json = None
        self.max_parliamentary_radius_calculator = MaxRadiusCalculator()
        self.max_political_party_radius_calculator = MaxRadiusCalculator()
        self.parliamentaries_scaler = GraphScaler()
        self.political_parties_scaler = GraphScaler()
        self.init_radius_calculator()

    def init_radius_calculator(self):

        political_parties_size_by_period = {}
        for ap in self.temporal_analysis.analises_periodo:
            label_periodo = str(ap.periodo)
            political_parties_size_by_period[
                label_periodo] = ap.tamanhos_partidos
        self.raio_partido_calculator = RaioPartidoCalculator(
            political_parties_size_by_period)

    def get_json(self):

        if not self.json:
            logger.info('Gerando json...')
            self.create_json()
            logger.info('json gerado')
        return self.json

    def create_json(self):

        dictionary_analysis = {}
        dictionary_analysis['geral'] = self.create_general_dictionary()
        dictionary_analysis['periodos'] = self.list_periods()
        dictionary_analysis['partidos'] = self.list_political_parties_instrumented()
        dictionary_analysis[
            'max_raio'] = self.max_parliamentary_radius_calculator.max_r()
        dictionary_analysis[
            'max_raio_partidos'] = self.max_political_party_radius_calculator.max_r()
        self.json = json.dumps(dictionary_analysis)

    def create_general_dictionary(self):

        general_dictionary = {}
        general_dictionary['escala_tamanho'] = None
        general_dictionary['filtro_votacoes'] = None
        general_dictionary['CasaLegislativa'] = self.create_legislative_house_dictionary()
        general_dictionary['total_votacoes'] = self.temporal_analysis.total_votacoes
        general_dictionary['palavras_chaves'] = self.temporal_analysis.palavras_chaves
        return general_dictionary

    def create_legislative_house_dictionary(self):

        legislative_house = self.temporal_analysis.casa_legislativa
        legislative_house_dictionary = {}
        legislative_house_dictionary['nome'] = legislative_house.nome
        legislative_house_dictionary['short_name'] = legislative_house.nome_curto
        legislative_house_dictionary['esfera'] = legislative_house.esfera
        legislative_house_dictionary['local'] = legislative_house.local
        legislative_house_dictionary['atualizacao'] = unicode(legislative_house.atualizacao)
        return legislative_house_dictionary

    def list_periods(self):

        list_aps = []
        for ap in self.temporal_analysis.analises_periodo:
            dictionary_political_party_analysis = {}
            eigen0 = ap.pca.eigen[0] if len(
                ap.pca.eigen) > 0 is not None else 0
            eigen1 = ap.pca.eigen[1] if len(
                ap.pca.eigen) > 1 is not None else 0
            var_explicada = round(
                (eigen0 + eigen1) / ap.pca.eigen.sum() * 100, 1)
            dictionary_political_party_analysis['nvotacoes'] = ap.num_votacoes
            dictionary_political_party_analysis['nome'] = ap.periodo.string
            dictionary_political_party_analysis['var_explicada'] = var_explicada
            dictionary_political_party_analysis['cp1'] = self.do_dictionary_composition_1(ap)
            dictionary_political_party_analysis['cp2'] = self.do_dictionary_composition_2(ap)
            dictionary_political_party_analysis['votacoes'] = self.list_votings_in_period(ap)
            list_aps.append(dictionary_political_party_analysis)
        return list_aps

    def do_dictionary_composition_1(self, ap):

        return self.compose_dictionary(ap, 0)

    def do_dictionary_composition_2(self, ap):

        return self.compose_dictionary(ap, 1)

    def compose_dictionary(self, ap, idx):

        """ap: AnalisePeriodo;
           idx == 0 para cp1 and idx == 1 para cp2"""

        dictionary_composition = {}
        try:
            theta = round(ap.theta, 0) % 180 + 90 * idx
        except AttributeError, error:
            logger.error("AttributeError: %s" % error)
            theta = 0
        try:
            var_explicada = round(
                ap.pca.eigen[idx] / ap.pca.eigen.sum() * 100, 1)
            if ap.pca.Vt is not None:
                composicao = [round(el, 2)
                              for el in 100 * ap.pca.Vt[idx, :] ** 2]
                dictionary_composition['composicao'] = composicao
        except IndexError:
            var_explicada = 0
            dictionary_composition['composicao'] = 0
        dictionary_composition['theta'] = theta
        dictionary_composition['var_explicada'] = var_explicada

        # ALL these complex accounts should gave been made by analysis
        # The JsonGenerator should not understand these things.
        return dictionary_composition

    def list_votings_in_period(self, ap):

        list_of_votings = []
        for voting in ap.votacoes:
            dictionary_voting = {}
            dictionary_voting['id'] = unicode(voting).replace('"', "'")
            list_of_votings.append(dictionary_voting)
        return list_of_votings

    def list_political_parties_instrumented(self):

        db.reset_queries()
        print 'comecando lista de partidos'
        ttotal1 = time.time()
        list_political_parties = self.list_political_parties()
        print 'queries para fazer lista de partidos = '
        print str(len(db.connection.queries))
        print 'tempo na lista de partidos = '
        print str(time.time() - ttotal1) + ' s.'
        return list_political_parties

    def list_political_parties(self):

        list_political_parties = []
        political_parties = self.temporal_analysis.casa_legislativa.get_political_parties_from_legislative_house(
        ).select_related('nome', 'numero', 'cor')

        for partido in political_parties:
            list_political_parties.append(self.compose_political_party_dictionary(partido))
        return list_political_parties

    def compose_political_party_dictionary(self, partido):

        political_party_dictionary = {
            "nome": partido.nome, "numero": partido.numero, "cor": partido.cor}
        political_party_dictionary["t"] = []
        political_party_dictionary["r"] = []
        political_party_dictionary["x"] = []
        political_party_dictionary["y"] = []

        for period_analysis in self.temporal_analysis.analises_periodo:
            label_period = str(period_analysis.periodo)
            cache_coords_key = label_period
            coordinates = self.political_parties_scaler.change_x_y_scales(
                period_analysis.coordenadas_partidos, cache_coords_key)
            try:
                x = round(coordinates[partido][0], 2)
                y = round(coordinates[partido][1], 2)
                self.max_political_party_radius_calculator.add_point(x, y)
                if not isnan(x):
                    political_party_dictionary["x"].append(round(x, 2))
                    political_party_dictionary["y"].append(round(y, 2))
                else:
                    political_party_dictionary["x"].append(0.)
                    political_party_dictionary["y"].append(0.)

            except KeyError, error:
                logger.error("KeyError: %s" % error)
                political_party_dictionary["x"].append(0.)
                political_party_dictionary["y"].append(0.)

            size = period_analysis.tamanhos_partidos[partido]
            political_party_dictionary["t"].append(size)

            radius = self.raio_partido_calculator.get_radius(
                partido, label_period)

            political_party_dictionary["r"].append(radius)

        political_party_dictionary["parlamentares"] = []


        legislatures = self.temporal_analysis.casa_legislativa.get_legislatures_from_legislative_house().filter(
            partido=partido).select_related('id', 'localidade', 'partido__nome', 'parlamentar__nome')

        for leg in legislatures:
            political_party_dictionary["parlamentares"].append(self.compose_parliamentary_dictionary(leg))
        return political_party_dictionary

    def compose_parliamentary_dictionary(self, legislatura):

        legislature_id = legislatura.id
        name = legislatura.parlamentar.nome
        location = legislatura.localidade
        parliamentary_dictionary = {
            "nome": name, "id": legislature_id, "localidade": location}
        parliamentary_dictionary["x"] = []
        parliamentary_dictionary["y"] = []

        for period_analysis in self.temporal_analysis.analises_periodo:
            cache_coords_key = str(period_analysis.periodo)
            coordinates = self.parliamentaries_scaler.change_x_y_scales(
                period_analysis.coordenadas_legislaturas, cache_coords_key)
            if coordinates.has_key(legislature_id):
                x = coordinates[legislature_id][0]
                y = coordinates[legislature_id][1]
                self.max_parliamentary_radius_calculator.add_point(x, y)
                if not isnan(x):
                    x = round(x, 2)
                    y = round(y, 2)
                else:
                    x = None
                    y = None
                parliamentary_dictionary["x"].append(x)
                parliamentary_dictionary["y"].append(y)
            else:
                parliamentary_dictionary["x"].append(None)
                parliamentary_dictionary["y"].append(None)
        return parliamentary_dictionary


class MaxRadiusCalculator:
    """Calculate the maximum radius of the chart"""

    def __init__(self):
        self.max_r2 = 0

    def add_point(self, x, y):
        if self._valid(x) and self._valid(y):
            r2 = x ** 2 + y ** 2
            self.max_r2 = max(self.max_r2, r2)

    def _valid(self, value):
        return value is not None and not isnan(value)

    def max_r(self):
        return round(sqrt(self.max_r2), 1)


class GraphScaler:

    def __init__(self):
        self.cache = {}

    def change_x_y_scales(self, coords, cache_key):
        """Changes X,Y scale from [-1,1] to [-100,100]
        coords -- key => [x, y]"""

        if cache_key in self.cache.keys():
            return self.cache[cache_key]
        scaled = self.scalar_coordinates(coords)
        self.cache[cache_key] = scaled

        return scaled

    def scalar_coordinates(self, coords):

        scaled = {}
        for key, coord in coords.items():
            x = coord[0]
            try:
                y = coord[1]
            except IndexError:
                y = 0
            if x < -1 or x > 1 or y < -1 or y > 1:
                raise ValueError("Value should be in [-1,1]")
            scaled[key] = [x * 100, y * 100]
        return scaled


class RaioPartidoCalculator():
    """Defines the party circumference radius in chart"""

    def __init__(self, tamanhos_dos_partidos_por_periodo):
        """Argument:
        tamanhos_dos_partidos_por_periodo:
            string_periodo => (search_political_party => int)
        where string_periodo is a string that represents univocally a period
        generated with str(periodo), where period is from PeriodoCasaLegislativa type"""

        self.CONSTANT_SCALE_SIZE = 120
        self.political_parties_size_by_period = tamanhos_dos_partidos_por_periodo
        self.init_total_area()
        self.scale = self.CONSTANT_SCALE_SIZE ** 2. / \
            max(1, self.total_area)

    def init_total_area(self):

        larger_sum = 0
        for political_parties_size in self.political_parties_size_by_period.values():
            political_parties_size_sum = sum(political_parties_size.values())
            if political_parties_size_sum > larger_sum:
                larger_sum = political_parties_size_sum
        self.total_area = larger_sum

    def get_radius(self, partido, periodo_str):

        political_parties_size = self.political_parties_size_by_period[periodo_str]
        size = political_parties_size[partido]
        radius = sqrt(size * self.scale)
        return round(radius, 1)
