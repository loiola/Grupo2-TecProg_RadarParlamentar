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

"""Script semelhanca_pca
Checks the difference between the partidos
based on the propositions voted on in 2011
using PrincipalComponentAnalysis (analysis of primary components)"""

import partidos
import sys

parties_list = []
vectors = []

# Recovering vectors polls
name = 'resultados/vetores.txt'
vfile = open(name, 'r')
flag = 1
for line in vfile:
  if flag % 2 == 1:
    parties_list.append(line.rstrip())
  else:
    vectors.append(eval(line))
  flag += 1

# Analyzing similarities
print('Análise PrincipalComponentAnalysis')
p = partidos.semelhanca_pca(vectors)
pc = p.pc()

# Printing similarities
print "Fração da variância explicada pelas dimensões:"
for i in range(0, 4):
  print "%f " % ( p.eigen[i] / p.eigen.sum() )

print "\nCoordenadas:"
for i in range(0,len(parties_list)):
  print "%s: [%f, %f]" % (parties_list[i], pc[i][0], pc[i][1])
