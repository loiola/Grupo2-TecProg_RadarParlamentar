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

"""Algebra module: has functions of vector algebra."""


import math

def calculate_vector_size(vector):
  """Calculates the norm of a vector (also called module or size).

  Arguments:
  vector: a list with real values.

  Returns:
  The vector's norm, which is the square root of the sum of the squares of each element of the vector.
  """
  sum = 0
  for v_i in vector:
    sum += v_i*v_i
  return math.sqrt(sum)

def normalize_vector(vetor):
  """Calculates a normalized vector in the same direction and the direction vector supplied.

  Arguments:
  vector: a list with real values.

  Returns:
  A list representing normalized vector (vn), calculated as 'vn_i = vector_i / norm(vector)'
  """
  normalized = []
  n = calculate_vector_size(vetor)
  for v_i in vetor:
    normalized.append(v_i / n)
  return normalized

def calculate_scalar_product(vector1, vector2):
  """Calculates the dot product between two vectors.

  Arguments:
  vector1, vector2: lists with real values.

  Returns:
  the dot product vector1.vector2, which is the sum of the products of the elements of the vectors.
  Exemple: v1=[a,b,c], v2=[x,y,z] => v1.v2 = a*x + b*y +c*z
  """
  sum = 0
  for v1, v2 in zip(vector1, vector2):
    sum += v1*v2
  return sum
