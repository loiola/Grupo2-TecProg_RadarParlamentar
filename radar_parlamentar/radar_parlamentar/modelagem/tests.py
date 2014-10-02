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

    def test_get_mandatos_municipais(self):
        mandate_initial_date = datetime.date(2008, 10, 10)
        mandate_final_date = datetime.date(2013, 10, 10)
        mandate_lists = utils.MandatoLists()
        mandates = mandate_lists.get_mandatos(MUNICIPAL, mandate_initial_date, mandate_final_date)
        self.assertEquals(len(mandates), 3)
        self.assertEquals(mandates[0].year, 2005)
        self.assertEquals(mandates[1].year, 2009)
        self.assertEquals(mandates[2].year, 2013)
        for mandato in mandates:
            self.assertEquals(mandato.day, 1)
            self.assertEquals(mandato.month, 1)

    def test_get_mandatos_municipais_soh_um(self):
        mandate_initial_date = parse_datetime('2009-10-10 0:0:0')
        mandate_final_date = parse_datetime('2012-10-10 0:0:0')
        mandate_lists = utils.MandatoLists()
        mandates = mandate_lists.get_mandatos(MUNICIPAL, mandate_initial_date, mandate_final_date)
        self.assertEquals(len(mandates), 1)
        self.assertEquals(mandates[0].year, 2009)

    def test_get_mandatos_federais(self):
        self._test_get_mandatos_federais_ou_estaduais(FEDERAL)

    def test_get_mandatos_estaduais(self):
        self._test_get_mandatos_federais_ou_estaduais(ESTADUAL)

    def _test_get_mandatos_federais_ou_estaduais(self, esfera):
        mandate_initial_date = datetime.date(2008, 10, 10)
        mandate_final_date = datetime.date(2015, 10, 10)
        mandate_lists = utils.MandatoLists()
        mandates = mandate_lists.get_mandatos(esfera, mandate_initial_date, mandate_final_date)
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
        importer = conv.ImportadorConvencao()
        importer.importar()

    @classmethod
    def tearDownClass(cls):
        flush_db(cls)

    def setUp(self):
        self.conv = models.CasaLegislativa.objects.get(nome_curto='conv')

    def test_casa_legislativa_periodos_anuais(self):
        retriever = utils.PeriodosRetriever(self.conv, models.ANO)
        retriever_periods = retriever.get_periodos()
        self.assertEquals(len(retriever_periods), 1)
        self.assertEqual(retriever_periods[0].string, '1989')
        self.assertEqual(retriever_periods[0].quantidade_votacoes, 8)

    def test_casa_legislativa_periodos_mensais(self):
        retriever = utils.PeriodosRetriever(self.conv, models.MES)
        retriever_periods = retriever.get_periodos()
        self.assertEquals(len(retriever_periods), 2)
        self.assertEqual(retriever_periods[0].string, '1989 Fev')
        self.assertEqual(retriever_periods[0].quantidade_votacoes, 4)
        self.assertEqual(retriever_periods[1].string, '1989 Out')
        self.assertEqual(retriever_periods[1].quantidade_votacoes, 4)

    def test_casa_legislativa_periodos_semestrais(self):
        retriever = utils.PeriodosRetriever(self.conv, models.SEMESTRE)
        retriever_periods = retriever.get_periodos()
        self.assertEquals(len(retriever_periods), 2)
        conv_period = retriever_periods[0].ini
        self.assertEqual(1989, conv_period.year)
        self.assertEqual(1, conv_period.month)
        conv_period = retriever_periods[0].fim
        self.assertEqual(1989, conv_period.year)
        self.assertEqual(6, conv_period.month)
        conv_period = retriever_periods[1].ini
        self.assertEqual(1989, conv_period.year)
        self.assertEqual(7, conv_period.month)
        conv_period = retriever_periods[1].fim
        self.assertEqual(1989, conv_period.year)
        self.assertEqual(12, conv_period.month)
        self.assertEqual(retriever_periods[0].string, '1989 1o Semestre')
        self.assertEqual(retriever_periods[1].string, '1989 2o Semestre')

    def test_periodo_municipal_nao_deve_conter_votacoes_de_dois_mandatos(self):
        self._test_periodos_em_duas_datas(2008, 2009, MUNICIPAL, BIENIO, 2)

    def test_periodo_municipal_deve_estar_em_um_mandato(self):
        self._test_periodos_em_duas_datas(2009, 2010, MUNICIPAL, BIENIO, 1)

    def test_inicio_de_periodo_municipal_deve_coincidir_com_inicio_mandato(self):
        self._test_periodos_em_duas_datas(2010, 2011, MUNICIPAL, BIENIO, 2)

    def test_periodo_federal_nao_deve_conter_votacoes_de_dois_mandatos(self):
        self._test_periodos_em_duas_datas(2010, 2011, FEDERAL, BIENIO, 2)

    def test_periodo_estadual_nao_deve_conter_votacoes_de_dois_mandatos(self):
        self._test_periodos_em_duas_datas(2010, 2011, ESTADUAL, BIENIO, 2)

    def test_periodo_federal_deve_estar_em_um_mandato(self):
        self._test_periodos_em_duas_datas(2011, 2012, FEDERAL, BIENIO, 1)

    def test_inicio_de_periodo_federal_deve_coincidir_com_inicio_mandato(self):
        self._test_periodos_em_duas_datas(2012, 2013, FEDERAL, BIENIO, 2)

    def _test_periodos_em_duas_datas(self, ano_ini, ano_fim, esfera,
                                     periodicidade, expected_periodos_len):
        A_DATE = datetime.date(ano_ini, 02, 02)
        OTHER_DATE = datetime.date(ano_fim, 10, 02)
        votings = models.Votacao.objects.all()
        half_of_votings_amount = len(votings) / 2
        original_dates = {}  # votacao.id => data
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
        retriever = utils.PeriodosRetriever(self.conv, periodicidade)
        retriever_periods = retriever.get_periodos()
        self.assertEquals(len(retriever_periods), expected_periodos_len)
        self._restore(original_sphere, votings, original_dates)

    def _restore(self, esfera_original, votacoes, datas_originais):
        self.conv.esfera = esfera_original
        self.conv.save()
        for v in votacoes:
            v.data = datas_originais[v.id]
            v.save()

    def test_casa_legislativa_periodos_sem_lista_votacoes(self):
        new_house = models.CasaLegislativa(nome="Casa Nova")
        retriever = utils.PeriodosRetriever(new_house, models.ANO)
        retriever_periods = retriever.get_periodos()
        self.assertEquals(len(retriever_periods), 0)


class ModelsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        importer = conv.ImportadorConvencao()
        importer.importar()

    @classmethod
    def tearDownClass(cls):
        flush_db(cls)

    def test_partido(self):
        pt_party = models.Partido.from_nome('PT')
        self.assertEquals(pt_party.numero, 13)
        self.assertEquals(pt_party.cor, '#FF0000')
        psdb_party = models.Partido.from_numero(45)
        self.assertEquals(psdb_party.nome, 'PSDB')
        self.assertEquals(psdb_party.cor, '#0059AB')

    def test_partido_from_nome_None(self):
        nome = None
        partido = models.Partido.from_nome(nome)
        self.assertIsNone(partido)

    def test_get_sem_partido(self):
        no_party = models.Partido.get_sem_partido()
        self.assertEquals(no_party.nome, 'Sem partido')
        self.assertEquals(no_party.numero, 0)
        self.assertEquals(no_party.cor, '#000000')

    def test_casa_legislativa_partidos(self):
        conv_legislative_house = models.CasaLegislativa.objects.get(nome_curto='conv')
        partidos = conv_legislative_house.partidos()
        self.assertEquals(len(partidos), 3)
        conv_party_names = [p.nome for p in partidos]
        self.assertTrue(conv.JACOBINOS in conv_party_names)
        self.assertTrue(conv.GIRONDINOS in conv_party_names)
        self.assertTrue(conv.MONARQUISTAS in conv_party_names)

    def test_should_find_legislatura(self):
        search_legislature_by_date = datetime.date(1989, 07, 14)
        try:
            leg = models.Legislatura.find(search_legislature_by_date, 'Pierre')
            self.assertTrue(leg is not None)
        except ValueError:
            self.fail('Legislatura não encontrada')

    def test_should_not_find_legislatura(self):
        search_legislature_by_date = datetime.date(1900, 07, 14)
        try:
            models.Legislatura.find(search_legislature_by_date, 'Pierre')
            self.fail('Legislatura não deveria ter sido encontrada')
        except:
            self.assertTrue(True)

    def test_deleta_casa(self):

        partyTest1 = models.Partido()
        partyTest1.nome = 'PA'
        partyTest1.numero = '01'
        partyTest1.cor = '#FFFAAA'
        partyTest1.save()

        partyTest2 = models.Partido()
        partyTest2.nome = 'PB'
        partyTest2.numero = '02'
        partyTest1.cor = '#FFFFFF'
        partyTest2.save()

        parliamentaryTest1 = models.Parlamentar()
        parliamentaryTest1.id_parlamentar = ''
        parliamentaryTest1.nome = 'Pierre'
        parliamentaryTest1.genero = ''
        parliamentaryTest1.save()

        parliamentaryTest2 = models.Parlamentar()
        parliamentaryTest2.id_parlamentar = ''
        parliamentaryTest2.nome = 'Napoleao'
        parliamentaryTest2.genero = ''
        parliamentaryTest2.save()

        lesgilativeHouseTest1 = models.CasaLegislativa()
        lesgilativeHouseTest1.nome = 'Casa1'
        lesgilativeHouseTest1.nome_curto = 'cs1'
        lesgilativeHouseTest1.esfera = 'FEDERAL'
        lesgilativeHouseTest1.local = ''
        lesgilativeHouseTest1.atualizacao = '2012-06-01'
        lesgilativeHouseTest1.save()

        lesgilativeHouseTest2 = models.CasaLegislativa()
        lesgilativeHouseTest2.nome = 'Casa2'
        lesgilativeHouseTest2.nome_curto = 'cs2'
        lesgilativeHouseTest2.esfera = 'MUNICIPAL'
        lesgilativeHouseTest2.local = 'local2'
        lesgilativeHouseTest2.atualizacao = '2012-12-31'
        lesgilativeHouseTest2.save()

        legislatureTest1 = models.Legislatura()
        legislatureTest1.parlamentar = parliamentaryTest1
        legislatureTest1.casa_legislativa = lesgilativeHouseTest1
        legislatureTest1.inicio = '2013-01-01'
        legislatureTest1.fim = '2013-02-01'
        legislatureTest1.partido = partyTest1
        legislatureTest1.localidade = 'PB'
        legislatureTest1.save()

        legislatureTest2 = models.Legislatura()
        legislatureTest2.parlamentar = parliamentaryTest2
        legislatureTest2.casa_legislativa = lesgilativeHouseTest2
        legislatureTest2.inicio = '2013-01-02'
        legislatureTest2.fim = '2013-02-02'
        legislatureTest2.partido = partyTest2
        legislatureTest2.localidade = 'PR'
        legislatureTest2.save()

        propositionTest1 = models.Proposicao()
        propositionTest1.id_prop = '0001'
        propositionTest1.sigla = 'PR1'
        propositionTest1.numero = '0001'
        propositionTest1.ano = '2013'
        propositionTest1.data_apresentacao = '2013-01-02'
        propositionTest1.casa_legislativa = lesgilativeHouseTest1
        propositionTest1.save()

        propositionTest2 = models.Proposicao()
        propositionTest2.id_prop = '0002'
        propositionTest2.sigla = 'PR2'
        propositionTest2.numero = '0002'
        propositionTest2.ano = '2013'
        propositionTest2.data_apresentacao = '2013-02-02'
        propositionTest2.casa_legislativa = lesgilativeHouseTest2
        propositionTest2.save()

        votingTest1 = models.Votacao(
            id_vot=' 12345', descricao='Teste da votacao',
            data='1900-12-05', resultado='Teste', proposicao=propositionTest1)
        votingTest1.save()

        voteTest1 = models.Voto(
            votacao=votingTest1, legislatura=legislatureTest1, opcao='TESTE')
        voteTest1.save()

        before_party_objects = models.Partido.objects.all()
        before_parliamentary_objects = models.Parlamentar.objects.all()
        before_house_objects = models.CasaLegislativa.objects.all()
        before_legislature_objects = models.Legislatura.objects.all()
        before_proposition_objects = models.Proposicao.objects.all()
        before_vote_objects = models.Voto.objects.all()
        before_voting_objects = models.Votacao.objects.all()

        party_names = [p.nome for p in before_party_objects]
        self.assertTrue('PA' in party_names)
        self.assertTrue('PB' in party_names)

        parliamentary_names = [pl.nome for pl in before_parliamentary_objects]
        self.assertTrue('Pierre' in parliamentary_names)
        self.assertTrue('Napoleao' in parliamentary_names)

        house_names = [c.nome for c in before_house_objects]
        self.assertTrue('Casa1' in house_names)
        self.assertTrue('Casa2' in house_names)

        legislature_names = [l.localidade for l in before_legislature_objects]
        self.assertTrue('PB' in legislature_names)
        self.assertTrue('PR' in legislature_names)

        proposition_names = [lg.sigla for lg in before_proposition_objects]
        self.assertTrue('PR1' in proposition_names)
        self.assertTrue('PR2' in proposition_names)

        vote_names = [v.votacao for v in before_vote_objects]
        self.assertTrue(votingTest1 in vote_names)

        voting_names = [vt.id_vot for vt in before_voting_objects]
        self.assertTrue(' 12345' in voting_names)

        # Trying to delete a house that does not exist
        models.CasaLegislativa.deleta_casa('casa_qualquer')
        models.CasaLegislativa.deleta_casa('cs1')

        after_party_objects = models.Partido.objects.all()
        after_parliamentary_objects = models.Parlamentar.objects.all()
        after_house_objects = models.CasaLegislativa.objects.all()
        after_legislature_objects = models.Legislatura.objects.all()
        after_proposition_objects = models.Proposicao.objects.all()
        after_vote_objects = models.Voto.objects.all()
        after_voting_objects = models.Votacao.objects.all()

        party_names = [p.nome for p in after_party_objects]
        self.assertTrue('PA' in party_names)
        self.assertTrue('PB' in party_names)

        parliamentary_names = [pl.nome for pl in after_parliamentary_objects]
        self.assertTrue('Pierre' in parliamentary_names)
        self.assertTrue('Napoleao' in parliamentary_names)

        house_names = [c.nome for c in after_house_objects]
        self.assertFalse('Casa1' in house_names)
        self.assertTrue('Casa2' in house_names)

        legislature_names = [l.localidade for l in after_legislature_objects]
        self.assertFalse('PB' in legislature_names)
        self.assertTrue('PR' in legislature_names)

        proposition_names = [lg.sigla for lg in after_proposition_objects]
        self.assertFalse('PR1' in proposition_names)
        self.assertTrue('PR2' in proposition_names)

        vote_names = [v.votacao for v in after_vote_objects]
        self.assertFalse(votingTest1 in vote_names)

        voting_names = [vt.id_vot for vt in after_voting_objects]
        self.assertFalse(' 12345' in voting_names)


class StringUtilsTest(TestCase):

    def test_transforma_texto_em_lista_de_string_texto_vazio(self):
        string_list = utils.StringUtils.transforma_texto_em_lista_de_string(
            "")
        self.assertEquals(0, len(string_list))

    def test_transforma_texto_em_lista_de_string_texto_nulo(self):
        string_list = utils.StringUtils.transforma_texto_em_lista_de_string(
            None)
        self.assertEquals(0, len(string_list))

    def test_transforma_texto_em_lista_de_string(self):
        string_list = utils.StringUtils.transforma_texto_em_lista_de_string(
            "educação, saúde, desmatamento")
        self.assertEquals(3, len(string_list))
        self.assertEquals("educação", string_list[0])
        self.assertEquals("saúde", string_list[1])
        self.assertEquals("desmatamento", string_list[2])
