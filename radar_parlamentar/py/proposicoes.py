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

""" Module propositions - functions for processing propositions
Has script that lists propositions to polls.

Functions:
parse_html - parse recusrsos / proposicoes.html file
com_votacao - web service verifies the list of propositions that have polls
proposicoes_com_votacao - returns list of propositions that have voting based 
votadas.txt file.
"""

import re
import codecs
import camaraws

# PL - projeto de lei
# PLP - projeto de lei complementar
# PDC - projeto de decreto legislativo
# MPV - projeto de medida provisória
# PEC - proposta de emenda à constituição

def parse_html():
    """ Parse do arquivo recusrsos/proposicoes.htmll
    Retorna:
    Uma lista com a identificação das proposições encontradas no htmll
    Cada posição da lista é um dicionário com chaves \in {id, tipo, num, ano}
    As chaves e valores desses dicionários são strings."""

    # File contains propositions voted on by the chamber in 2011:

    file_name = 'recursos/proposicoes2011.html'  
    prop_file = codecs.open(file_name, encoding='ISO-8859-15', mode='r')
    regexp = '<A HREF=http://.*?id=([0-9]*?)>([A-Z]*?) ([0-9]*?)/([0-9]{4})</A>'
    proposicoes = []
    for line in prop_file:
        res = re.search(regexp, line)
        if res:
            proposicoes.append({'id':res.group(1), 'tipo':res.group(2), 
		'num':res.group(3), 'ano':res.group(4)})
    return proposicoes

def parse():
    """ Parse the recusrsos / proposicoes.htmll file
     returns:
     A list identifying the propositions found in htmll
     Each position on the list is a dictionary with keys \ in {id, type in a year}
     The keys and values ​​are strings of these dictionaries.
	"""

    """File contains propositions voted on by the chamber in 2011 for which we 
	obtained the vote xml:
	"""

    file_name = 'resultados/votadas.txt'  
    prop_file = open(file_name, 'r')

    # Example: "485262: MPV 501/2010"
    
    regexp = '^([0-9]*?): ([A-Z]*?) ([0-9]*?)/([0-9]{4})'
    proposicoes = []
    for line in prop_file:
        res = re.search(regexp, line)
        if res:
            proposicoes.append({'id':res.group(1), 'tipo':res.group(2), 
		'num':res.group(3), 'ano':res.group(4)})
    return proposicoes

def com_votacao(proposicoes): 
    """ Checks which propositions have votes in the chamber web service
     It is only on those propositions we will do our analyzes
     This check is done by invoking the web service camera
     arguments:
     propositions - list of propositions; every proposition is a dictionary with 
	keys \ in {id, type in a year}; keys and values ​​are strings

     returns:
     List of propositions that present voting list
     Each proposition is a dictionary with keys \ in {id, type in a year}; 
	keys and values ​​are strings.
	"""

    votadas = []
    for prop in proposicoes:
        print "requisitando " + prop['id']
        vot = camaraws.obter_votacao(prop['tipo'], prop['num'], prop['ano']) 
        if vot != None:
            votadas.append(prop)
    return votadas

def proposicoes_com_votacao():
    """ Returns the list of propositions for which it is possible to get the xml of the vote
     This list is taken from the results / votadas.txt file
     returns:
     A list of propositions
     Each position on the list is a dictionary with keys \ in {id, type in a year}
     The keys and values ​​are strings of these dictionaries."""
    return parse()


if __name__ == "__main__":
    proposicoes = parse_html()
    votadas = com_votacao(proposicoes)
    print("# Documento entregue pela câmara continha %d proposições votadas em 2011" % len(proposicoes))
    print("# %d proposições retornaram informações sobre suas votações pelo web service" % len(votadas))
    print("# Proposições que retornaram a votação:")
    for prop in votadas:
        print("%s: %s %s/%s" % (prop['id'],prop['tipo'],prop['num'],prop['ano']))



