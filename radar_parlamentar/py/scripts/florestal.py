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

"""Script florestal 
Download voting forest code
Shows aggregate votes by party
If you flag -uf shows votes by UF"""

from __future__ import unicode_literals
import camaraws
import sys

# Forest Code
# http://www.camara.gov.br/proposicoesWeb/fichadetramitacao?idProposicao=17338
type = 'pl'
number = '1876'
year = '1999'
proposition = camaraws.get_votings(type, number, year)

txt = str(proposition)
print type(txt)

# Print propositions
for votations in proposition.votacoes:
  print('************')
  print(votations)

  if len(sys.argv) > 1 and sys.argv[1] == '-uf':
    dic = votations.aggregate_votes_by_UF()
  else:
    dic = votations.by_party()

  for key, vote in dic.items():
    yes = vote.sim
    no = vote.nao
    abstention = vote.abstencao
    print("%s: \t Sim: %s \t Não: %s \t Abstenções: %s" % (key, yes, no, abstention))

