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

"""Script analise_tipos -- makes an analysis of the types of propositions voted on
2011"""

import proposicoes

proposicoes = proposicoes.parse_html()

initial_quantity = 0
ordinary_law_projects = complementary_law_projects = legislative_decree_projects = provisional_measures = amendment_constitution = initial_quantity

# Performs proposition count for each type
for propositions in proposicoes:
  if (propositions['tipo'] == 'PL'):
    ordinary_law_projects += 1
  elif (propositions['tipo'] == 'PLP'):
    complementary_law_projects += 1
  elif (propositions['tipo'] == 'PDC'):
    legislative_decree_projects += 1
  elif (propositions['tipo'] == 'MPV'):
    provisional_measures += 1
  elif (propositions['tipo'] == 'PEC'):
    amendment_constitution += 1

# Performs total count of propositions and shows the result for each type
total = len(proposicoes)
print('Votações na câmara em 2011')
print('%d proposições' % total)
print('%d PLs (%d%s)' % (ordinary_law_projects, ordinary_law_projects/total*100, '%'))
print('%d PLPs (%d%s)' % (complementary_law_projects, complementary_law_projects/total*100, '%'))
print('%d PDCs (%d%s)' % (legislative_decree_projects, legislative_decree_projects/total*100, '%'))
print('%d MPVs (%d%s)' % (provisional_measures, provisional_measures/total*100, '%'))
print('%d PECs (%d%s)' % (amendment_constitution, amendment_constitution/total*100, '%'))
#print('Checksum: %d' % (pl+plp+pdc+mpv+pec))
