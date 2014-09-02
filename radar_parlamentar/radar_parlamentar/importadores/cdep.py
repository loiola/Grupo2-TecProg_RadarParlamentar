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

        parametros_de_consulta = ["idprop"]
        args = {'idprop': id_prop}
        url = self._montar_url_consulta_camara(
            Camaraws.URL_PROPOSICAO, parametros_de_consulta, **args)
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

        parametros_de_consulta = ["tipo", "numero", "ano"]
        args = {'tipo': sigla, 'numero': num, 'ano': ano}
        if kwargs:
            args.update(kwargs)
        url = self._montar_url_consulta_camara(
            Camaraws.URL_VOTACOES, parametros_de_consulta, **args)
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

        parametros_de_consulta = ["ano", "tipo"]
        args = {'ano': ano, 'tipo': ' '}
        url = self._montar_url_consulta_camara(
            Camaraws.URL_PLENARIO, parametros_de_consulta, **args)
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

        parametros_de_consulta = [
            "sigla", "numero", "ano", "datapresentacaoini",
            "datapresentacaofim", "idtipoautor", "partenomeautor",
            "siglapartidoautor", "siglaufautor", "generoautor", "codestado",
            "codorgaoestado", "emtramitacao"]
        args = {'sigla': sigla, 'ano': ano}
        if kwargs:
            args.update(kwargs)
        print(args)
        url = self._montar_url_consulta_camara(
            Camaraws.URL_LISTAR_PROPOSICOES, parametros_de_consulta, **args)
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

        list_id_prop = []
        list_nome = []
        for child in xml:
            id_prop = child.find('codProposicao').text.strip()
            nome_prop = child.find('nomeProposicao').text.strip()
            list_id_prop.append(id_prop)
            list_nome.append(nome_prop)
        return zip(list_id_prop, list_nome)

    def find_props_disponiveis(self, ano_min=1991, ano_max=2013,
                               camaraws=Camaraws()):
        """Returna a list with two ids and names of propositions available
        by feature ListarProposicoesVotadasPlenario.

        Searches are made by propositions from ano_min, which by default is 1991 to the present."""

        today = datetime.today()
        if (ano_max is None):
            ano_max = today.year
        siglas = camaraws.listar_siglas()
        votadas = []
        for ano in range(ano_min, ano_max + 1):
            logger.info('Procurando em %s' % ano)
            for sigla in siglas:
                try:
                    xml = camaraws.obter_proposicoes_votadas_plenario(ano)
                    zip_list_prop = self._parse_nomes_lista_proposicoes(xml)
                    votadas.append(zip_list_prop)
                    logger.info('%d %ss encontrados' %
                                (len(zip_list_prop), sigla))
                except urllib2.URLError, etree.ParseError:
                    logger.error('access error in %s' % sigla)
                except ValueError, error:
                    logger.error("ValueError: %s" % error)
        return votadas


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

        proposicoes = []
        for position in self.votadas:
            for prop in position:
                id_prop = prop[0]
                sigla = prop[1][0:prop[1].index(" ")]
                num = prop[1][prop[1].index(" ") + 1: prop[1].index("/")]
                ano = prop[1][prop[1].index("/") + 1: len(prop[1])]
                proposicoes.append(
                    {'id': id_prop, 'sigla': sigla, 'num': num, 'ano': ano})
        return proposicoes

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
            prop = query[0]
        else:
            prop = models.Proposicao()
            prop.id_prop = id_prop
            prop.sigla = prop_xml.get('tipo').strip()
            prop.numero = prop_xml.get('numero').strip()
            prop.ano = prop_xml.get('ano').strip()
            prop.ementa = prop_xml.find('Ementa').text.strip()
            prop.descricao = prop_xml.find('ExplicacaoEmenta').text.strip()
            prop.indexacao = prop_xml.find('Indexacao').text.strip()
            prop.autor_principal = prop_xml.find('Autor').text.strip()
            date_str = prop_xml.find('DataApresentacao').text.strip()
            prop.data_apresentacao = self._converte_data(date_str)
            prop.situacao = prop_xml.find('Situacao').text.strip()
            prop.casa_legislativa = self.camara_dos_deputados
            prop.save()
        return prop

    def _votacao_from_xml(self, votacao_xml, prop):
        
        descricao = 'Resumo: [%s]. ObjVotacao: [%s]' % (
            votacao_xml.get('Resumo'), votacao_xml.get('ObjVotacao'))
        data_str = votacao_xml.get('Data').strip()
        hora_str = votacao_xml.get('Hora').strip()
        date_time = self._converte_data(data_str, hora_str)

        query = models.Votacao.objects.filter(
            descricao=descricao, data=date_time,
            proposicao__casa_legislativa=self.camara_dos_deputados)
        if query:
            votacao = query[0]
        else:
            logger.info('Importando votação ocorrida em %s' % data_str)
            votacao = models.Votacao()
            votacao.descricao = descricao
            votacao.data = date_time
            votacao.proposicao = prop
            votacao.save()
            if votacao_xml.find('votos'):
                for voto_xml in votacao_xml.find('votos'):
                    self._voto_from_xml(voto_xml, votacao)
            votacao.save()

        return votacao

    def _voto_from_xml(self, voto_xml, votacao):
        """Save voting in the database.

        Attributes:
            voto_xml -- XML representing voting (object etree)
            votacao -- object of type Votacao

        Returns:
            object of type Voting."""
            
        voto = models.Voto()

        opcao_str = voto_xml.get('Voto')
    
        if (opcao_str.find(" ") > -1):
            voto.opcao = self._opcao_xml_to_model(
                opcao_str[0:opcao_str.index(" ")])
        else:
            voto.opcao = self._opcao_xml_to_model(opcao_str)
        leg = self._legislatura(voto_xml)

        voto.legislatura = leg
        voto.votacao = votacao
        voto.save()

        return voto

    def _opcao_xml_to_model(self, voto):
        """Interprets vote as it is in XML and responds suitability modeling in models.py."""

        if voto == 'Não':
            return models.NAO
        elif voto == 'Sim':
            return models.SIM
        elif voto == 'Obstrução':
            return models.OBSTRUCAO
        elif voto == 'Abstenção':
            return models.ABSTENCAO
        else:
            logger.warning(
                'tipo de voto (%s) desconhecido! Mapeado como ABSTENCAO'
                % voto)
            return models.ABSTENCAO

    def _legislatura(self, voto_xml):
    
        partido = self._partido(voto_xml.get('Partido'))
        votante = self._votante(voto_xml.get('Nome'), partido.nome)

        
        legs = models.Legislatura.objects.filter(
            parlamentar=votante, partido=partido,
            casa_legislativa=self.camara_dos_deputados)

        if legs:
            leg = legs[0]
        else:
            leg = models.Legislatura()
            leg.parlamentar = votante
            leg.partido = partido
            leg.localidade = voto_xml.get('UF')
            leg.casa_legislativa = self.camara_dos_deputados
            leg.inicio = INICIO_PERIODO  
            leg.fim = FIM_PERIODO  
            leg.save()

        return leg

    def _partido(self, nome_partido):
        """Search the cache first and then in the database; if not, creates new political party."""

        nome_partido = nome_partido.strip()
        partido = self.partidos.get(nome_partido)
        if not partido:
            partido = models.Partido.from_nome(nome_partido)
            if partido is None:
                logger.warning(
                    'Não achou o partido %s; Usando "sem partido"'
                    % nome_partido)
                partido = models.Partido.get_sem_partido()
            else:
                partido.save()
                self.partidos[nome_partido] = partido

        return partido

    def _votante(self, nome_dep, nome_partido):
        """Search the cache first and then in the database; if not, creates new parliamentary."""

        key = '%s-%s' % (nome_dep, nome_partido)
        parlamentar = self.parlamentares.get(key)
        if not parlamentar:
            parlamentares = models.Parlamentar.objects.filter(nome=nome_dep)
            if parlamentares:
                parlamentar = parlamentares[0]
                self.parlamentares[key] = parlamentar

        if not parlamentar:
            parlamentar = models.Parlamentar()
            parlamentar.nome = nome_dep
            parlamentar.save()
            self.parlamentares[key] = parlamentar
        return parlamentar

    def _progresso(self):
        """Indicate progress on screen."""

        porctg = (int)(1.0 * self.importadas / self.total * 100)
        logger.info('Progresso: %d / %d proposições (%d%%)' %
                    (self.importadas, self.total, porctg))

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
        lista_de_listas = []
        start = 0
        chunk_size = (int)(
            math.ceil(1.0 * len(lista) / self.numero_de_listas))
        while start < len(lista):
            end = start + chunk_size
            if (end > len(lista)):
                end = len(lista)
            lista_de_listas.append(lista[start:end])
            start += chunk_size
        return lista_de_listas


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
    ano_min = 2012
    ano_max = 2013
    proposicoes = {}
    percentuais_fem = {}
    contagem_proposicoes = {}

    for ano in range(ano_min, ano_max + 1):
        proposicoes[ano] = {}
        contagem_proposicoes[ano] = {}
        proposicoes[ano]['F'] = []
        proposicoes[ano]['M'] = []
        contagem_proposicoes[ano]['F'] = []
        contagem_proposicoes[ano]['M'] = []
        contagem_proposicoes[ano]['somatotal'] = []

        for gen in ['F', 'M']:
            prop_ano_gen = propFinder._parse_nomes_lista_proposicoes(
                camaraws.listar_proposicoes('PL', str(ano), **{
                    'generoautor': gen}))
            for prop in prop_ano_gen:
                prop_xml = camaraws.obter_proposicao_por_id(prop[0])
                proposicoes[ano][gen].append(
                    importador._prop_from_xml(prop_xml, prop[0]))

        contagem_proposicoes[ano]['mulheres'] = len(proposicoes[ano]['F'])
        contagem_proposicoes[ano]['homens'] = len(proposicoes[ano]['M'])
        contagem_proposicoes[ano]['somatotal'] = len(
            proposicoes[ano]['F']) + len(proposicoes[ano]['M'])

        percentuais_fem[ano] = 100 * float(
            contagem_proposicoes[ano]['F']) / float(contagem_proposicoes[
                                                    ano]['somatotal'])

    return {'proposicoes': proposicoes, 'contagem': contagem_proposicoes,
            'percentuais_fem': percentuais_fem}


def main():

    logger.info('IMPORTANDO DADOS DA CAMARA DOS DEPUTADOS')
    propFinder = ProposicoesFinder()
    zip_votadas = propFinder.find_props_disponiveis()
    propParser = ProposicoesParser(zip_votadas)
    dic_votadas = propParser.parse()
    separador = SeparadorDeLista(NUM_THREADS)
    listas_votadas = separador.separa_lista_em_varias_listas(dic_votadas)
    threads = []
    for lista_votadas in listas_votadas:
        importer = ImportadorCamara(lista_votadas)
        thread = ImportadorCamaraThread(importer)
        threads.append(thread)
        thread.start()
    wait_threads(threads)
    logger.info('IMPORTACAO DE DADOS DA CAMARA DOS DEPUTADOS FINALIZADA')
