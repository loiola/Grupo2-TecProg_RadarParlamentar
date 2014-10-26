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
propositions = []

# total analyzed votes
n_votes = 0

for propositions in voted:
  print('Analisando proposição ' + propositions['id'])

  # get voting web service
  propositions_voting = camaraws.get_votings(propositions['tipo'],
                                               propositions['num'], propositions['ano'])
  n_votes += len(propositions_voting.votacoes)
  proposicoes.append(propositions_voting)

# analysis of the similarity
percentage_conversion_factor = 100
print('Análise baseada em %d votações de %d proposições, votadas na '
      'camâra em 2011' % (n_votes, len(voted)))

for i in range(0,length):
  for j in range(i+1,length):
    similarity = partidos.semelhanca(PARTIDOS[i], PARTIDOS[j], proposicoes)

    print('Semelhança entre %s e %s = %.2f%s' % (PARTIDOS[i], PARTIDOS[j],
                                                 similarity*convert_to_percentage, '%'))

