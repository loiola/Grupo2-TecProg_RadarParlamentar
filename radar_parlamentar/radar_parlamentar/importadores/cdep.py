# !/usr/bin/python
# coding=utf8

# Copyright (C) 2012, Leonardo Leite, Diego Rabatone, Saulo Trento
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

"""Module that processes the data import the Chamber of Deputies."""

from __future__ import unicode_literals
from django.utils.dateparse import parse_datetime
from django.db.utils import DatabaseError
from modelagem import models
from datetime import datetime
import re
import os
import xml.etree.ElementTree as etree
import urllib2
import logging
import threading
import time
import math

# Date the list, votadas.txt was updated:
LAST_UPDATE = parse_datetime('2013-07-22 0:0:0')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
RESOURCES_FOLDER = os.path.join(MODULE_DIR, 'dados/cdep/')
PERIOD_BEGIN = parse_datetime('2004-01-01 0:0:0')
PERIOD_END = parse_datetime('2013-08-01 0:0:0')

NUMBER_THREADS = 16

logger = logging.getLogger("radar")

class Url(object):

    """Class that open urls."""

    def toXml(self, url):
        try:
            xml = self.read(url)
            tree = etree.fromstring(xml)
        except etree.ParseError, error:
            logger.error("etree.ParseError: %s" % error)
            return None
        return tree

    def read(self, url):
        text = ''
        try:
            request = urllib2.Request(url)
            text = urllib2.urlopen(request).read()
        except urllib2.URLError, error:
            logger.error("urllib2.URLError: %s" % error)
        except urllib2.HTTPError:
            logger.error("urllib2.HTTPError: %s" % error)
        return text

class Camaraws:

    """Acess to Chamber of Deputies's Web Services."""
    PROPOSITION_URL = \
        'http://www.camara.gov.br/sitcamaraws/Proposicoes.asmx/ObterProposicaoPorID?'
    VOTINGS_URL = \
        'http://www.camara.gov.br/sitcamaraws/Proposicoes.asmx/ObterVotacaoProposicao?'
    LIST_PROPOSITIONS_URL = \
        'http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx/ListarProposicoes?'
    PLENARY_URL = \
        'http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx/ListarProposicoesVotadasEmPlenario?'

    def __init__(self, url=Url()):
        self.url = url

    def _convert_to_percentage(self, value){
        percentage_conversion_factor = 100
        percentage = percentage_conversion_factor*value
        return percentage
    }

    def _montar_url_consulta_camara(self, url_base, url_parameters, **kwargs):
        built_url = url_base

        for pair in kwargs.keys():
            if type(pair) == str:
                kwargs[pair] = kwargs[pair].lower()

        for pair in url_parameters:
            if pair in kwargs.keys():
                built_url += str(pair) + "=" + str(kwargs[pair]) + "&"
            else:
                built_url += str(pair) + "=&"

        built_url = built_url.rstrip("&")
        return built_url

    def obter_proposicao_por_id(self, id_propositions):

        """Get details of a proposition

        Arguments:
        id_prop

        Returns:
        An object, corresponding to the ElementTree XML returned by the web service.
        Exemple:
        http://www.camara.gov.br/sitcamaraws/Proposicoes.asmx/ObterProposicaoPorID?idProp=17338

        Exceptions:
            ValueError -- when proposition doesn't exist."""

        consult_parameters = ["idprop"]
        args = {'idprop': id_propositions}
        url = self._montar_url_consulta_camara(
            Camaraws.PROPOSITION_URL, consult_parameters, **args)
        tree = self.url.toXml(url)
        if tree is None:
            raise ValueError('Proposicao %s nao encontrada' % id_propositions)
        return tree

    def obter_votacoes(self, acronym, number, year, **kwargs):
        """Get votings of a proposition

        Arguments:
        sigla, num, ano -- strings that caracterize a proposition

        Retorna:
        An object, corresponding to the ElementTree XML returned by the web service.
        Exemple:
        http://www.camara.gov.br/sitcamaraws/Proposicoes.asmx/ObterVotacaoProposicao?tipo=pl&numero=1876&ano=1999

        Exceptions:
            ValueError -- when proposition doesn't existor doesn't has votings."""

        consult_parameters = ["tipo", "numero", "ano"]
        args = {'tipo': acronym, 'numero': number, 'ano': year}
        if kwargs:
            args.update(kwargs)
        url = self._montar_url_consulta_camara(
            Camaraws.VOTINGS_URL, consult_parameters, **args)
        tree = self.url.toXml(url)
        if tree is None:
            raise ValueError(
                'Votacoes da proposicao %s %s/%s nao encontrada'
                % (acronym, number, year))
        return tree

    def obter_proposicoes_votadas_plenario(self, year):
        """Voting gets made ​​in plenary

        Arguments:
        > obrigatory: ano
        > optional: tipo

        Returns:
        An object, corresponding to the ElementTree XML returned by the web service.
        Exemple:
        http://www.camara.gov.br/sitcamaraws/Proposicoes.asmx/ListarProposicoesVotadasEmPlenario."""

        consult_parameters = ["ano", "tipo"]
        args = {'ano': year, 'tipo': ' '}
        url = self._montar_url_consulta_camara(
            Camaraws.PLENARY_URL, consult_parameters, **args)
        tree = self.url.toXml(url)

        if tree is None:
            raise ValueError('O ano %s nao possui votacoes ainda' % year)
        return tree

    def listar_proposicoes(self, acronym, year, **kwargs):
        """seek propositions according to year and acronym desired.

        Mandatory arguments:
        sigla, ano -- characterizing strings fetched propositions

        Returns:
        Corresponding to the ElementTree XML returned by webservice.
        Exemplo:
        http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx/ListarProposicoes?sigla=PL
        &numero=&ano=2011&datApresentacaoIni=14/11/2011&datApresentacaoFim=16/1
        1/2011&autor=&parteNomeAutor=&siglaPartidoAutor=&siglaUFAutor=&generoAutor=&codE
        stado=&codOrgaoEstado=&emTramitacao=

        The return is a list of Element objects with each list item a proposition found.

        Exceptions:
            ValueError -- when the web service does not return a that occurs when there are
            no results for the search criteria."""

        consult_parameters = [
            "sigla", "numero", "ano", "datapresentacaoini",
            "datapresentacaofim", "idtipoautor", "partenomeautor",
            "siglapartidoautor", "siglaufautor", "generoautor", "codestado",
            "codorgaoestado", "emtramitacao"]
        args = {'sigla': acronym, 'ano': year}

        if kwargs:
            args.update(kwargs)
        print(args)
        url_camara_consult = self._montar_url_consulta_camara(
            Camaraws.LIST_PROPOSITIONS_URL, consult_parameters, **args)
        tree = self.url.toXml(url_camara_consult)

        if tree is None:
            raise ValueError(
                'Proposicoes nao encontradas para sigla=%s&ano=%s' % (acronym, year))
        return tree

    def listar_siglas(self):
        """List of acronyms existing propositions; example: "PL", "PEC" etc. 
           The return is a list of strings."""

        # The full list is here:
        # http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx/ListarSiglasTipoProposicao
        # However, many of these acronyms correspond to propositions do not have voting.
        # So here we are returning a narrower result.
        return ['PL', 'MPV', 'PDC', 'PEC', 'PLP',
                'PLC', 'PLN', 'PLOA', 'PLS', 'PLV']


class ProposicoesFinder:

    def __init__(self, verbose=True):
        self.verbose = verbose

    def _parse_nomes_lista_proposicoes(self, xml_propositions):
        """Receive XML (etree object) from web service
        ListarProposicoesVotadasPlenario and returns a list of tuples.
        The first tuple's item is the propositions id, and the second item
        is the name of proposition (sigla num/ano)."""

        id_propositions_list = []
        name_list = []

        for child in xml_propositions:
            id_propositions = child.find_legislature('codProposicao').text.strip()
            name_propositions = child.find_legislature('nomeProposicao').text.strip()
            id_propositions_list.append(id_propositions)
            name_list.append(name_propositions)
        return zip(id_propositions_list, name_list)

    def find_props_disponiveis(self, minimal_year=1991, maximum_year=2013,
                               camaraws=Camaraws()):
        """Return a list with two ids and names of propositions available
        by feature ListarProposicoesVotadasPlenario.

        Searches are made by propositions from ano_min, which by default is 1991 to the
        present."""

        today = datetime.today()

        if (maximum_year is None):
            maximum_year = today.year
        acronyms = camaraws.listar_siglas()
        voted = []

        for year in range(minimal_year, maximum_year + 1):
            logger.info('Procurando em %s' % year)

            for acronym in acronyms:
                try:
                    xml_propositions = camaraws.obter_proposicoes_votadas_plenario(year)
                    zip_list_prop = self._parse_nomes_lista_proposicoes(xml_propositions)
                    voted.append(zip_list_prop)
                    logger.info('%d %ss encontrados' %
                                (len(zip_list_prop), acronym))
                except urllib2.URLError, etree.ParseError:
                    logger.error('access error in %s' % acronym)
                except ValueError, error:
                    logger.error("ValueError: %s" % error)
        return voted


class ProposicoesParser:

    def __init__(self, zip_voted):
        self.votadas = zip_voted

    def parse(self):
        """
        Returns:
        A list identifying the propositions present in zip_votadas.
        Each position on the list is a dictionary with keys \in {id, sigla, num, ano}.
        The keys and values ​​are strings of these dictionaries.

        list format that will be covered:
        Ex:[('604604', 'REQ 9261/2013 => PRC 228/2013'),
        '604123', 'PL 9261/2013 => PRC 228/2013')]."""

        propositions = []

        for position in self.votadas:

            for proposition in position:
                id_propositions = proposition[0]
                    acronyms = proposition[1][0:proposition[1].index(" ")]
                number = proposition[1][proposition[1].index(" ") + 1: proposition[1].index("/")]
                year = proposition[1][proposition[1].index("/") + 1: len(proposition[1])]
                propositions.append(
                    {'id': id_propositions, 'sigla': acronyms, 'num': number, 'ano': year})
        return propositions

LOCK_TO_CREATE_CASA = threading.Lock()

class ImportadorCamara:

    """Saves the data of the web services of the Chamber of Deputies in the database."""

    def __init__(self, voted, verbose=False):
        """verbose (boolean) -- enables / disables the screen prints."""

        self.verbose = verbose
        # id/aconym/number/year das propositions that had votings
        self.votadas = voted
        self.total = len(self.votadas)

        # Indicate progress:
        self.importadas = 0  
        self.partidos = {}

            # Political parties cache (key is name, and value is object Partido)
        self.parlamentares = {}

    # Parliamentary cache (key is 'nome-search_political_party', and value is object Parlamentar
    def _convert_data(self, data_string, hour_string='00:00'):
        """Convert string 'd/m/a' to object datetime.
        Returns None if data_str is invalid.
        can also receive time: hora_str likes 'h:m'."""

        DATA_REGEX = '(\d\d?)/(\d\d?)/(\d{4})'
        HORA_REGEX = '(\d\d?):(\d\d?)'
        date_regex_variable = re.match(DATA_REGEX, data_string)
        hour_regex_variable = re.match(HORA_REGEX, hour_string)

        if date_regex_variable and hour_regex_variable:
            new_str = '%s-%s-%s %s:%s:0' % (
                date_regex_variable.group(3), date_regex_variable.group(2), date_regex_variable.group(1),
                hour_regex_variable.group(1), hour_regex_variable.group(2))
            return parse_datetime(new_str)
        else:
            return None

    def _generate_legislative_house(self):

        """Creates object likes CasaLegislativa,
        Chamber of Deputies and save in database.
        If cdep already exists in the database, returns the existing object."""

        LOCK_TO_CREATE_CASA.acquire()
        count_cdep = models.CasaLegislativa.objects.filter(
            short_name='cdep').count()

        no_records = 0

        if (count_cdep == no_records):
            deputies_chamber = models.CasaLegislativa()
            deputies_chamber.nome = 'Câmara dos Deputados'
            deputies_chamber.nome_curto = 'cdep'
            deputies_chamber.esfera = models.FEDERAL
            deputies_chamber.atualizacao = LAST_UPDATE
            deputies_chamber.save_data_in_file()
            LOCK_TO_CREATE_CASA.release()
            return deputies_chamber
        else:
            LOCK_TO_CREATE_CASA.release()
            return models.CasaLegislativa.objects.get(short_name='cdep')

    def _propostion_from_xml(self, proposition_xml, id_proposition):
        """Receive XML representing proposition (object etree)
        and returns objects like Proposicao, which is saved in database.
        If proposition already exists in the database, it returned the proposition
        that was already in the bank."""

        try:
            query = models.Proposicao.objects.filter(
                id_propositions=id_proposition, legislative_house=self.camara_dos_deputados)
        except DatabaseError, error:
            logger.error("DatabaseError: %s" % error)

            # try again
            time.sleep(1)
            query = models.Proposicao.objects.filter(
                id_propositions=id_proposition, legislative_house=self.camara_dos_deputados)

        if query:
            proposition = query[0]
        else:
            proposition = models.Proposicao()
            proposition.id_prop = id_proposition
            proposition.sigla = proposition_xml.get('tipo').strip()
            proposition.numero = proposition_xml.get('numero').strip()
            proposition.ano = proposition_xml.get('ano').strip()
            proposition.ementa = proposition_xml.find_legislature('Ementa').text.strip()
            proposition.descricao = proposition_xml.find_legislature('ExplicacaoEmenta').text.strip()
            proposition.indexacao = proposition_xml.find_legislature('Indexacao').text.strip()
            proposition.autor_principal = proposition_xml.find_legislature('Autor').text.strip()
            date_str = proposition_xml.find_legislature('DataApresentacao').text.strip()
            proposition.data_apresentacao = self._convert_data(date_str)
            proposition.situacao = proposition_xml.find_legislature('Situacao').text.strip()
            proposition.casa_legislativa = self.camara_dos_deputados
            proposition.save_data_in_file()
        return proposition

    def _voting_from_xml(self, voting_xml, proposition):
        
        description = 'Resumo: [%s]. ObjVotacao: [%s]' % (
            voting_xml.get('Resumo'), voting_xml.get('ObjVotacao'))
        date_str = voting_xml.get('Data').strip()
        hour_str = voting_xml.get('Hora').strip()
        date_time = self._convert_data(date_str, hour_str)

        query = models.Votacao.objects.filter(
            description=description, data=date_time,
            proposition_legislative_house=self.camara_dos_deputados)
        if query:
            voting = query[0]
        else:
            logger.info('Importando votação ocorrida em %s' % date_str)
            voting = models.Votacao()
            voting.descricao = description
            voting.data = date_time
            voting.proposicao = proposition
            voting.save_data_in_file()

            if voting_xml.find_legislature('votos'):
                for vote_xml in voting_xml.find_legislature('votos'):
                    self._vote_from_xml(vote_xml, voting)
            voting.save_data_in_file()

        return voting

    def _vote_from_xml(self, vote_xml, voting):
        """Save voting in the database.

        Attributes:
            voto_xml -- XML representing voting (object etree)
            votacao -- object of type Votacao

        Returns:
            object of type Voting."""
            
        vote = models.Voto()

        option_str = vote_xml.get('Voto')
    
        if (option_str.find_legislature(" ") > -1):
            vote.opcao = self._option_xml_to_model(
                option_str[0:option_str.index(" ")])
        else:
            vote.opcao = self._option_xml_to_model(option_str)
        leg = self._legislature(vote_xml)

        vote.legislatura = leg
        vote.votacao = voting
        vote.save_data_in_file()

        return vote

    def _option_xml_to_model(self, vote):
        """Interprets vote as it is in XML and responds suitability modeling in models.py."""

        if vote == 'Não':
            return models.NAO
        elif vote == 'Sim':
            return models.SIM
        elif vote == 'Obstrução':
            return models.OBSTRUCAO
        elif vote == 'Abstenção':
            return models.ABSTENCAO
        else:
            logger.warning(
                'tipo de voto (%s) desconhecido! Mapeado como ABSTENCAO'
                % vote)
            return models.ABSTENCAO

    def _legislature(self, vote_xml):
    
        party = self._party(vote_xml.get('Partido'))
        voter = self._voter(vote_xml.get('Nome'), party.nome)

        legs = models.Legislatura.objects.filter(
            parlieamentary=voter, party=party,
            legislative_house=self.camara_dos_deputados)

        if legs:
            leg = legs[0]
        else:
            leg = models.Legislatura()
            leg.parlamentar = voter
            leg.partido = party
            leg.localidade = vote_xml.get('UF')
            leg.casa_legislativa = self.camara_dos_deputados
            leg.inicio = PERIOD_BEGIN
            leg.fim = PERIOD_END
            leg.save_data_in_file()

        return leg

    def _party(self, party_name):
        """Search the cache first and then in the database; if not, creates new political party."""

        party_name = party_name.strip()
        party = self.partidos.get(party_name)

        if not party:
            party = models.Partido.from_name(party_name)

            if party is None:
                logger.warning(
                    'Não achou o search_political_party %s; Usando "sem search_political_party"'
                    % party_name)
                party = models.Partido.get_no_party()
            else:
                party.save_data_in_file()
                self.partidos[party_name] = party

        return party

    def _voter(self, deputy_name, party_name):
        """Search the cache first and then in the database; if not, creates new parliamentary."""

        key = '%s-%s' % (deputy_name, party_name)
        parliamentarian = self.parlamentares.get(key)

        if not parliamentarian:
            parliamentarians = models.Parlamentar.objects.filter(name=deputy_name)
            if parliamentarians:
                parliamentarian = parliamentarians[0]
                self.parlamentares[key] = parliamentarian

        if not parliamentarian:
            parliamentarian = models.Parlamentar()
            parliamentarian.nome = deputy_name
            parliamentarian.save_data_in_file()
            self.parlamentares[key] = parliamentarian
        return parliamentarian

    def _progress(self):
        """Indicate progress on screen."""
        percentage = (int)(1.0 * self.importadas / _convert_to_percentage(self.total))
        logger.info('Progresso: %d / %d proposições (%d%%)' %
                    (self.importadas, self.total, percentage))

    def importar(self, camaraws=Camaraws()):

        self.camara_dos_deputados = self._generate_legislative_house()

        f = lambda dic: (dic['id'], dic['sigla'], dic['num'], dic['ano'])
        for id_proposition, acronym, number, year in [f(dic) for dic in self.votadas]:

            logger.info(
                '############################################################')
            logger.info('Importando votações da PROPOSIÇÃO %s: %s %s/%s' %
                        (id_proposition, acronym, number, year))

            try:
                proposition_xml = camaraws.obter_proposicao_por_id(id_proposition)
                proposition = self._propostion_from_xml(proposition_xml, id_proposition)
                votes_xml = camaraws.obter_votacoes(acronym, number, year)

                for child in votes_xml.find('Votacoes'):
                    self._voting_from_xml(child, proposition)

                self.importadas += 1
                self._progress()
            except ValueError, error:
                logger.error("ValueError: %s" % error)

        logger.info(
            ' Fim da Importação das Votações das Proposições da Câmara dos Deputados.')


class SeparadorDeLista:

    def __init__(self, lists_number):
        self.numero_de_listas = lists_number

    def separa_lista_em_varias_listas(self, list):
        list_lists = []
        start = 0
        chunk_size = (int)(
            math.ceil(1.0 * len(list) / self.numero_de_listas))

        while start < len(list):
            end = start + chunk_size

            if (end > len(list)):
                end = len(list)
            list_lists.append(list[start:end])
            start += chunk_size
        return list_lists


class ImportadorCamaraThread(threading.Thread):

    def __init__(self, importer):
        threading.Thread.__init__(self)
        self.importer = importer

    def run(self):
        self.importer.import_data()


def wait_threads(threads):
    for t in threads:
        t.join()


def lista_proposicoes_de_mulheres():
    camaraws = Camaraws()
    propFinder = ProposicoesFinder()
    importer = ImportadorCamara([''])
    importer.camara_dos_deputados = importer._generate_legislative_house()
    minimal_year = 2012
    maximum_year = 2013
    propositions = {}
    female_percentage = {}
    count_propositions = {}

    increment_variable_adjustment = 1

    for year in range(minimal_year, maximum_year + increment_variable_adjustment):
        propositions[year] = {}
        count_propositions[year] = {}
        propositions[year]['F'] = []
        propositions[year]['M'] = []
        count_propositions[year]['F'] = []
        count_propositions[year]['M'] = []
        count_propositions[year]['somatotal'] = []

        for gender in ['F', 'M']:
            proposition_year_gender = propFinder._parse_nomes_lista_proposicoes(
                camaraws.listar_proposicoes('PL', str(year), **{
                    'generoautor': gender}))

            for proposition in proposition_year_gender:
                proposition_xml = camaraws.obter_proposicao_por_id(proposition[0])
                propositions[year][gender].append(
                    importer._propostion_from_xml(proposition_xml, proposition[0]))

        count_propositions[year]['mulheres'] = len(propositions[year]['F'])
        count_propositions[year]['homens'] = len(propositions[year]['M'])
        count_propositions[year]['somatotal'] = len(
            propositions[year]['F']) + len(propositions[year]['M'])

        female_percentage[year] = _convert_to_percentage(float(
            count_propositions[year]['F'])) / float(count_propositions[
                                                    year]['somatotal'])

    return {'proposicoes': propositions, 'contagem': count_propositions,
            'percentuais_fem': female_percentage}


def main():

    logger.info('IMPORTANDO DADOS DA CAMARA DOS DEPUTADOS')
    propFinder = ProposicoesFinder()
    zip_voted = propFinder.find_props_disponiveis()
    propParser = ProposicoesParser(zip_voted)
    dic_voted = propParser.parse()
    tab = SeparadorDeLista(NUMBER_THREADS)
    voted_lists = tab.separa_lista_em_varias_listas(dic_voted)
    threads = []

    for voted_list in voted_lists:
        importer = ImportadorCamara(voted_list)
        thread = ImportadorCamaraThread(importer)
        threads.append(thread)
        thread.start()
    wait_threads(threads)
    logger.info('IMPORTACAO DE DADOS DA CAMARA DOS DEPUTADOS FINALIZADA')
