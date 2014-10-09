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

        testParty1 = models.Partido(nome='PMDB', numero='40')
        testParty2 = models.Partido(nome='PT', numero='13')
        partyTest3 = models.Partido(nome='PSDB', numero='23')
        testParty1.save()
        testParty2.save()
        partyTest3.save()

        parliamentaryTest1 = models.Parlamentar(
            id_parlamentar='', nome='Ivandro Cunha Lima', genero='')
        parliamentaryTest2 = models.Parlamentar(
            id_parlamentar='', nome='Fernando Ferro', genero='')
        parliamentaryTest3 = models.Parlamentar(
            id_parlamentar='', nome='Humberto Costa', genero='')

        parliamentaryTest1.save()
        parliamentaryTest2.save()
        parliamentaryTest3.save()

        legislative_houseTest1 = models.CasaLegislativa(
            nome='Camara dos Deputados', nome_curto='cdep', esfera='FEDERAL',
            local='', atualizacao='2012-06-01')

        legislative_houseTest2 = models.CasaLegislativa(
            nome='Camara Municipal de Sao Paulo', nome_curto='cmsp',
            esfera='MUNICIPAL', local='Sao Paulo - SP',
            atualizacao='2012-12-31')

        legislative_houseTest1.save()
        legislative_houseTest2.save()

        legislatureTest1 = models.Legislatura(
            parlamentar=parliamentaryTest1,
            casa_legislativa=legislative_houseTest1, inicio='2004-01-01',
            fim='2012-07-01', partido=testParty1, localidade='PB')
        legislatureTest1.save()

        propositionTest1 = models.Proposicao()
        propositionTest1.id_prop = '5555'
        propositionTest1.sigla = 'PL'
        propositionTest1.numero = '4520'
        propositionTest1.casa_legislativa = legislative_houseTest1
        propositionTest1.save()

        votingTest1 = models.Votacao(
            id_vot=' 12345', descricao='Teste da votacao',
            data='1900-12-05', resultado='Teste', proposicao=propositionTest1)
        votingTest1.save()

        voteTest1 = models.Voto(
            votacao=votingTest1, legislatura=legislatureTest1, opcao='TESTE')
        voteTest1.save()

        exportar.main()

    @classmethod
    def tearDownClass(cls):
        from util_test import flush_db
        flush_db(cls)

    def test_create_file_partido(self):
        filepath = os.path.join(MODULE_DIR, 'dados/search_political_party.xml')
        self.assertTrue(os.path.isfile(filepath))

    def test_verify_file_partido(self):
        party = models.Partido.objects.get(nome='PMDB')
        filepath = os.path.join(MODULE_DIR, 'dados/search_political_party.xml')
        file_xml = open(filepath, 'r')
        file_read = file_xml.read()
        self.assertTrue(file_read.find(party.nome) > 0)
        self.assertTrue(file_read.find(str(party.numero)) > 0)

    def test_create_file_casa_legislativa(self):
        filepath = os.path.join(MODULE_DIR, 'dados/casa_legislativa.xml')
        self.assertTrue(os.path.isfile(filepath))

    def test_verify_file_casa_legislativa(self):
        legislative_house = models.CasaLegislativa.objects.get(
            atualizacao='2012-12-31')
        filepath = os.path.join(MODULE_DIR, 'dados/casa_legislativa.xml')
        file_xml = open(filepath, 'r')

        # Transforms the xml file into a string
        file_read = file_xml.read()
        self.assertTrue(
            file_read.find(legislative_house.nome.decode("utf-8")) > 0)
        self.assertTrue(file_read.find(legislative_house.nome_curto) > 0)
        self.assertTrue(file_read.find(legislative_house.esfera) > 0)

        # Case is less than zero the word does not exist in the string
        self.assertTrue(file_read.find('cdeb') < 0)

    def test_create_file_parlamentar(self):
        filepath = os.path.join(MODULE_DIR, 'dados/parlamentar.xml')
        self.assertTrue(os.path.isfile(filepath))

    def test_verify_file_parlamentar(self):
        parlamentar = models.Parlamentar.objects.get(nome='Humberto Costa')
        filepath = os.path.join(MODULE_DIR, 'dados/parlamentar.xml')
        file_xml = open(filepath, 'r')
        file_read = file_xml.read()
        self.assertTrue(file_read.find(parlamentar.nome) > 0)

    def test_create_file_legislatura(self):
        filepath = os.path.join(MODULE_DIR, 'dados/legislatura.xml')
        self.assertTrue(os.path.isfile(filepath))

    def test_verify_file_legislatura(self):
        legislature = models.Legislatura.objects.get(inicio='2004-01-01')
        filepath = os.path.join(MODULE_DIR, 'dados/legislatura.xml')
        file_xml = open(filepath, 'r')
        file_read = file_xml.read()
        self.assertTrue(file_read.find(legislature.localidade) > 0)
        self.assertTrue(file_read.find(str(legislature.inicio)) > 0)
        self.assertTrue(file_read.find(str(legislature.fim)) > 0)

    def test_create_file_proposicao(self):
        filepath = os.path.join(MODULE_DIR, 'dados/proposicao.xml')
        self.assertTrue(os.path.isfile(filepath))

    def teste_verify_file_proposicao(self):
        proposition = models.Proposicao.objects.get(sigla='PL')
        filepath = os.path.join(MODULE_DIR, 'dados/proposicao.xml')
        file_xml = open(filepath, 'r')
        file_read = file_xml.read()
        self.assertTrue(file_read.find(proposition.numero) > 0)
        self.assertTrue(file_read.find(proposition.id_prop) > 0)

    def test_create_file_votacao(self):
        filepath = os.path.join(MODULE_DIR, 'dados/votacao.xml')
        self.assertTrue(os.path.isfile(filepath))

    def test_verify_file_votacao(self):
        voting = models.Votacao.objects.get(resultado='Teste')
        filepath = os.path.join(MODULE_DIR, 'dados/votacao.xml')
        file_xml = open(filepath, 'r')
        file_read = file_xml.read()
        self.assertTrue(file_read.find(voting.descricao) > 0)
        self.assertTrue(file_read.find(str(voting.data)) > 0)

    def test_verify_file_voto(self):
        vote = models.Voto.objects.get(opcao='TESTE')
        filepath = os.path.join(MODULE_DIR, 'dados/voto.xml')
        file_xml = open(filepath, 'r')
        file_read = file_xml.read()
        self.assertTrue(file_read.find(vote.opcao) > 0)

    def test_create_file_voto(self):
        filepath = os.path.join(MODULE_DIR, 'dados/voto.xml')
        self.assertTrue(os.path.isfile(filepath))
