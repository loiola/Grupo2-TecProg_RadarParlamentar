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

"""Script pecs
Download the PECs 2011
Shows aggregate votes by party"""

from __future__ import unicode_literals
import camaraws

pecs = []

# PEC music (tax exemption for music and Brazilian artists)
# http://www.camara.gov.br/proposicoesWeb/fichadetramitacao?idProposicao=357094
type = 'pec'
number = '98'
year = '2007'
pecs.append(camaraws.obter_votacao(type, number, year))

# Extending the validity of DRU until December 31, 2015
# http://www.camara.gov.br/proposicoesWeb/fichadetramitacao?idProposicao=513496
type = 'pec'
number = '61'
year = '2011'
pecs.append(camaraws.obter_votacao(type, number, year))

# Print propositions
for propositions in pecs:
  print(propositions)

  for voting in propositions.votacoes:
    print('************')
    print(voting)
    dic = voting.by_party()

    for party, vote in dic.items():
      print("%s: \t Sim: %s \t Não: %s \t Abstenções: %s" % (party, vote.sim,
                                                             vote.nao, vote.abstencao))
  print('=================================================================================')
