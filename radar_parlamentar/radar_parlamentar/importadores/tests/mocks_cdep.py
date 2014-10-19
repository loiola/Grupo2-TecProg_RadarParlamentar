# !/usr/bin/python
# coding=utf8

# Copyright (C) 2012, Leonardo Leite, Diego Rabatone
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

import os
import xml.etree.ElementTree as etree
import glob
from importadores import cdep

VOTADAS_FILE_PATH = cdep.RESOURCES_FOLDER + 'votadas_test.txt'
MOCK_PATH = os.path.join(cdep.RESOURCES_FOLDER, 'mocks')
MOCK_PROPOSITION = glob.glob(os.path.join(MOCK_PATH, 'proposicao_*'))
MOCK_PROPOSITIONS = glob.glob(os.path.join(MOCK_PATH, 'proposicoes_*'))
MOCK_VOTINGS = glob.glob(os.path.join(MOCK_PATH, 'votacoes_*'))
MOCK_VOTED_PROPOSITIONS = glob.glob(
    os.path.join(MOCK_PATH, 'proposicoes_votadas_*'))


def check_xml(nome, lista_xmls):
    """Checks if there is a file with certain name, in a list of files"""

    for xml in lista_xmls:
        if nome == os.path.basename(xml):
            with open(xml) as arquivo_xml:
                return etree.fromstring(arquivo_xml.read())
    raise ValueError


def mock_get_proposition(id_prop):
    """Mock of 'get_proposition' method from camaraWS (webservice).
    Gets the id of the proposition and returns check_xml"""

    return check_xml('proposicao_' + str(id_prop), MOCK_PROPOSITION)


def mock_list_propositions(sigla, ano):
    """Mock of 'list_propositions' method from camaraWS (webservice).
    Receives the acronym and the year of proposition and returns a xml"""

    return check_xml('proposicoes_' + sigla + str(ano), MOCK_PROPOSITIONS)


def mock_get_voted_propositions_on_plenary(ano):
    """Mock of 'get_voted_propositions_on_plenary' method from camaraWS (webservice).
    Receive the year of proposition and returns a xml"""

    return check_xml('proposicoes_votadas_' + str(
        ano), MOCK_VOTED_PROPOSITIONS)


def mock_get_votings(sigla, num, ano):
    """Mock of 'get_votings' method from camaraWS (webservice).
    Receives a acronym, the number and the year and returns a xml"""

    return check_xml('votacoes_' + sigla + str(num) + str(
        ano), MOCK_VOTINGS)
