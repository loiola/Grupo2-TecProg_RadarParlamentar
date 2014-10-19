# !/usr/bin/python
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
from importadores import conv
from modelagem import models


class ConvencaoTest(TestCase):
    """Tests for the Franch Convention."""

    @classmethod
    def setUpClass(cls):
        importer = conv.ImportadorConvencao()
        importer.importar()

    @classmethod
    def tearDownClass(cls):
        from util_test import flush_db
        flush_db(cls)

    def setUp(self):
        self.conv = models.CasaLegislativa.objects.get(nome_curto='conv')

    def test_check_len_votings(self):
        """Tests if the number of Franch Convention votings is correct."""

        NUMBER_OF_VOTINGS = 8
        votings_number = len(models.Votacao.objects.filter(
            proposicao__casa_legislativa=self.conv))
        self.assertEquals(votings_number, NUMBER_OF_VOTINGS)

    def test_check_len_votes(self):
        """Tests if the number of Franch Convention votes is correct."""

        NUMBER_OF_VOTINGS = 8 * 3 * 3
        votings_number = len(models.Voto.objects.filter(
            votacao__proposicao__casa_legislativa=self.conv))
        self.assertEquals(votings_number, NUMBER_OF_VOTINGS)

    def test_check_len_votes_by_votings(self):
        """Tests if the number Franch Convention votes by votings is correct."""

        NUMBER_OF_VOTES_BY_VOTINGS = 3 * 3
        votings = models.Votacao.objects.filter(
            proposicao__casa_legislativa=self.conv)
        for votacao in votings:
            votings_number = len(models.Voto.objects.filter(votacao=votacao))
            self.assertEquals(votings_number, NUMBER_OF_VOTES_BY_VOTINGS)

    def test_check_political_parties(self):
        """Tests if the names of Franch Convention 'partidos' are correct."""

        political_parties = models.Partido.objects.all()
        political_parties_names = [p.nome for p in political_parties]
        self.assertTrue(conv.GIRONDINOS in political_parties_names)
        self.assertTrue(conv.JACOBINOS in political_parties_names)
        self.assertTrue(conv.MONARQUISTAS in political_parties_names)

    def test_check_parliamentaries(self):
        """Tests if the number of Franch Convention parliamentaries and their names are
        correct."""

        NUMBER_OF_PARLIAMENTARIES = 3 * 3
        parliamentaries = models.Parlamentar.objects.filter(
            legislatura__casa_legislativa=self.conv)
        self.assertEqual(len(parliamentaries), NUMBER_OF_PARLIAMENTARIES)
        parliamentaries_names = [p.nome for p in parliamentaries]
        self.assertEquals(
            parliamentaries_names.count('Pierre'), NUMBER_OF_PARLIAMENTARIES)
