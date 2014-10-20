# coding=utf8

# Copyright (C) 2012, Leonardo Leite, Eduardo Hideo, Diego Rabatone
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
import datetime
import models
import utils
from util_test import flush_db
from django.utils.dateparse import parse_datetime
from modelagem.models import MUNICIPAL, FEDERAL, ESTADUAL, BIENIO


class MandatoListsTest(TestCase):

    def test_get_municipal_mandates(self):

        # Start date of the mandate
        mandate_initial_date = datetime.date(2008, 10, 10)

        # End date of the mandate
        mandate_final_date = datetime.date(2013, 10, 10)

        # Lists of mandates
        mandate_lists = utils.MandatoLists()

        # Mandates that fall within a certain period (start date and end date)
        # in some of the spheres (municipal, state or federal)
        mandates = mandate_lists.get_mandates(MUNICIPAL, mandate_initial_date, mandate_final_date)

        self.assertEquals(len(mandates), 3)
        self.assertEquals(mandates[0].year, 2005)
        self.assertEquals(mandates[1].year, 2009)
        self.assertEquals(mandates[2].year, 2013)
        for mandato in mandates:
            self.assertEquals(mandato.day, 1)
            self.assertEquals(mandato.month, 1)

    def test_get_just_one_municipal_mandate(self):

        # Start date of the mandate
        mandate_initial_date = parse_datetime('2009-10-10 0:0:0')

        # End date of the mandate
        mandate_final_date = parse_datetime('2012-10-10 0:0:0')

        # Lists of mandates
        mandate_lists = utils.MandatoLists()

        # Mandates that fall within a certain period (start date and end date)
        # in some of the spheres (municipal, state or federal)
        mandates = mandate_lists.get_mandates(MUNICIPAL, mandate_initial_date, mandate_final_date)

        self.assertEquals(len(mandates), 1)
        self.assertEquals(mandates[0].year, 2009)

    def test_get_federal_mandates(self):
        self._test_get_federal_or_state_mandates(FEDERAL)

    def test_get_state_mandates(self):
        self._test_get_federal_or_state_mandates(ESTADUAL)

    def _test_get_federal_or_state_mandates(self, esfera):

        # Start date of the mandate
        mandate_initial_date = datetime.date(2008, 10, 10)

        # End date of the mandate
        mandate_final_date = datetime.date(2015, 10, 10)

        # Lists of mandates
        mandate_lists = utils.MandatoLists()

        # Mandates that fall within a certain period (start date and end date)
        # in some of the spheres (municipal, state or federal)
        mandates = mandate_lists.get_mandates(esfera, mandate_initial_date, mandate_final_date)

        self.assertEquals(len(mandates), 3)
        self.assertEquals(mandates[0].year, 2007)
        self.assertEquals(mandates[1].year, 2011)
        self.assertEquals(mandates[2].year, 2015)

        for mandato in mandates:
            self.assertEquals(mandato.day, 1)
            self.assertEquals(mandato.month, 1)


class PeriodosRetrieverTest(TestCase):

    @classmethod
    def setUpClass(cls):

        # Importer of French Convention
        importer = conv.ImportadorConvencao()
        importer.import_data()

    @classmethod
    def tearDownClass(cls):
        flush_db(cls)

    def setUp(self):
        self.conv = models.CasaLegislativa.objects.get(nome_curto='conv')

    def test_legislative_house_annual_periods(self):

        # Stores the objects of conv and the year from models
        retriever = utils.PeriodosRetriever(self.conv, models.ANO)

        # Stores the retriever periods
        retriever_periods = retriever.get_periods()

        self.assertEquals(len(retriever_periods), 1)
        self.assertEqual(retriever_periods[0].string, '1989')
        self.assertEqual(retriever_periods[0].quantidade_votacoes, 8)

    def test_legislative_house_monthly_periods(self):

        # Stores the objects of conv and the month from models
        retriever = utils.PeriodosRetriever(self.conv, models.MES)

        # Stores the retriever periods
        retriever_periods = retriever.get_periods()

        self.assertEquals(len(retriever_periods), 2)
        self.assertEqual(retriever_periods[0].string, '1989 Fev')
        self.assertEqual(retriever_periods[0].quantidade_votacoes, 4)
        self.assertEqual(retriever_periods[1].string, '1989 Out')
        self.assertEqual(retriever_periods[1].quantidade_votacoes, 4)

    def test_legislative_house_semiannual_periods(self):

        # Stores the objects of conv and the semester from models
        retriever = utils.PeriodosRetriever(self.conv, models.SEMESTRE)

        # Stores the retriever periods
        retriever_periods = retriever.get_periods()

        self.assertEquals(len(retriever_periods), 2)

        # Temporary variable that stores the initial period of conv legislative house
        conv_period = retriever_periods[0].ini

        self.assertEqual(1989, conv_period.year)
        self.assertEqual(1, conv_period.month)

        # Temporary variable that stores the final period of conv legislative house
        conv_period = retriever_periods[0].fim

        self.assertEqual(1989, conv_period.year)
        self.assertEqual(6, conv_period.month)

        # Temporary variable that stores the initial period of conv legislative house
        conv_period = retriever_periods[1].ini

        self.assertEqual(1989, conv_period.year)
        self.assertEqual(7, conv_period.month)

        # Temporary variable that stores the final period of conv legislative house
        conv_period = retriever_periods[1].fim

        self.assertEqual(1989, conv_period.year)
        self.assertEqual(12, conv_period.month)
        self.assertEqual(retriever_periods[0].string, '1989 1o Semestre')
        self.assertEqual(retriever_periods[1].string, '1989 2o Semestre')

    def test_municipal_period_polls_must_not_contain_two_mandates(self):
        self._test_periods_in_two_dates(2008, 2009, MUNICIPAL, BIENIO, 2)

    def test_municipal_period_must_be_in_a_mandate(self):
        self._test_periods_in_two_dates(2009, 2010, MUNICIPAL, BIENIO, 1)

    def test_begin_of_municipal_period_must_match_begin_of_mandate(self):
        self._test_periods_in_two_dates(2010, 2011, MUNICIPAL, BIENIO, 2)

    def test_federal_period_must_not_contain_votes_of_two_mandates(self):
        self._test_periods_in_two_dates(2010, 2011, FEDERAL, BIENIO, 2)

    def test_state_period_must_not_contain_votes_of_two_mandates(self):
        self._test_periods_in_two_dates(2010, 2011, ESTADUAL, BIENIO, 2)

    def test_federal_period_must_be_ia_a_mandate(self):
        self._test_periods_in_two_dates(2011, 2012, FEDERAL, BIENIO, 1)

    def test_begin_of_federal_period_must_match_begin_mandate(self):
        self._test_periods_in_two_dates(2012, 2013, FEDERAL, BIENIO, 2)

    def _test_periods_in_two_dates(self, ano_ini, ano_fim, esfera,
                                     periodicidade, expected_periodos_len):

        # Receives the start date for testing
        A_DATE = datetime.date(ano_ini, 02, 02)

        # Receives the final date for testing
        OTHER_DATE = datetime.date(ano_fim, 10, 02)

        # Receives all objects of the Voting from models
        votings = models.Votacao.objects.all()

        # Receives half of the number of votes
        half_of_votings_amount = len(votings) / 2

        # Receives original dates of periods
        original_dates = {}

        # Receives original sphere of  conv legislative house
        original_sphere = self.conv.esfera

        self.conv.esfera = esfera

        for i in range(0, half_of_votings_amount):
            voting_list = votings[i]
            original_dates[voting_list.id] = voting_list.data
            voting_list.data = A_DATE
            voting_list.save()
        for i in range(half_of_votings_amount, len(votings)):
            voting_list = votings[i]
            original_dates[voting_list.id] = voting_list.data
            voting_list.data = OTHER_DATE
            voting_list.save()

        # Stores the objects of conv and the periodicity
        retriever = utils.PeriodosRetriever(self.conv, periodicidade)

        # Stores the retriever periods
        retriever_periods = retriever.get_periods()

        self.assertEquals(len(retriever_periods), expected_periodos_len)
        self._restore(original_sphere, votings, original_dates)

    def _restore(self, esfera_original, votacoes, datas_originais):
        self.conv.esfera = esfera_original
        self.conv.save()
        for voting_list in votacoes:
            voting_list.data = datas_originais[voting_list.id]
            voting_list.save()

    def test_legislative_house_periods_with_no_votes_list(self):

        # Receives objects of legislative house where name is equal to casa_nova to
        # perform home test without legislative voting list
        new_house = models.CasaLegislativa(nome="Casa Nova")

        # Stores the objects of new house and the year from models
        retriever = utils.PeriodosRetriever(new_house, models.ANO)

        # Stores the retriever periods
        retriever_periods = retriever.get_periods()

        self.assertEquals(len(retriever_periods), 0)


class ModelsTest(TestCase):

    @classmethod
    def setUpClass(cls):

        # Importer of French Convention
        importer = conv.ImportadorConvencao()

        importer.import_data()

    @classmethod
    def tearDownClass(cls):
        flush_db(cls)

    def test_party(self):

        # Receives the objects o PT party
        pt_party = models.Partido.from_name('PT')

        self.assertEquals(pt_party.numero, 13)
        self.assertEquals(pt_party.cor, '#FF0000')

        # Receives the objects o PSDB party
        psdb_party = models.Partido.from_number(45)
        self.assertEquals(psdb_party.nome, 'PSDB')
        self.assertEquals(psdb_party.cor, '#0059AB')

    def test_party_from_None_name(self):

        # Receives the name of party equals none
        nome = None

        # Receives the party by party name
        partido = models.Partido.from_name(nome)

        self.assertIsNone(partido)

    def test_get_no_party(self):

        # Receives the objects from Partido whre tha party name is equals
        # SEM_PARTIDO
        no_party = models.Partido.get_no_party()

        self.assertEquals(no_party.nome, 'Sem search_political_party')
        self.assertEquals(no_party.numero, 0)
        self.assertEquals(no_party.cor, '#000000')

    def test_legislative_house_parties(self):

        # Receives the objects of CasaLegislativa where the short name is conv
        conv_legislative_house = models.CasaLegislativa.objects.get(nome_curto='conv')

        # Receives the partidos of conv legislative house
        partidos = conv_legislative_house.parties()

        self.assertEquals(len(partidos), 3)

        # Receives the name of partidos of conv legislative house
        conv_party_names = [p.nome for p in partidos]

        self.assertTrue(conv.JACOBINOS in conv_party_names)
        self.assertTrue(conv.GIRONDINOS in conv_party_names)
        self.assertTrue(conv.MONARQUISTAS in conv_party_names)

    def test_should_find_legislature(self):

        # Receives the results of the search of legislature by date
        search_legislature_by_date = datetime.date(1989, 07, 14)

        try:
            leg = models.Legislatura.find_legislature(search_legislature_by_date, 'Pierre')
            self.assertTrue(leg is not None)
        except ValueError:
            self.fail('Legislatura não encontrada')

    def test_should_not_find_legislature(self):

        # Receives the results of the search of legislature by date
        search_legislature_by_date = datetime.date(1900, 07, 14)

        try:
            models.Legislatura.find_legislature(search_legislature_by_date, 'Pierre')
            self.fail('Legislatura não deveria ter sido encontrada')
        except:
            self.assertTrue(True)

    def test_remove_house(self):

        # Receives objects of Partido for inserting data to removal house test
        partyTest1 = models.Partido()

        partyTest1.nome = 'PA'
        partyTest1.numero = '01'
        partyTest1.cor = '#FFFAAA'
        partyTest1.save()


        # Receives objects of Partido for inserting data to removal house test
        partyTest2 = models.Partido()

        partyTest2.nome = 'PB'
        partyTest2.numero = '02'
        partyTest1.cor = '#FFFFFF'
        partyTest2.save()


        # Receives objects of Parlamentar for inserting data to removal house test
        parliamentaryTest1 = models.Parlamentar()

        parliamentaryTest1.id_parlamentar = ''
        parliamentaryTest1.nome = 'Pierre'
        parliamentaryTest1.genero = ''
        parliamentaryTest1.save()


        # Receives objects of Parlamentar for inserting data to removal house test
        parliamentaryTest2 = models.Parlamentar()

        parliamentaryTest2.id_parlamentar = ''
        parliamentaryTest2.nome = 'Napoleao'
        parliamentaryTest2.genero = ''
        parliamentaryTest2.save()


        # Receives objects of CasaLegislativa for inserting data to removal house test
        lesgilativeHouseTest1 = models.CasaLegislativa()

        lesgilativeHouseTest1.nome = 'Casa1'
        lesgilativeHouseTest1.nome_curto = 'cs1'
        lesgilativeHouseTest1.esfera = 'FEDERAL'
        lesgilativeHouseTest1.local = ''
        lesgilativeHouseTest1.atualizacao = '2012-06-01'
        lesgilativeHouseTest1.save()

        # Receives objects of CasaLegislativa for inserting data to removal house test
        lesgilativeHouseTest2 = models.CasaLegislativa()

        lesgilativeHouseTest2.nome = 'Casa2'
        lesgilativeHouseTest2.nome_curto = 'cs2'
        lesgilativeHouseTest2.esfera = 'MUNICIPAL'
        lesgilativeHouseTest2.local = 'local2'
        lesgilativeHouseTest2.atualizacao = '2012-12-31'
        lesgilativeHouseTest2.save()


        # Receives objects of Legislature for inserting data to removal house test
        legislatureTest1 = models.Legislatura()

        legislatureTest1.parlamentar = parliamentaryTest1
        legislatureTest1.casa_legislativa = lesgilativeHouseTest1
        legislatureTest1.inicio = '2013-01-01'
        legislatureTest1.fim = '2013-02-01'
        legislatureTest1.partido = partyTest1
        legislatureTest1.localidade = 'PB'
        legislatureTest1.save()

        # Receives objects of Legislature for inserting data to removal house test
        legislatureTest2 = models.Legislatura()

        legislatureTest2.parlamentar = parliamentaryTest2
        legislatureTest2.casa_legislativa = lesgilativeHouseTest2
        legislatureTest2.inicio = '2013-01-02'
        legislatureTest2.fim = '2013-02-02'
        legislatureTest2.partido = partyTest2
        legislatureTest2.localidade = 'PR'
        legislatureTest2.save()


        # Receives objects of Proposicao for inserting data to removal house test
        propositionTest1 = models.Proposicao()

        propositionTest1.id_prop = '0001'
        propositionTest1.sigla = 'PR1'
        propositionTest1.numero = '0001'
        propositionTest1.ano = '2013'
        propositionTest1.data_apresentacao = '2013-01-02'
        propositionTest1.casa_legislativa = lesgilativeHouseTest1
        propositionTest1.save()

        # Receives objects of Proposicao for inserting data to removal house test
        propositionTest2 = models.Proposicao()

        propositionTest2.id_prop = '0002'
        propositionTest2.sigla = 'PR2'
        propositionTest2.numero = '0002'
        propositionTest2.ano = '2013'
        propositionTest2.data_apresentacao = '2013-02-02'
        propositionTest2.casa_legislativa = lesgilativeHouseTest2
        propositionTest2.save()

        # Receives objects of Votaçao for inserting data to removal house test
        votingTest1 = models.Votacao(
            id_vot=' 12345', descricao='Teste da votacao',
            data='1900-12-05', resultado='Teste', proposicao=propositionTest1)

        votingTest1.save()

        # Receives objects of Votaçao for inserting data to removal house test
        voteTest1 = models.Voto(
            votacao=votingTest1, legislatura=legislatureTest1, opcao='TESTE')

        voteTest1.save()

        # Receives all objects of Partido from models before removal
        before_party_objects = models.Partido.objects.all()

        # Receives all objects of Parlamentar from models before removal
        before_parliamentary_objects = models.Parlamentar.objects.all()

        # Receives all objects of CasaLegislativa from models before removal
        before_house_objects = models.CasaLegislativa.objects.all()

        # Receives all objects of Legislatura from models before removal
        before_legislature_objects = models.Legislatura.objects.all()

        # Receives all objects of Proposicao from models before removal
        before_proposition_objects = models.Proposicao.objects.all()

        # Receives all objects of Voto from models before removal
        before_vote_objects = models.Voto.objects.all()

        # Receives all objects of Votacao from models before removal
        before_voting_objects = models.Votacao.objects.all()

        # Receives the names of partidos before removal
        party_names = [p.nome for p in before_party_objects]

        self.assertTrue('PA' in party_names)
        self.assertTrue('PB' in party_names)

        # Receives the names of parliamentaries before removal
        parliamentary_names = [pl.nome for pl in before_parliamentary_objects]

        self.assertTrue('Pierre' in parliamentary_names)
        self.assertTrue('Napoleao' in parliamentary_names)

        # Receives the names of houses before removal
        house_names = [c.nome for c in before_house_objects]

        self.assertTrue('Casa1' in house_names)
        self.assertTrue('Casa2' in house_names)


        # Receives the names of legislaturas before removal
        legislature_names = [l.localidade for l in before_legislature_objects]

        self.assertTrue('PB' in legislature_names)
        self.assertTrue('PR' in legislature_names)

        # Receives the names of ppropositions before removal
        proposition_names = [lg.sigla for lg in before_proposition_objects]

        self.assertTrue('PR1' in proposition_names)
        self.assertTrue('PR2' in proposition_names)


        # Receives the names of votes before removal
        vote_names = [v.votacao for v in before_vote_objects]

        self.assertTrue(votingTest1 in vote_names)

        # Receives the names of voting before removal
        voting_names = [vt.id_vot for vt in before_voting_objects]

        self.assertTrue(' 12345' in voting_names)

        # Trying to delete a house that does not exist
        models.CasaLegislativa.remove_house('casa_qualquer')
        models.CasaLegislativa.remove_house('cs1')

        # Receives all objects of Partido from models after removal
        after_party_objects = models.Partido.objects.all()

        # Receives all objects of Parlamentar from models after removal
        after_parliamentary_objects = models.Parlamentar.objects.all()

        # Receives all objects of CasaLegislativa from models after removal
        after_house_objects = models.CasaLegislativa.objects.all()

        # Receives all objects of Legislatura from models after removal
        after_legislature_objects = models.Legislatura.objects.all()

        # Receives all objects of Propositcao from models after removal
        after_proposition_objects = models.Proposicao.objects.all()

        # Receives all objects of Voto from models after removal
        after_vote_objects = models.Voto.objects.all()

        # Receives all objects of Votacao from models after removal
        after_voting_objects = models.Votacao.objects.all()

        # Receives the names of partidos after removal
        party_names = [p.nome for p in after_party_objects]

        self.assertTrue('PA' in party_names)
        self.assertTrue('PB' in party_names)

        # Receives the names of parliamentaries after removal
        parliamentary_names = [pl.nome for pl in after_parliamentary_objects]

        self.assertTrue('Pierre' in parliamentary_names)
        self.assertTrue('Napoleao' in parliamentary_names)

        # Receives the names of houses after removal
        house_names = [c.nome for c in after_house_objects]

        self.assertFalse('Casa1' in house_names)
        self.assertTrue('Casa2' in house_names)

        # Receives the names of legislaturas after removal
        legislature_names = [l.localidade for l in after_legislature_objects]

        self.assertFalse('PB' in legislature_names)
        self.assertTrue('PR' in legislature_names)

        # Receives the names of propositions after removal
        proposition_names = [lg.sigla for lg in after_proposition_objects]

        self.assertFalse('PR1' in proposition_names)
        self.assertTrue('PR2' in proposition_names)

        # Receives the names of votes after removal
        vote_names = [v.votacao for v in after_vote_objects]

        self.assertFalse(votingTest1 in vote_names)

        # Receives the names of voting after removal
        voting_names = [vt.id_vot for vt in after_voting_objects]

        self.assertFalse(' 12345' in voting_names)


class StringUtilsTest(TestCase):

    def test_transforms_text_in_a_string_list_empty_text_case(self):

        # Receives the result of transforma_texto_em_lista_de_string() method
        # in StringUtils class to test with blank text
        string_list = utils.StringUtils.transforms_text_in_string_list(
            "")

        self.assertEquals(0, len(string_list))

    def test_transforms_text_in_a_string_list_null_text_case(self):

        # Receives the result of transforma_texto_em_lista_de_string() method
        # in StringUtils class to test with none text
        string_list = utils.StringUtils.transforms_text_in_string_list(
            None)

        self.assertEquals(0, len(string_list))

    def test_transforms_text_in_a_string_list_with_text_case(self):

        # Receives the result of transforma_texto_em_lista_de_string() method
        # in StringUtils class to test with text
        string_list = utils.StringUtils.transforms_text_in_string_list(
            "educação, saúde, desmatamento")

        self.assertEquals(3, len(string_list))
        self.assertEquals("educação", string_list[0])
        self.assertEquals("saúde", string_list[1])
        self.assertEquals("desmatamento", string_list[2])
