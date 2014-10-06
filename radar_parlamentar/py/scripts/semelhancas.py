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

"""Script semelhancas -- Checks the difference between two partidos based on the
propositions voted on in 2011"""

import proposicoes
import camaraws
import partidos
import sys
from partidos import PARTIDOS

length = len(PARTIDOS)

# PRTB, PRP, PMN, PSL, PHS given problem, did appear in some polls
# TODO: o que fazer nesses casos?
length = len(PARTIDOS)

# recovery propositions

# identification of propositions voted on in 2011
voted = proposicoes.parse()

# list of propositions with their respective votes
proposicoes = []

# total analyzed votes
n_vot = 0
for propositions in voted:
  print('Analisando proposição ' + propositions['id'])

  # get voting web service
  prop_vot = camaraws.obter_votacao(propositions['tipo'], propositions['num'], propositions['ano'])
  n_vot += len(prop_vot.votacoes)
  proposicoes.append(prop_vot)

# analysis of the similarity
print('Análise baseada em %d votações de %d proposições, votadas na camâra em 2011' % (n_vot, len(voted)))
for i in range(0,length):
  for j in range(i+1,length):
    sem = partidos.semelhanca(PARTIDOS[i], PARTIDOS[j], proposicoes)
    print('Semelhança entre %s e %s = %.2f%s' % (PARTIDOS[i], PARTIDOS[j], sem*100, '%'))

