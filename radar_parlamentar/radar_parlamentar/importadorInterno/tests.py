# !/usr/bin/python
# coding=utf8

# Copyright (C) 2013, Arthur Del Esposte, Gustavo Corrêia
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
from importadorInterno import importador_interno
from exportadores import exportar
from modelagem import models


class ImportadorInternoTest(TestCase):

    @classmethod
    def setUpClass(cls):

        # Creating dummy data in mock:
        partyTest1 = models.Partido(name='PMDB', number='40')
        partyTest2 = models.Partido(name='PT', number='13')
        partyTest3 = models.Partido(name='PSDB', number='23')

        partyTest1.save()
        partyTest2.save()
        partyTest3.save()

        parliamentarianTest1 = models.Parlamentar(
            id_parliamentary='', name='Ivandro Cunha Lima', gender='')
        parliamentarianTest2 = models.Parlamentar(
            id_parliamentary='', name='Fernando Ferro', gender='')
        parliamentarianTest3 = models.Parlamentar(
            id_parliamentary='', name='Humberto Costa', gender='')

        parliamentarianTest1.save()
        parliamentarianTest2.save()
        parliamentarianTest3.save()

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
            parliamentary=parliamentarianTest1,
            legislative_house=legislative_houseTest1, begin='2004-01-01',
            end='2012-07-01', party=partyTest1, location='PB')
        legislatureTest1.save()

        propositionTest1 = models.Proposicao()
        propositionTest1.id_prop = '5555'
        propositionTest1.sigla = 'PL'
        propositionTest1.numero = '4520'
        propositionTest1.casa_legislativa = legislative_houseTest1
        propositionTest1.save()

        votingTest1 = models.Votacao(
            id_vote=' 12345', description='Teste da votacao',
            date='1900-12-05', result='Teste', proposition=propositionTest1)
        votingTest1.save()

        voteTest1 = models.Voto(
            votacao=votingTest1, legislature=legislatureTest1, option='TESTE')
        voteTest1.save()

        # Exporting the mocks's data to XMLs:
        exportar.serialize_partido()
        exportar.serialize_parlamentar()
        exportar.serialize_casa_legislativa()
        exportar.serialize_legislatura()
        exportar.serialize_proposicao()
        exportar.serialize_votacao()
        exportar.serialize_voto()

        # Deleting records of mock:
        partyTest1.delete()
        partyTest2.delete()
        partyTest3.delete()

        parliamentarianTest1.delete()
        parliamentarianTest2.delete()
        parliamentarianTest3.delete()

        legislative_houseTest1.delete()
        legislative_houseTest2.delete()

        legislatureTest1.delete()

        propositionTest1.delete()

        votingTest1.delete()

        voteTest1.delete()

    @classmethod
    def tearDownClass(cls):
        from util_test import flush_db
        flush_db(cls)

    def test_deserialize_party(self):

        importador_interno.deserialize_partido()
        partyPMDB = models.Partido.objects.filter(name='PMDB')
        self.assertEquals(partyPMDB[0].numero, 40)

    def test_deserialize_parliamentary(self):

        importador_interno.deserialize_parlamentar()
        parliamentarian = models.Parlamentar.objects.filter(
            name='Ivandro Cunha Lima')
        self.assertEquals(parliamentarian[0].nome, 'Ivandro Cunha Lima')

    def test_deserialize_legislative_house(self):

        importador_interno.deserialize_casa_legislativa()
        legislative_house = models.CasaLegislativa.objects.filter(
            short_name='cdep')
        self.assertEquals(legislative_house[0].nome, 'Camara dos Deputados')

    def test_deserialize_legislature(self):

        importador_interno.main()
        parliamentarian = models.Parlamentar.objects.filter(
            name='Ivandro Cunha Lima')
        legislature = models.Legislatura.objects.filter(
            parliamentary=parliamentarian[0])
        self.assertEquals(
            legislature[0].parlamentar.nome, 'Ivandro Cunha Lima')

    def test_deserialize_proposition(self):

        importador_interno.main()
        propostion = models.Proposicao.objects.filter(number='4520')
        self.assertEquals(propostion[0].sigla, 'PL')

    def test_deserialize_voting(self):

        importador_interno.main()
        voting = models.Votacao.objects.filter(id_vote='12345')
        self.assertEquals(str(voting[0].data), '1900-12-05')

    def test_deserialize_vote(self):

        importador_interno.main()
        vote = models.Voto.objects.filter(option='TESTE')
        self.assertEquals(vote[0].opcao, 'TESTE')

    def test_importa_legislative_house(self):

        models.CasaLegislativa.remove_house('cmsp')
        models.CasaLegislativa.remove_house('cdep')

        importador_interno.importa_casa_legislativa('cdep')
        legislative_house = models.CasaLegislativa.objects.filter(
            short_name='cdep')
        self.assertEquals(legislative_house[0].nome, 'Camara dos Deputados')

        cmsp_house = models.CasaLegislativa.objects.filter(short_name='cmsp')
        self.assertEquals(cmsp_house[0].nome, 'Camara Municipal de Sao Paulo')
