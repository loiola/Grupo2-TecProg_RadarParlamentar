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


# Constants on the Forest Code

# Constant representing the indicator of the forest code
ID = '17338'

# Constant that represents the abbreviation of the forest code (PL)
SIGLA = 'PL'

# Constant representing the number of the Forest Code (1876)
NUM = '1876'

# Constant representing the year of the Forest Code (1999)
ANO = '1999'

# constant representing the name of the Forest Code (PL 1876/1999)
NOME = 'PL 1876/1999'


class CamarawsTest(TestCase):

    """Conducts tests involving Web services Camera"""

    def setUp(self):

        # Receives Cameraws() method of cdep
        self.camaraws = cdep.Camaraws()

    def test_obtain_proposition(self):

        # Receives obter_proposicao_por_id() method
        forest_code_xml = self.camaraws.obter_proposicao_por_id(ID)

        # Receives the search of proposition by name in the xml file
        forest_code_name = forest_code_xml.find_legislature('nomeProposicao').text

        self.assertEquals(forest_code_name, NOME)

    def test_obtain_votings(self):

        # Receives  the votes by acronym, number and year
        forest_code_xml = self.camaraws.obter_votacoes(SIGLA, NUM, ANO)

        # Receives the date of the proposition of the forest code to perform test
        found_vote_date = forest_code_xml.find_legislature(
            'Votacoes').find_legislature('Votacao').get('Data')

        self.assertEquals(found_vote_date, '11/5/2011')

    def test_list_propositions(self):

        # Receives pecs propositions for the year 2011
        pecs_2011_xml = self.camaraws.listar_proposicoes('PEC', '2011')

        # Receives the elements of proposition in the file
        pecs_elements = pecs_2011_xml.findall('proposicao')

        self.assertEquals(len(pecs_elements), 135)

    def test_proposition_that_doesnt_exist(self):

        # Receives a id that does not exists
        no_id = 'id_que_nao_existe'

        # Receives False
        caught = False

        try:
            self.camaraws.obter_proposicao_por_id(no_id)
        except ValueError as e:
            self.assertEquals(
                e.message, 'Proposicao %s nao encontrada' % no_id)

            # Receives True
            caught = True

        self.assertTrue(caught)

    def test_votings_that_dont_exist(self):

        # Receives a acronym that does not exist (PCC)
        acronym = 'PCC'

        # Receives a number that does not exist (1500)
        number_of_proposition = '1500'

        # Receives a year that does not exist (1876)
        year_of_voting = '1876'

        # Receives False
        caught = False

        try:
            self.camaraws.obter_votacoes(acronym, number_of_proposition,
                                         year_of_voting)
        except ValueError as e:
            self.assertEquals(
                e.message, 'Votacoes da proposicao %s %s/%s nao encontrada'
                % (acronym, number_of_proposition, year_of_voting))

            # Receives True
            caught = True

        self.assertTrue(caught)

    def test_list_propositions_that_dont_exist(self):

        # Receives a acronym (PEC)
        acronym = 'PEC'

        # Receives a year that does not exist (3013)
        year_of_proposition = '3013'

        try:
            self.camaraws.listar_proposicoes(acronym, year_of_proposition)
        except ValueError as e:
            self.assertEquals(
                e.message, 'Proposicoes nao encontradas para sigla=%s&ano=%s'
                % (acronym, year_of_proposition))

            # Receives True
            caught = True

        self.assertTrue(caught)

    def test_list_acronyms(self):
        """Test to list the acronyms of propositions"""

        # Receives the listar_siglas() method
        acronyms = self.camaraws.listar_siglas()

        self.assertTrue('PL' in acronyms)
        self.assertTrue('PEC' in acronyms)
        self.assertTrue('MPV' in acronyms)

    def test_voting_present_in_plenary(self):

        # Receives a year of an existing vote at Plenarium (2013)
        plenary_year = 2013

        # Receives a proposition name that was voted at Plenarium (REQ 8196/2013)
        plenary_name = 'REQ 8196/2013'

        # Receives a invalid proposition name (DAVID 1309/1992)
        no_plenary_name = 'DAVID 1309/1992'

        # Receives obter_proposicoes_votadas_plenario() method
        plenary_etree = self.camaraws.obter_proposicoes_votadas_plenario(
            plenary_year)

        # Receives the list of propositions
        list_of_propositions = []

        for nomeProp in plenary_etree:
            list_of_propositions.append(nomeProp.find_legislature('nomeProposicao').text)
        self.assertTrue(plenary_name in list_of_propositions)
        self.assertFalse(no_plenary_name in list_of_propositions)
