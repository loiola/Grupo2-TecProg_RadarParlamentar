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

# constant on the Forest Code
ID = '17338'
SIGLA = 'PL'
NUM = '1876'
ANO = '1999'
NOME = 'PL 1876/1999'


class CamarawsTest(TestCase):

    #Conducts tests involving Web services Camera

    def setUp(self):
        self.camaraws = cdep.Camaraws()

    def test_obter_proposicao(self):
        forest_code_xml = self.camaraws.obter_proposicao_por_id(ID)
        forest_code_name = forest_code_xml.find('nomeProposicao').text
        self.assertEquals(forest_code_name, NOME)

    def test_obter_votacoes(self):
        forest_code_xml = self.camaraws.obter_votacoes(SIGLA, NUM, ANO)
        found_vote_date = forest_code_xml.find(
            'Votacoes').find('Votacao').get('Data')
        self.assertEquals(found_vote_date, '11/5/2011')

    def test_listar_proposicoes(self):
        pecs_2011_xml = self.camaraws.listar_proposicoes('PEC', '2011')
        pecs_elements = pecs_2011_xml.findall('proposicao')
        self.assertEquals(len(pecs_elements), 135)

    def test_prop_nao_existe(self):
        no_id = 'id_que_nao_existe'
        caught = False
        try:
            self.camaraws.obter_proposicao_por_id(no_id)
        except ValueError as e:
            self.assertEquals(
                e.message, 'Proposicao %s nao encontrada' % no_id)
            caught = True
        self.assertTrue(caught)

    def test_votacoes_nao_existe(self):
        acronym = 'PCC'
        number_of_proposition = '1500'
        year_of_voting = '1876'
        caught = False
        try:
            self.camaraws.obter_votacoes(acronym, number_of_proposition,
                                         year_of_voting)
        except ValueError as e:
            self.assertEquals(
                e.message, 'Votacoes da proposicao %s %s/%s nao encontrada'
                % (acronym, number_of_proposition, year_of_voting))
            caught = True
        self.assertTrue(caught)

    def test_listar_proposicoes_que_nao_existem(self):
        acronym = 'PEC'
        year_of_proposition = '3013'
        try:
            self.camaraws.listar_proposicoes(acronym, year_of_proposition)
        except ValueError as e:
            self.assertEquals(
                e.message, 'Proposicoes nao encontradas para sigla=%s&ano=%s'
                % (acronym, year_of_proposition))
            caught = True
        self.assertTrue(caught)

    def test_listar_siglas(self):
        acronyms = self.camaraws.listar_siglas()
        self.assertTrue('PL' in acronyms)
        self.assertTrue('PEC' in acronyms)
        self.assertTrue('MPV' in acronyms)

    def test_votacao_presente_plenario(self):
        plenary_year = 2013
        plenary_name = 'REQ 8196/2013'
        no_plenary_name = 'DAVID 1309/1992'
        plenary_etree = self.camaraws.obter_proposicoes_votadas_plenario(
            plenary_year)
        list_of_propositions = []
        for nomeProp in plenary_etree:
            list_of_propositions.append(nomeProp.find('nomeProposicao').text)
        self.assertTrue(plenary_name in list_of_propositions)
        self.assertFalse(no_plenary_name in list_of_propositions)
