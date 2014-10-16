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

"""Script vetores -- imprime os vetores de votações"""

import proposicoes
import camaraws
import partidos
import sys
from partidos import PARTIDOS

length = len(PARTIDOS)

# recovery propositions

# identification of propositions voted on 2011
voted = proposicoes.parse()

# list of propositions with their respective votes
proposicoes = []

# Total analyzed votes
n_votes = 0
for propositions in voted:
    print('Analisando proposição ' + propositions['id'])

    # get voting web service
    votes_propositions = camaraws.obter_votacao(propositions['tipo'], propositions['num'], propositions['ano'])
    n_votes += len(votes_propositions.votacoes)
    proposicoes.append(votes_propositions)

for party in PARTIDOS:
    party_vector = partidos.vetor_votacoes(party, proposicoes)
    print("%s\n%s" % (party, party_vector))
