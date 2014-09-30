#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2012, Leonardo Leite
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

"""Module propositions - functions for processing propositions
Has script that lists propositions to polls.

Functions:
parse_html - parse recusrsos / proposicoes.html file
com_votacao - web service verifies the list of propositions that have polls
proposicoes_com_votacao - returns list of propositions that have voting based
votadas.txt file."""

import re
import codecs
import camaraws

# PL - projeto de lei
# PLP - projeto de lei complementar
# PDC - projeto de decreto legislativo
# MPV - projeto de medida provisória
# PEC - proposta de emenda à constituição

def parse_html():
    """Parse of the file recusrsos/proposicoes.htmll
    Retorns:
    A list with a identification of the propositions found in html
    Each list position is a dicionary with key \in {id, tipo, num, ano}
    The keys and values of this dictionaries are strings."""

    # File contains propositions voted on by the chamber in 2011:
    file_name = 'recursos/proposicoes2011.html'
    prop_file = codecs.open(file_name, encoding='ISO-8859-15', mode='r')
    regexp = '<A HREF=http://.*?id=([0-9]*?)>([A-Z]*?) ([0-9]*?)/([0-9]{4})</A>'
    propositions = []
    for line in prop_file:
        res = re.search(regexp, line)
        if res:
            propositions.append({'id':res.group(1), 'tipo':res.group(2),
        'num':res.group(3), 'ano':res.group(4)})
    return propositions

def parse():
    """Parse the recursos / proposicoes.htmll file
     returns:
     A list identifying the propositions found in htmll
     Each position on the list is a dictionary with keys \ in {id, type in a year}
     The keys and values ​​are strings of these dictionaries."""

    """File contains propositions voted on by the chamber in 2011 for which we
	obtained the vote xml:"""

    file_name = 'resultados/votadas.txt'
    prop_file = open(file_name, 'r')

    regexp = '^([0-9]*?): ([A-Z]*?) ([0-9]*?)/([0-9]{4})'
    propositions = []
    for line in prop_file:
        res = re.search(regexp, line)
        if res:
            propositions.append({'id':res.group(1), 'tipo':res.group(2),
		'num':res.group(3), 'ano':res.group(4)})
    return propositions

def com_votacao(proposicoes):
    """Checks which propositions have votes in the chamber web service
     It is only on those propositions we will do our analyzes
     This check is done by invoking the web service camera
     arguments:
     propositions - list of propositions; every proposition is a dictionary
     with keys \ in {id, type in a year}; keys and values ​​are strings

     returns:
     List of propositions that present voting list
     Each proposition is a dictionary with keys \ in {id, type in a year};
	keys and values ​​are strings."""

    voted = []
    for proposition in proposicoes:
        print "requisitando " + proposition['id']
        votes = camaraws.obter_votacao(proposition['tipo'], proposition['num'],
                                     proposition['ano'])
        if votes != None:
            voted.append(proposition)
    return voted

def proposicoes_com_votacao():
    """Returns the list of propositions for which it is possible to get the xml
    of the vote
     This list is taken from the results / votadas.txt file
     returns:
     A list of propositions
     Each position on the list is a dictionary with keys \ in {id, type in a year}
     The keys and values ​​are strings of these dictionaries."""
    return parse()


if __name__ == "__main__":
    propositions = parse_html()
    voted = com_votacao(propositions)
    print("# Documento entregue pela câmara continha %d proposições votadas em 2011" %
          len(propositions))
    print("# %d proposições retornaram informações sobre suas votações pelo web service" %
          len(voted))
    print("# Proposições que retornaram a votação:")
    for proposition in voted:
        print("%s: %s %s/%s" % (proposition['id'],proposition['tipo'],proposition['num'],
                                proposition['ano']))



