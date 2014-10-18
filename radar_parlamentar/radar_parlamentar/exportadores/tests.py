# !/usr/bin/python
# coding=utf8

# Copyright (C) 2013, Arthur Del Esposte,  David Carlos de Araujo Silva
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
from exportadores import exportar
import os
from modelagem import models


MODULE_DIR = os.path.abspath(os.path.dirname(__file__))


class ExportadoresFileTest(TestCase):

    @classmethod
    def setUpClass(cls):
        """Method to set responsible for what is needed to run the tests. 
        In this case, the creation of objects in the test bank."""
        testParty1 = models.Partido(name='PMDB', number='40')
        testParty2 = models.Partido(name='PT', number='13')
        partyTest3 = models.Partido(name='PSDB', number='23')
        testParty1.save()
        testParty2.save()
        partyTest3.save()

        parliamentaryTest1 = models.Parlamentar(
            id_parliamentary='', name='Ivandro Cunha Lima', gender='')
        parliamentaryTest2 = models.Parlamentar(
            id_parliamentary='', name='Fernando Ferro', gender='')
        parliamentaryTest3 = models.Parlamentar(
            id_parliamentary='', name='Humberto Costa', gender='')

        parliamentaryTest1.save()
        parliamentaryTest2.save()
        parliamentaryTest3.save()

        legislative_houseTest1 = models.CasaLegislativa(
            name='Camara dos Deputados', short_name='cdep', sphere='FEDERAL',
            local='', update='2012-06-01')

        legislative_houseTest2 = models.CasaLegislativa(
            name='Camara Municipal de Sao Paulo', short_name='cmsp',
            sphere='MUNICIPAL', local='Sao Paulo - SP',
            update='2012-12-31')

        legislative_houseTest1.save()
        legislative_houseTest2.save()

        legislatureTest1 = models.Legislatura(
            parliamentary=parliamentaryTest1,
            legislative_house=legislative_houseTest1, begin='2004-01-01',
            end='2012-07-01', party=testParty1, location='PB')
        legislatureTest1.save()

        propositionTest1 = models.Proposicao()
        propositionTest1.id_prop = '5555'
        propositionTest1.sigla = 'PL'
        propositionTest1.numero = '4520'
        propositionTest1.casa_legislativa = legislative_houseTest1
        propositionTest1.save()

        votingTest1 = models.Votacao(
            id_votes=' 12345', description='Teste da votacao',
            date='1900-12-05', result='Teste', proposition=propositionTest1)
        votingTest1.save()

        voteTest1 = models.Voto(
            voting=votingTest1, legislature=legislatureTest1, option='TESTE')
        voteTest1.save()

        exportar.main()

    @classmethod
    def tearDownClass(cls):
        from util_test import flush_db
        flush_db(cls)

    def test_create_file_party(self):
        filepath = os.path.join(MODULE_DIR, 'dados/search_political_party.xml')
        self.assertTrue(os.path.isfile(filepath))

    def test_verify_file_party(self):
        invalid_value = 0
        party = models.Partido.objects.get(nome='PMDB')
        filepath = os.path.join(MODULE_DIR, 'dados/search_political_party.xml')
        file_xml = open(filepath, 'r')
        file_read = file_xml.read()
        self.assertTrue(file_read.find(party.nome) > invalid_value)
        self.assertTrue(file_read.find(str(party.numero)) > invalid_value)

    def test_create_file_legislative_house(self):
        filepath = os.path.join(MODULE_DIR, 'dados/casa_legislativa.xml')
        self.assertTrue(os.path.isfile(filepath))

    def test_verify_file_legislative_house(self):
        invalid_value = 0
        legislative_house = models.CasaLegislativa.objects.get(
            update='2012-12-31')
        filepath = os.path.join(MODULE_DIR, 'dados/casa_legislativa.xml')
        file_xml = open(filepath, 'r')

        # Transforms the xml file into a string
        file_read = file_xml.read()
        self.assertTrue(
            file_read.find(legislative_house.nome.decode("utf-8")) > invalid_value)
        self.assertTrue(file_read.find(legislative_house.nome_curto) > invalid_value)
        self.assertTrue(file_read.find(legislative_house.esfera) > invalid_value)

        # Case is less than zero the word does not exist in the string
        self.assertTrue(file_read.find('cdeb') < invalid_value)

    def test_create_file_parliamentary(self):
        filepath = os.path.join(MODULE_DIR, 'dados/parlamentar.xml')
        self.assertTrue(os.path.isfile(filepath))

    def test_verify_file_parlamentar(self):
        invalid_value = 0
        parlamentar = models.Parlamentar.objects.get(nome='Humberto Costa')
        filepath = os.path.join(MODULE_DIR, 'dados/parlamentar.xml')
        file_xml = open(filepath, 'r')
        file_read = file_xml.read()
        self.assertTrue(file_read.find(parlamentar.nome) > invalid_value)

    def test_create_file_legislature(self):
        filepath = os.path.join(MODULE_DIR, 'dados/legislatura.xml')
        self.assertTrue(os.path.isfile(filepath))

    def test_verify_file_legislature(self):
        invalid_value = 0
        legislature = models.Legislatura.objects.get(inicio='2004-01-01')
        filepath = os.path.join(MODULE_DIR, 'dados/legislatura.xml')
        file_xml = open(filepath, 'r')
        file_read = file_xml.read()
        self.assertTrue(file_read.find(legislature.localidade) > invalid_value)
        self.assertTrue(file_read.find(str(legislature.inicio)) > invalid_value)
        self.assertTrue(file_read.find(str(legislature.fim)) > invalid_value)

    def test_create_file_proposition(self):
        filepath = os.path.join(MODULE_DIR, 'dados/proposicao.xml')
        self.assertTrue(os.path.isfile(filepath))

    def teste_verify_file_proposition(self):
        invalid_value = 0
        proposition = models.Proposicao.objects.get(sigla='PL')
        filepath = os.path.join(MODULE_DIR, 'dados/proposicao.xml')
        file_xml = open(filepath, 'r')
        file_read = file_xml.read()
        self.assertTrue(file_read.find(proposition.numero) > invalid_value)
        self.assertTrue(file_read.find(proposition.id_prop) > invalid_value)

    def test_create_file_voting(self):
        filepath = os.path.join(MODULE_DIR, 'dados/votacao.xml')
        self.assertTrue(os.path.isfile(filepath))

    def test_verify_file_voting(self):
        invalid_value = 0
        voting = models.Votacao.objects.get(resultado='Teste')
        filepath = os.path.join(MODULE_DIR, 'dados/votacao.xml')
        file_xml = open(filepath, 'r')
        file_read = file_xml.read()
        self.assertTrue(file_read.find(voting.descricao) > invalid_value)
        self.assertTrue(file_read.find(str(voting.data)) > invalid_value)

    def test_verify_file_vote(self):
        invalid_value = 0
        vote = models.Voto.objects.get(opcao='TESTE')
        filepath = os.path.join(MODULE_DIR, 'dados/voto.xml')
        file_xml = open(filepath, 'r')
        file_read = file_xml.read()
        self.assertTrue(file_read.find(vote.opcao) > invalid_value)

    def test_create_file_vote(self):
        filepath = os.path.join(MODULE_DIR, 'dados/voto.xml')
        self.assertTrue(os.path.isfile(filepath))
