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
ULTIMA_ATUALIZACAO = parse_datetime('2013-07-22 0:0:0')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
RESOURCES_FOLDER = os.path.join(MODULE_DIR, 'dados/cdep/')
INICIO_PERIODO = parse_datetime('2004-01-01 0:0:0')
FIM_PERIODO = parse_datetime('2013-08-01 0:0:0')

NUM_THREADS = 16

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
    URL_PROPOSICAO = 'http://www.camara.gov.br/sitcamaraws/Proposicoes.asmx/ObterProposicaoPorID?'
    URL_VOTACOES = 'http://www.camara.gov.br/sitcamaraws/Proposicoes.asmx/ObterVotacaoProposicao?'
    URL_LISTAR_PROPOSICOES = 'http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx/ListarProposicoes?'
    URL_PLENARIO = 'http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx/ListarProposicoesVotadasEmPlenario?'

    def __init__(self, url=Url()):
        self.url = url

    def _montar_url_consulta_camara(self, base_url, url_params, **kwargs):
        built_url = base_url

        for par in kwargs.keys():
            if type(par) == str:
                kwargs[par] = kwargs[par].lower()

        for par in url_params:
            if par in kwargs.keys():
                built_url += str(par) + "=" + str(kwargs[par]) + "&"
            else:
                built_url += str(par) + "=&"

        built_url = built_url.rstrip("&")
        return built_url

    def obter_proposicao_por_id(self, id_prop):

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
        args = {'idprop': id_prop}
        url = self._montar_url_consulta_camara(
            Camaraws.URL_PROPOSICAO, consult_parameters, **args)
        tree = self.url.toXml(url)
        if tree is None:
            raise ValueError('Proposicao %s nao encontrada' % id_prop)
        return tree

    def obter_votacoes(self, sigla, num, ano, **kwargs):
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
        args = {'tipo': sigla, 'numero': num, 'ano': ano}
        if kwargs:
            args.update(kwargs)
        url = self._montar_url_consulta_camara(
            Camaraws.URL_VOTACOES, consult_parameters, **args)
        tree = self.url.toXml(url)
        if tree is None:
            raise ValueError(
                'Votacoes da proposicao %s %s/%s nao encontrada'
                % (sigla, num, ano))
        return tree

    def obter_proposicoes_votadas_plenario(self, ano):
        """Voting gets made ​​in plenary

        Arguments:
        > obrigatory: ano
        > optional: tipo

        Returns:
        An object, corresponding to the ElementTree XML returned by the web service.
        Exemple:
        http://www.camara.gov.br/sitcamaraws/Proposicoes.asmx/ListarProposicoesVotadasEmPlenario."""

        consult_parameters = ["ano", "tipo"]
        args = {'ano': ano, 'tipo': ' '}
        url = self._montar_url_consulta_camara(
            Camaraws.URL_PLENARIO, consult_parameters, **args)
        tree = self.url.toXml(url)
        if tree is None:
            raise ValueError('O ano %s nao possui votacoes ainda' % ano)
        return tree

    def listar_proposicoes(self, sigla, ano, **kwargs):
        """seek propositions according to year and acronym desired.

        Mandatory arguments:
        sigla, ano -- characterizing strings fetched propositions

        Returns:
        Corresponding to the ElementTree XML returned by webservice.
        Exemplo:
        http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx/ListarProposicoes?sigla=PL&numero=&ano=2011&datApresentacaoIni=14/11/2011&datApresentacaoFim=16/11/2011&autor=&parteNomeAutor=&siglaPartidoAutor=&siglaUFAutor=&generoAutor=&codEstado=&codOrgaoEstado=&emTramitacao=
        The return is a list of Element objects with each list item a proposition found.

        Exceptions:
            ValueError -- when the web service does not return a that occurs when there are no results for the search criteria."""

        consult_parameters = [
            "sigla", "numero", "ano", "datapresentacaoini",
            "datapresentacaofim", "idtipoautor", "partenomeautor",
            "siglapartidoautor", "siglaufautor", "generoautor", "codestado",
            "codorgaoestado", "emtramitacao"]
        args = {'sigla': sigla, 'ano': ano}
        if kwargs:
            args.update(kwargs)
        print(args)
        url = self._montar_url_consulta_camara(
            Camaraws.URL_LISTAR_PROPOSICOES, consult_parameters, **args)
        tree = self.url.toXml(url)
        if tree is None:
            raise ValueError(
                'Proposicoes nao encontradas para sigla=%s&ano=%s' % (sigla, ano))
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

    def _parse_nomes_lista_proposicoes(self, xml):
        """Receive XML (etree object) from web service
        ListarProposicoesVotadasPlenario and returns a list of tuples.
        The first tuple's item is the propositions id, and the second item
        is the name of proposition (sigla num/ano)."""

        id_propositions_list = []
        name_list = []
        for child in xml:
            id_propositions = child.find('codProposicao').text.strip()
            name_propositions = child.find('nomeProposicao').text.strip()
            id_propositions_list.append(id_propositions)
            name_list.append(name_propositions)
        return zip(id_propositions_list, name_list)

    def find_props_disponiveis(self, ano_min=1991, ano_max=2013,
                               camaraws=Camaraws()):
        """Return a list with two ids and names of propositions available
        by feature ListarProposicoesVotadasPlenario.

        Searches are made by propositions from ano_min, which by default is 1991 to the present."""

        today = datetime.today()
        if (ano_max is None):
            ano_max = today.year
        acronyms = camaraws.listar_siglas()
        voted = []
        for year in range(ano_min, ano_max + 1):
            logger.info('Procurando em %s' % year)
            for acronym in acronyms:
                try:
                    xml = camaraws.obter_proposicoes_votadas_plenario(year)
                    zip_list_prop = self._parse_nomes_lista_proposicoes(xml)
                    voted.append(zip_list_prop)
                    logger.info('%d %ss encontrados' %
                                (len(zip_list_prop), acronym))
                except urllib2.URLError, etree.ParseError:
                    logger.error('access error in %s' % acronym)
                except ValueError, error:
                    logger.error("ValueError: %s" % error)
        return voted


class ProposicoesParser:

    def __init__(self, zip_votadas):
        self.votadas = zip_votadas

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
            for prop in position:
                id_propositions = prop[0]
                    acronyms = prop[1][0:prop[1].index(" ")]
                num = prop[1][prop[1].index(" ") + 1: prop[1].index("/")]
                year = prop[1][prop[1].index("/") + 1: len(prop[1])]
                propositions.append(
                    {'id': id_propositions, 'sigla': acronyms, 'num': num, 'ano': year})
        return propositions

LOCK_TO_CREATE_CASA = threading.Lock()


class ImportadorCamara:

    """Saves the data of the web services of the Chamber of Deputies in the database."""

    def __init__(self, votadas, verbose=False):
        """verbose (booleano) -- enables / disables the screen prints."""

        self.verbose = verbose
        # id/sigla/num/ano das proposições que tiveram votações
        self.votadas = votadas
        self.total = len(self.votadas)

        # Indicate progress:
        self.importadas = 0  
        self.partidos = {}

            # Political parties cache (key is name, and value is object Partido)
        self.parlamentares = {}

            # Parliamentary cache (key is 'nome-partido', and value é object Parlamentar


    def _converte_data(self, data_str, hora_str='00:00'):
        """Convert string 'd/m/a' to object datetime.
        Returns None if data_str is invalid.
        can also receive time: hora_str likes 'h:m'."""

        DATA_REGEX = '(\d\d?)/(\d\d?)/(\d{4})'
        HORA_REGEX = '(\d\d?):(\d\d?)'
        dt = re.match(DATA_REGEX, data_str)
        hr = re.match(HORA_REGEX, hora_str)
        if dt and hr:
            new_str = '%s-%s-%s %s:%s:0' % (
                dt.group(3), dt.group(2), dt.group(1),
                hr.group(1), hr.group(2))
            return parse_datetime(new_str)
        else:
            return None

    def _gera_casa_legislativa(self):

        """Creates object likes CasaLegislativa,
        Chamber of Deputies and save in database.
        If cdep already exists in the database, returns the existing object."""

        LOCK_TO_CREATE_CASA.acquire()
        count_cdep = models.CasaLegislativa.objects.filter(
            nome_curto='cdep').count()
        if (count_cdep == 0):
            camara_dos_deputados = models.CasaLegislativa()
            camara_dos_deputados.nome = 'Câmara dos Deputados'
            camara_dos_deputados.nome_curto = 'cdep'
            camara_dos_deputados.esfera = models.FEDERAL
            camara_dos_deputados.atualizacao = ULTIMA_ATUALIZACAO
            camara_dos_deputados.save()
            LOCK_TO_CREATE_CASA.release()
            return camara_dos_deputados
        else:
            LOCK_TO_CREATE_CASA.release()
            return models.CasaLegislativa.objects.get(nome_curto='cdep')

    def _prop_from_xml(self, prop_xml, id_prop):
        """Receive XML representing proposition (object etree)
        and returns objects like Proposicao, which is saved in database.
        If proposition already exists in the database, it returned the proposition
        that was already in the bank."""

        try:
            query = models.Proposicao.objects.filter(
                id_prop=id_prop, casa_legislativa=self.camara_dos_deputados)
        except DatabaseError, error:
            logger.error("DatabaseError: %s" % error)
            # try again
            time.sleep(1)
            query = models.Proposicao.objects.filter(
                id_prop=id_prop, casa_legislativa=self.camara_dos_deputados)

        if query:
            proposition = query[0]
        else:
            proposition = models.Proposicao()
            proposition.id_prop = id_prop
            proposition.sigla = prop_xml.get('tipo').strip()
            proposition.numero = prop_xml.get('numero').strip()
            proposition.ano = prop_xml.get('ano').strip()
            proposition.ementa = prop_xml.find('Ementa').text.strip()
            proposition.descricao = prop_xml.find('ExplicacaoEmenta').text.strip()
            proposition.indexacao = prop_xml.find('Indexacao').text.strip()
            proposition.autor_principal = prop_xml.find('Autor').text.strip()
            date_str = prop_xml.find('DataApresentacao').text.strip()
            proposition.data_apresentacao = self._converte_data(date_str)
            proposition.situacao = prop_xml.find('Situacao').text.strip()
            proposition.casa_legislativa = self.camara_dos_deputados
            proposition.save()
        return proposition

    def _votacao_from_xml(self, votacao_xml, prop):
        
        description = 'Resumo: [%s]. ObjVotacao: [%s]' % (
            votacao_xml.get('Resumo'), votacao_xml.get('ObjVotacao'))
        data_str = votacao_xml.get('Data').strip()
        hora_str = votacao_xml.get('Hora').strip()
        date_time = self._converte_data(data_str, hora_str)

        query = models.Votacao.objects.filter(
            descricao=description, data=date_time,
            proposicao__casa_legislativa=self.camara_dos_deputados)
        if query:
            voting = query[0]
        else:
            logger.info('Importando votação ocorrida em %s' % data_str)
            voting = models.Votacao()
            voting.descricao = description
            voting.data = date_time
            voting.proposicao = prop
            voting.save()
            if votacao_xml.find('votos'):
                for voto_xml in votacao_xml.find('votos'):
                    self._voto_from_xml(voto_xml, voting)
            voting.save()

        return voting

    def _voto_from_xml(self, voto_xml, votacao):
        """Save voting in the database.

        Attributes:
            voto_xml -- XML representing voting (object etree)
            votacao -- object of type Votacao

        Returns:
            object of type Voting."""
            
        vote = models.Voto()

        option_str = voto_xml.get('Voto')
    
        if (option_str.find(" ") > -1):
            vote.opcao = self._opcao_xml_to_model(
                option_str[0:option_str.index(" ")])
        else:
            vote.opcao = self._opcao_xml_to_model(option_str)
        leg = self._legislatura(voto_xml)

        vote.legislatura = leg
        vote.votacao = votacao
        vote.save()

        return vote

    def _opcao_xml_to_model(self, vote):
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

    def _legislatura(self, voto_xml):
    
        party = self._partido(voto_xml.get('Partido'))
        voter = self._votante(voto_xml.get('Nome'), party.nome)

        
        legs = models.Legislatura.objects.filter(
            parlamentar=voter, partido=party,
            casa_legislativa=self.camara_dos_deputados)

        if legs:
            leg = legs[0]
        else:
            leg = models.Legislatura()
            leg.parlamentar = voter
            leg.partido = party
            leg.localidade = voto_xml.get('UF')
            leg.casa_legislativa = self.camara_dos_deputados
            leg.inicio = INICIO_PERIODO  
            leg.fim = FIM_PERIODO  
            leg.save()

        return leg

    def _partido(self, party_name):
        """Search the cache first and then in the database; if not, creates new political party."""

        party_name = party_name.strip()
        party = self.partidos.get(party_name)
        if not party:
            party = models.Partido.from_nome(party_name)
            if party is None:
                logger.warning(
                    'Não achou o partido %s; Usando "sem partido"'
                    % party_name)
                party = models.Partido.get_sem_partido()
            else:
                party.save()
                self.partidos[party_name] = party

        return party

    def _votante(self, nome_dep, nome_partido):
        """Search the cache first and then in the database; if not, creates new parliamentary."""

        key = '%s-%s' % (nome_dep, nome_partido)
        parliamentarian = self.parlamentares.get(key)
        if not parliamentarian:
            parliamentarians = models.Parlamentar.objects.filter(nome=nome_dep)
            if parliamentarians:
                parliamentarian = parliamentarians[0]
                self.parlamentares[key] = parliamentarian

        if not parliamentarian:
            parliamentarian = models.Parlamentar()
            parliamentarian.nome = nome_dep
            parliamentarian.save()
            self.parlamentares[key] = parliamentarian
        return parliamentarian

    def _progresso(self):
        """Indicate progress on screen."""

        percentage = (int)(1.0 * self.importadas / self.total * 100)
        logger.info('Progresso: %d / %d proposições (%d%%)' %
                    (self.importadas, self.total, percentage))

    def importar(self, camaraws=Camaraws()):

        self.camara_dos_deputados = self._gera_casa_legislativa()

        f = lambda dic: (dic['id'], dic['sigla'], dic['num'], dic['ano'])
        for id_prop, sigla, num, ano in [f(dic) for dic in self.votadas]:

            logger.info(
                '############################################################')
            logger.info('Importando votações da PROPOSIÇÃO %s: %s %s/%s' %
                        (id_prop, sigla, num, ano))

            try:
                prop_xml = camaraws.obter_proposicao_por_id(id_prop)
                prop = self._prop_from_xml(prop_xml, id_prop)
                vots_xml = camaraws.obter_votacoes(sigla, num, ano)

                for child in vots_xml.find('Votacoes'):
                    self._votacao_from_xml(child, prop)

                self.importadas += 1
                self._progresso()
            except ValueError, error:
                logger.error("ValueError: %s" % error)

        logger.info(
            ' Fim da Importação das Votações das Proposições da Câmara dos Deputados.')


class SeparadorDeLista:

    def __init__(self, numero_de_listas):
        self.numero_de_listas = numero_de_listas

    def separa_lista_em_varias_listas(self, lista):
        list_lists = []
        start = 0
        chunk_size = (int)(
            math.ceil(1.0 * len(lista) / self.numero_de_listas))
        while start < len(lista):
            end = start + chunk_size
            if (end > len(lista)):
                end = len(lista)
            list_lists.append(lista[start:end])
            start += chunk_size
        return list_lists


class ImportadorCamaraThread(threading.Thread):

    def __init__(self, importer):
        threading.Thread.__init__(self)
        self.importer = importer

    def run(self):
        self.importer.importar()


def wait_threads(threads):
    for t in threads:
        t.join()


def lista_proposicoes_de_mulheres():
    camaraws = Camaraws()
    propFinder = ProposicoesFinder()
    importador = ImportadorCamara([''])
    importador.camara_dos_deputados = importador._gera_casa_legislativa()
    minimal_year = 2012
    maximum_year = 2013
    propositions = {}
    female_percentage = {}
    count_propositions = {}

    for year in range(minimal_year, maximum_year + 1):
        propositions[year] = {}
        count_propositions[year] = {}
        propositions[year]['F'] = []
        propositions[year]['M'] = []
        count_propositions[year]['F'] = []
        count_propositions[year]['M'] = []
        count_propositions[year]['somatotal'] = []

        for gen in ['F', 'M']:
            prop_ano_gen = propFinder._parse_nomes_lista_proposicoes(
                camaraws.listar_proposicoes('PL', str(year), **{
                    'generoautor': gen}))
            for prop in prop_ano_gen:
                prop_xml = camaraws.obter_proposicao_por_id(prop[0])
                propositions[year][gen].append(
                    importador._prop_from_xml(prop_xml, prop[0]))

        count_propositions[year]['mulheres'] = len(propositions[year]['F'])
        count_propositions[year]['homens'] = len(propositions[year]['M'])
        count_propositions[year]['somatotal'] = len(
            propositions[year]['F']) + len(propositions[year]['M'])

        female_percentage[year] = 100 * float(
            count_propositions[year]['F']) / float(count_propositions[
                                                    year]['somatotal'])

    return {'proposicoes': propositions, 'contagem': count_propositions,
            'percentuais_fem': female_percentage}


def main():

    logger.info('IMPORTANDO DADOS DA CAMARA DOS DEPUTADOS')
    propFinder = ProposicoesFinder()
    zip_voted = propFinder.find_props_disponiveis()
    propParser = ProposicoesParser(zip_voted)
    dic_voted = propParser.parse()
    separador = SeparadorDeLista(NUM_THREADS)
    listas_votadas = separador.separa_lista_em_varias_listas(dic_voted)
    threads = []
    for voted_list in listas_votadas:
        importer = ImportadorCamara(voted_list)
        thread = ImportadorCamaraThread(importer)
        threads.append(thread)
        thread.start()
    wait_threads(threads)
    logger.info('IMPORTACAO DE DADOS DA CAMARA DOS DEPUTADOS FINALIZADA')
