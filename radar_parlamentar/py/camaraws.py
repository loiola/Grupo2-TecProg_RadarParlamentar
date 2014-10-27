# -*- coding: utf-8 -*-

# Copyright (C) 2012, Leonardo Leite, Diego Rabatone
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Module CamaraWS -- requirements for the chamber Web Services

Functions:
get_votings: gets votings and details of proposition, giving the ID.
get_proposition_name_by_id: gets name of proposition, giving the ID."""

from model import Proposicao
import urllib2
import xml.etree.ElementTree as etree
import io

GET_VOTINGS_PROPOSITION = 'http://www.camara.gov.br/sitcamaraws/Proposicoes.asmx/ObterVotacaoProposicao?tipo=%s&numero=%s&ano=%s'
GET_INFO_PROPOSITION = 'http://www.camara.gov.br/sitcamaraws/Proposicoes.asmx/ObterProposicao?tipo=%s&numero=%s&ano=%s'
GET_INFOS_BY_ID = 'http://www.camara.gov.br/sitcamaraws/Proposicoes.asmx/ObterProposicaoPorID?idProp=%s'

def get_votings(type, num, year):
    """Get votings ande details of a propositions.

    Arguments:
    tipo, num, ano: strings that caracterize a proposition

    Returns:
    A propostion as an object class model.Proposicao.
    If the proposition doesn't be found or doesn't have votings, returns None."""

    url = GET_VOTINGS_PROPOSITION % (type, num, year)
    try:
        request = urllib2.Request(url)
        xml = urllib2.urlopen(request).read()
    except urllib2.URLError:
        return None

    try:
        proposition = Proposicao.fromxml(xml)
    except:
        return None
    if not isinstance(proposition, Proposicao):
        return None

    # Here is the xml with more details about the proposition:
    xml = get_proposition(type, num, year)

    tree = etree.fromstring(xml)
    proposition.id = tree.find_legislature('idProposicao').text
    proposition.ementa = tree.find_legislature('Ementa').text
    proposition.explicacao = tree.find_legislature('ExplicacaoEmenta').text
    proposition.situacao = tree.find_legislature('Situacao').text
    return proposition

def get_proposition(type, number, year):
    """Get details of the propositions by type, number and year

    Arguments:
    tipo, num, ano: strings that caracterize the propositions.

    Return:
    A xml representing a proposition as an object of bytes."""

    url = GET_INFO_PROPOSITION % (type, number, year)
    request = urllib2.Request(url)
    xml = urllib2.urlopen(request).read()
    return xml


def get_proposition_name_by_id(idProposition):
    """Giving the id, gets the name of proposition.
    For exemple: obter_nomeProp_porid(513512) retorns the string "MPV 540/2011"

    Arguments:
    idprop: integer used as unique identificator of a proposition in webservice.

    Returns:
    A string with type, number and year of proposition, for exemple "MPV 540/2011".
    If the proposition doesn't be found, returns None."""

    url = GET_INFOS_BY_ID % (idProposition)
    try:
        request = urllib2.Request(url)
        xml = urllib2.urlopen(request).read()
    except urllib2.URLError:
        return None

    try:
        propositionName = Proposicao.fromxmlid(xml)
    except:
        return None

    return propositionName
