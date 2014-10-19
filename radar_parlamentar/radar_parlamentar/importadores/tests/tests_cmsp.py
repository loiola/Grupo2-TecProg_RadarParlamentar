# !/usr/bin/python
# coding=utf8

# Copyright (C) 2012, Eduardo Hideo
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
from importadores.cmsp import *
from importadores import cmsp
from modelagem import models
import os
import xml.etree.ElementTree as etree

XML_TEST = os.path.join(cmsp.MODULE_DIR, 'dados/cmsp/cmsp_test.xml')


class AprendizadoEtreeCase(TestCase):
    """Tests to understand the operation of etree lib"""

    def setUp(self):
        xml = """<CMSP>
                    <Votacao VotacaoID="1">
                        <Vereador NomeParlamentar="Teste_vereador"/>
                    </Votacao>
                </CMSP>
                """
        self.no_xml = etree.fromstring(xml)

    def test_of_reading_CMSP(self):
        self.assertEquals(self.no_xml.tag, "CMSP")

    def test_go_through_node(self):
        for no_filho in self.no_xml.getchildren():
            self.assertEquals(no_filho.tag, "Votacao")
            for no_neto in no_filho:
                self.assertEquals(no_neto.tag, "Vereador")

    def test_read_atribute(self):
        for no_filho in self.no_xml.getchildren():
            self.assertEquals(no_filho.get("VotacaoID"), "1")


class GeradorCMSPCase(TestCase):

    def test_generate_legislative_house(self):
        legislative_house = GeradorCasaLegislativa().generate_cmsp()
        self.assertEquals(legislative_house.nome_curto, 'cmsp')

    def test_retrieve_existing_house(self):
        legislative_house_1 = GeradorCasaLegislativa().generate_cmsp()
        legislative_house_2 = GeradorCasaLegislativa().generate_cmsp()
        self.assertEquals(legislative_house_1.pk, legislative_house_2.pk)


class ImportadorCMSPCase(TestCase):

    def setUp(self):
        legislative_house = GeradorCasaLegislativa().generate_cmsp()
        importer = ImportadorCMSP(legislative_house, True)
        self.votacao = importer.import_from(XML_TEST)[0]

    def test_import_vote(self):
        self.assertEquals(self.votacao.id_vot, '1')

    def test_parliamentary_imported(self):
        parliamentary = models.Parlamentar.objects.get(id_parlamentar='1')
        self.assertTrue(parliamentary)


class EstaticosCMSPCase(TestCase):
    """Test case os static methods of XmlCMSP"""

    def setUp(self):
        legislative_house = GeradorCasaLegislativa().generate_cmsp()
        self.xmlCMSP = XmlCMSP(legislative_house, True)

    def test_convert_valid_date(self):
        from django.utils.dateparse import parse_datetime
        date = self.xmlCMSP.convert_data("1/1/1000")
        self.assertEquals(date, parse_datetime("1000-1-1 0:0:0"))

    def test_convert_invalid_date(self):
        data = self.xmlCMSP.convert_data("1000")
        self.assertEquals(data, None)

    def test_proposition_valid_name(self):
        text = "Encontra Proposicoes como PL 1 /1000 no texto"
        draft_law = self.xmlCMSP.search_propostition_by_name(text)
        self.assertEquals(draft_law, "PL 1 /1000")

    def test_proposition_invalid_name(self):
        text = "Nao encontra proposicoes no texto"
        draft_law = self.xmlCMSP.search_propostition_by_name(text)
        self.assertEquals(draft_law, None)

    def test_extract_year_valid_proposition(self):
        proposition_name = "PL 1 /1000"
        number_and_year = self.xmlCMSP.extract_year_from_num_and_year(proposition_name)
        self.assertEquals(number_and_year, ("PL", "1", "1000"))

    def test_extract_year_invalid_proposition(self):
        proposition_name = "Nao e proposicao valida"
        number_and_year = self.xmlCMSP.extract_year_from_num_and_year(proposition_name)
        self.assertEquals(number_and_year, (None, None, None))

    def test_cmsp_mapped_vote(self):
        type_of_vote = "Sim"
        model_of_vote = self.xmlCMSP.interpret_vote(type_of_vote)
        self.assertEquals(model_of_vote, models.SIM)

    def test_cmsp_not_mapped_vote(self):
        vote = "Voto nao mapeado"
        model_of_vote = self.xmlCMSP.interpret_vote(vote)
        self.assertEquals(model_of_vote, models.ABSTENCAO)


class ModelCMSPCase(TestCase):
    """Test Case of methods that use model objects in XmlCMSP."""

    def setUp(self):
        legislative_house = GeradorCasaLegislativa().generate_cmsp()
        self.xmlCMSP = XmlCMSP(legislative_house, True)
        type(self).populate_database(legislative_house)

    @staticmethod
    def populate_database(casa):
        political_party = models.Partido(nome="PTest", numero="1")
        political_party.save()
        parliamentary = models.Parlamentar(
            id_parlamentar="1", nome="Teste_vereador")
        parliamentary.save()
        legislature = models.Legislatura(
            parlamentar=parliamentary, partido=political_party, casa_legislativa=casa)
        legislature.save()

    def test_councilman_without_political_party(self):
        councilman_in_xml = etree.fromstring(
            "<Vereador Partido=\"nao tem partido\"/>")
        political_party = self.xmlCMSP.partido(councilman_in_xml)
        self.assertEquals(
            political_party, models.Partido.objects.get(nome=models.SEM_PARTIDO))

    def test_councilman_with_political_party(self):
        councilman_in_xml = etree.fromstring("<Vereador Partido=\"PTest\"/>")
        political_party = self.xmlCMSP.partido(councilman_in_xml)
        self.assertEquals(political_party, models.Partido.objects.get(nome="PTest"))

    def test_save_existing_councilman(self):
        councilman_in_xml = etree.fromstring(
            "<Vereador IDParlamentar=\"999\" NomeParlamentar=\"Nao_consta\"/>")
        parliamentary = self.xmlCMSP.list_parliamentary(councilman_in_xml)
        self.assertEquals(
            parliamentary, models.Parlamentar.objects.get(id_parlamentar=999))

    def test_save_inexisting_legislature(self):
        councilman_in_xml = etree.fromstring(
            "<Vereador IDParlamentar=\"999\" NomeParlamentar=\"Nao_consta\" Partido=\"PTest\"/>")
        legislature = self.xmlCMSP.legislatura(councilman_in_xml)
        self.assertEquals(legislature, models.Legislatura.objects.get(
            parlamentar__id_parlamentar="999", partido__nome="PTest"))


class IdempotenciaCMSPCase(TestCase):

    # def setUp(self):

    def test_idempotencia_cmsp(self):

        legislative_house = GeradorCasaLegislativa().generate_cmsp()
        importer = ImportadorCMSP(legislative_house, False)

        # Import to the first time.
        votings = importer.import_from(XML_TEST)
        self.votacao = votings[0]

        number_legislative_house_before = models.CasaLegislativa.objects.filter(
            nome_curto='cmsp').count()
        number_votings_before = models.Votacao.objects.filter(
            proposicao__casa_legislativa=legislative_house).count()
        number_legislature_before = models.Legislatura.objects.filter(
            casa_legislativa=legislative_house).count()
        number_parliamentary_after = models.Parlamentar.objects.all().count()

        # Import again.
        self.votacao = importer.import_from(XML_TEST)[0]

        number_legislative_house_after = models.CasaLegislativa.objects.filter(
            nome_curto='cmsp').count()
        number_votings_after = models.Votacao.objects.filter(
            proposicao__casa_legislativa=legislative_house).count()
        number_legislature_after = models.Legislatura.objects.filter(
            casa_legislativa=legislative_house).count()
        number_parliamentary_after = models.Parlamentar.objects.all().count()

        self.assertEqual(number_legislative_house_before, 1)
        self.assertEqual(number_legislative_house_after, 1)
        self.assertEquals(number_votings_after, number_votings_before)
        self.assertEquals(number_legislature_after, number_legislature_before)
        self.assertEquals(number_parliamentary_after, number_parliamentary_after)
