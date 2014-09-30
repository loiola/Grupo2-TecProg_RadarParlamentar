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

"""Module camaraws -- requirements for the chamber Web Services

Functions:
obter_votacao -- gets votings and details of proposition, giving the ID.
obter_nomeProp_porid -- gets name of proposition, giving the ID.."""

from model import Proposicao
import urllib2
import xml.etree.ElementTree as etree
import io

OBTER_VOTACOES_PROPOSICAO = 'http://www.camara.gov.br/sitcamaraws/Proposicoes.asmx/ObterVotacaoProposicao?tipo=%s&numero=%s&ano=%s'
OBTER_INFOS_PROPOSICAO = 'http://www.camara.gov.br/sitcamaraws/Proposicoes.asmx/ObterProposicao?tipo=%s&numero=%s&ano=%s'
OBTER_INFOS_PORID = 'http://www.camara.gov.br/sitcamaraws/Proposicoes.asmx/ObterProposicaoPorID?idProp=%s'

def obter_votacao(tipo, num, ano):
    """Get votings ande details of a propositions.

    Arguments:
    tipo, num, ano -- strings that caracterize a proposition

    Retorns:
    A propostions as an object class model.Proposicao.
    If the proposition doesn't be found or doesn't have votings, returns None."""

    url  = OBTER_VOTACOES_PROPOSICAO % (tipo, num, ano)
    try:
        request = urllib2.Request(url)
        xml = urllib2.urlopen(request).read()
    except urllib2.URLError:
        return None

    try:
        prop = Proposicao.fromxml(xml)
    except:
        return None
    if not isinstance(prop, Proposicao): 
        return None

    # Here is the xml with more details about the proposition:
    xml = obter_proposicao(tipo, num, ano) 

    tree = etree.fromstring(xml)
    prop.id = tree.find('idProposicao').text
    prop.ementa = tree.find('Ementa').text
    prop.explicacao = tree.find('ExplicacaoEmenta').text
    prop.situacao = tree.find('Situacao').text 
    return prop

def obter_proposicao(tipo, num, ano):
    """Get details of the propositions by type, number and year

    Arguments:
    tipo, num, ano -- strings that caracterize the propositions.

    Return:
    A xml representing a proposition as an object of bytes classe."""

    url = OBTER_INFOS_PROPOSICAO % (tipo, num, ano)
    request = urllib2.Request(url)
    xml = urllib2.urlopen(request).read()
    return xml


def obter_nomeProp_porid(idProp):
    """Giving the id, gets the name of proposition.
    For exemple: obter_nomeProp_porid(513512) retorns the string "MPV 540/2011"

    Arguments:
    idprop -- integer used as unique identificator of a proposition in webservice.

    Returns:
    A string with type, number and year of proposition, for exemple "MPV 540/2011".
    If the proposition doesn't be found, returns None."""

    url = OBTER_INFOS_PORID % (idProp)
    try:
        request = urllib2.Request(url)
        xml = urllib2.urlopen(request).read()
    except urllib2.URLError:
        return None

    try:
        nomeProp = Proposicao.fromxmlid(xml)
    except:
        return None

    return nomeProp
