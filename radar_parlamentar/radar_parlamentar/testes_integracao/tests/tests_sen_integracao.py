#!/usr/bin/python
# coding=utf8

# Copyright (C) 2012, Leonardo Leite, Diego Rabatone
#
# This file is part of Radar Parlamentar.
#
# Radar Parlamentar is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Radar Parlamentar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Radar Parlamentar.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals
from django.test import TestCase
from importadores import sen

#Conducts tests involving Web services about Senado

class SenadoWSTest(TestCase):

    def test_obtain_senators_from_legislature(self):

        # Receives a legislature by id (52)
        legislature_id = '52'

        # Receives SenadoWS() method
        senws = sen.SenadoWS()

        # Receives the senators of the legislature whose identifier is number 52
        tree = senws.get_senators_from_legislature(legislature_id)

        self.assertIsNotNone(tree)
        self.assertTrue(len(tree.findall('Metadados')) == 1)






# end
