# !/usr/bin/python
# coding=utf8

# Copyright (C) 2012, 2013, Leonardo Leite, Diego Rabatone, Eduardo Hideo
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
from django.test import TestCase
from importadores import cdep
from importadores.tests.mocks_cdep import mock_obter_proposicao
from importadores.tests.mocks_cdep import mock_listar_proposicoes
from importadores.tests.mocks_cdep import mock_obter_votacoes
from importadores.tests.mocks_cdep import mock_obter_proposicoes_votadas_plenario
from mock import Mock
from modelagem import models

# Constants related to forestry code and the amendment of the constitution.

ID = '17338'
YEAR = '1999'
ACRONYM = 'PL'
NUMBER = '1876'
NAME = 'PL 1876/1999'


PLENARY_ID = '584279'
PLENARY_YEAR = '2013'
PLENARY_ACRONYM = 'REQ'
PLENARY_NUMBER = '8196'

votings_tests = [[('17338', 'PL 1876/1999')]]


class ProposicoesParserTest(TestCase):

    def test_parse(self):

        # Tests if the forest code is in the voted propositions.
        parserVotings = cdep.ProposicoesParser(votings_tests)
        votings = parserVotings.parse()
        forestry_code = {'id': ID, 'sigla': ACRONYM, 'num': NUMBER, 'ano': YEAR}
        self.assertTrue(forestry_code in votings)


class SeparadorDeListaTest(TestCase):

    def test_separate_list(self):

        # Inserting tabs in list: a list is separated into several lists.
        list = [1, 2, 3, 4, 5, 6]

        tab = cdep.SeparadorDeLista(1)
        lists = tab.separa_lista_em_varias_listas(list)
        self.assertEquals(len(lists), 1)
        self.assertEquals(lists[0], list)

        tab = cdep.SeparadorDeLista(2)
        lists = tab.separa_lista_em_varias_listas(list)
        self.assertEquals(len(lists), 2)
        self.assertEquals(lists[0], [1, 2, 3])
        self.assertEquals(lists[1], [4, 5, 6])

        tab = cdep.SeparadorDeLista(3)
        lists = tab.separa_lista_em_varias_listas(list)
        self.assertEquals(len(lists), 3)
        self.assertEquals(lists[0], [1, 2])
        self.assertEquals(lists[1], [3, 4])
        self.assertEquals(lists[2], [5, 6])

    def test_separate_list_when_it_is_not_multiple(self):

        list = [1, 2, 3, 4, 5, 6, 7]

        tab = cdep.SeparadorDeLista(3)
        lists = tab.separa_lista_em_varias_listas(list)
        self.assertEquals(len(lists), 3)
        self.assertEquals(lists[0], [1, 2, 3])
        self.assertEquals(lists[1], [4, 5, 6])
        self.assertEquals(lists[2], [7])


class CamaraTest(TestCase):

    @classmethod
    def setUpClass(cls):

        # Iporting just the votings of proposition in 'votadas_test.txt'.
        parserVotings = cdep.ProposicoesParser(votings_tests)
        votings = parserVotings.parse()
        importer = cdep.ImportadorCamara(votings)

        camaraWebService = cdep.Camaraws()
        camaraWebService.listar_proposicoes = Mock(side_effect=mock_listar_proposicoes)
        camaraWebService.obter_proposicao_por_id = Mock(
            side_effect=mock_obter_proposicao)
        camaraWebService.obter_votacoes = Mock(side_effect=mock_obter_votacoes)
        importer.importar(camaraWebService)

    @classmethod
    def tearDownClass(cls):

        from util_test import flush_db
        flush_db(cls)

    def test_legislative_house(self):
        """Certifying the short name "cdep" refers to name "Camara dos 
        Deputados."""

        chamber_of_deputies = models.CasaLegislativa.objects.get(nome_curto='cdep')
        self.assertEquals(chamber_of_deputies.nome, 'Câmara dos Deputados')

    def test_forest_code_propositions(self):
        """Certifying if the date (day, month and year) and situation of 
        forest code is correct."""

        parserVotings = cdep.ProposicoesParser(votings_tests)
        votings = parserVotings.parse()
        importer = cdep.ImportadorCamara(votings)
        data = importer.converte_data('19/10/1999')
        forest_code_proposition = models.Proposicao.objects.get(id_prop=ID)
        self.assertEquals(forest_code_proposition.nome(), NAME)
        self.assertEquals(
            forest_code_proposition.situacao,
            'Tranformada no(a) Lei Ordinária 12651/2012')
        self.assertEquals(forest_code_proposition.data_apresentacao.day, data.day)
        self.assertEquals(forest_code_proposition.data_apresentacao.month, data.month)
        self.assertEquals(forest_code_proposition.data_apresentacao.year, data.year)

    def test_forest_code_votings(self):
        """Checks if the description of voting is the same, besides it tests 
        if date (day, month and year) of the voting is correct."""

        votings = models.Votacao.objects.filter(proposicao__id_prop=ID)
        self.assertEquals(len(votings), 5)

        vote = votings[0]
        self.assertTrue('REQUERIMENTO DE RETIRADA DE PAUTA' in vote.descricao)

        importer = cdep.ImportadorCamara(votings)
        date = importer.converte_data('24/5/2011')
        vote = votings[1]
        self.assertEquals(vote.data.day, date.day)
        self.assertEquals(vote.data.month, date.month)
        self.assertEquals(vote.data.year, date.year)

    def test_forest_code_votes(self):
        """Checks if the votes are correct (who voted, what he or she voted and
            his or her political party name)."""

        votings = models.Votacao.objects.filter(proposicao__id_prop=ID)[0]
        first_vote = [
            v for v in votings.votes() if v.legislatura.parlamentar.nome == 'Mara Gabrilli'][0]
        seconde_vote = [
            v for v in votings.votes() if v.legislatura.parlamentar.nome == 'Carlos Roberto'][0]
        self.assertEquals(first_vote.opcao, models.SIM)
        self.assertEquals(seconde_vote.opcao, models.NAO)
        self.assertEquals(first_vote.legislatura.partido.nome, 'PSDB')
        self.assertEquals(seconde_vote.legislatura.localidade, 'SP')


class WsPlenarioTest(TestCase):

    def test_proposition_in_xml(self):
        """Tests if the plenary proposition defined are in zip_votadas[x]."""

        minimal_year = 2013
        maximal_year = 2013
        chamberWebService = cdep.Camaraws()
        chamberWebService.obter_proposicoes_votadas_plenario = Mock(
            side_effect=mock_obter_proposicoes_votadas_plenario)
        proposition_finder = cdep.ProposicoesFinder()
        zip_votadas = proposition_finder.find_props_disponiveis(
            minimal_year, maximal_year, chamberWebService)
        prop_test = ('14245', 'PEC 3/1999')
        for x in range(0, len(zip_votadas)):
            self.assertTrue(prop_test in zip_votadas[x])

    def test_find_propositions(self):
        """Tests if the plenary proposition "id", "sigla", "num" and "year" are
        in 'dict_votadas'."""

        minimal_year = 2013
        maximal_year = 2013
        chamberWebService = cdep.Camaraws()
        chamberWebService.obter_proposicoes_votadas_plenario = Mock(
            side_effect=mock_obter_proposicoes_votadas_plenario)
        proposition_finder = cdep.ProposicoesFinder()
        zip_votadas = proposition_finder.find_props_disponiveis(
            minimal_year, maximal_year, chamberWebService)
        proposition_parser = cdep.ProposicoesParser(zip_votadas)
        dict_votadas = proposition_parser.parse()
        proposition_on_dict = {'id': PLENARY_ID, 'sigla':
                        PLENARY_ACRONYM, 'num': PLENARY_NUMBER, 'ano': PLENARY_YEAR}
        self.assertTrue(proposition_on_dict in dict_votadas)
