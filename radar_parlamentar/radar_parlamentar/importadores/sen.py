# !/usr/bin/python
# coding=utf8

# Copyright (C) 2012, Leonardo Leite
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

"""Senate Module

Classes:
    CasaLegislativaGerador
    ImportadorVotacoesSenado
    ImportadorSenadores"""

from __future__ import unicode_literals
from django.utils.dateparse import parse_datetime
from datetime import date
from modelagem import models
import urllib2
import re
import os
import xml.etree.ElementTree as etree
import logging

# Date the XML files were updated
ULTIMA_ATUALIZACAO = parse_datetime('2013-02-14 0:0:0')

MODULE_DIR = os.path.abspath(os.path.dirname(__file__))

# Folder with the files with data provided by senate
DATA_FOLDER = os.path.join(MODULE_DIR, 'dados/senado')
VOTACOES_FOLDER = os.path.join(DATA_FOLDER, 'votacoes')

NOME_CURTO = 'sen'

logger = logging.getLogger("radar")


class SenadoWS:
    """Access to senate web services"""

    URL_LEGISLATURA = 'http://legis.senado.gov.br/dadosabertos/senador/lista/legislatura/%s'

    def obter_senadores_from_legislatura(self, id_leg):
        """Get senator from a legislature

        Arguments:
        id_leg

        Returns:
        An object ElementTree corresponding to XML returned by web service
        Exemple:
        http://legis.senado.gov.br/dadosabertos/senador/lista/legislatura/52

        Exceptions:
            ValueError -- when legislature does not exist"""

        url = SenadoWS.URL_LEGISLATURA % id_leg
        try:
            request = urllib2.Request(url)
            xml = urllib2.urlopen(request).read()
        except urllib2.URLError, error:
            logger.error("urllib2.URLError: %s" % error)
            raise ValueError('Legislatura %s não encontrada' % id_leg)

        try:
            tree = etree.fromstring(xml)
        except etree.ParseError, error:
            logger.error("etree.ParseError: %s" % error)
            raise ValueError('Legislatura %s não encontrada' % id_leg)

        return tree


class CasaLegislativaGerador:

    def gera_senado(self):
        """Generate object by CasaLegislativa type representing the Senate"""

        if not models.CasaLegislativa.objects.filter(nome_curto=NOME_CURTO):
            sen = models.CasaLegislativa()
            sen.nome = 'Senado'
            sen.nome_curto = NOME_CURTO
            sen.esfera = models.FEDERAL
            sen.atualizacao = ULTIMA_ATUALIZACAO
            sen.save()
        else:
            sen = models.CasaLegislativa.objects.get(nome_curto=NOME_CURTO)
        return sen


class ImportadorVotacoesSenado:
    """Save the XML Snetae datas in the database"""

    def __init__(self):
        self.senado = models.CasaLegislativa.objects.get(nome_curto=NOME_CURTO)
        self.proposicoes = {}
            # chave é o nome da proposição (sigla num/ano), valor é objeto
            # Proposicao

    def _converte_data(self, data_str):
        """Converts string "aaaa-mm-dd to datetime object;
        returns None if data_str is invalid"""

        DATA_REGEX = '(\d{4})-(\d{2})-(\d{2})'
        res = re.match(DATA_REGEX, data_str)
        if res:
            return date(int(res.group(1)), int(res.group(2)),
                        int(res.group(3)))
        else:
            raise ValueError

    def _voto_senado_to_model(self, voto):
        """Interprets vote as in XML and answer according to the modeling in 
        models.py"""

        DESCULPAS = ['MIS', 'MERC', 'P-NRV', 'REP',
                     'AP', 'LA', 'LAP', 'LC', 'LG', 'LS', 'NA']

        # XML is not in UTF-8, it can issue the operations
        if voto == 'Não':
            return models.NAO
        elif voto == 'Sim':
            return models.SIM
        elif voto == 'NCom':
            return models.AUSENTE
        elif voto in DESCULPAS:
            return models.AUSENTE
        elif voto == 'Abstenção':
            return models.ABSTENCAO

        # Obstruction
        elif voto == 'P-OD':  
            return models.ABSTENCAO
        else:
            return models.ABSTENCAO

    def _find_partido(self, nome_partido):

        nome_partido = nome_partido.strip()
        partido = models.Partido.from_nome(nome_partido)
        if partido is None:
            logger.warn('Não achou o partido %s' % nome_partido)
            partido = models.Partido.get_sem_partido()
        return partido

    def _cria_legislatura(self, voto_parlamentar_tree, votacao):

        nome = voto_parlamentar_tree.find('NomeParlamentar').text
        codigo = voto_parlamentar_tree.find('CodigoParlamentar').text
        sexo = voto_parlamentar_tree.find('SexoParlamentar').text

        if models.Parlamentar.objects.filter(nome=nome,
                                             id_parlamentar=codigo).exists():
            senador = models.Parlamentar.objects.get(
                nome=nome, id_parlamentar=codigo)
        else:
            senador = models.Parlamentar()
            senador.id_parlamentar = codigo
            senador.nome = nome
            senador.genero = sexo
            senador.save()

        leg = models.Legislatura()
        leg.parlamentar = senador
        leg.casa_legislativa = self.senado
        ini, fim = self._periodo_arbitrario(votacao.data)
        leg.inicio = ini
        leg.fim = fim
        sigla_partido = voto_parlamentar_tree.find('SiglaPartido').text
        leg.partido = self._find_partido(sigla_partido)
        leg.localidade = voto_parlamentar_tree.find('SiglaUF').text
        leg.save()
        return leg

    def _votos_from_tree(self, votos_tree, votacao):
        """Makes parsing of the votes, save in the database and returns the list 
        of votes"""

        votos = []
        for voto_parlamentar_tree in votos_tree:
            nome_senador = voto_parlamentar_tree.find('NomeParlamentar').text
            try:
                legislatura = models.Legislatura.find(
                    votacao.data, nome_senador)
            except ValueError, error:
                logger.error("ValueError: %s" % error)
                logger.warn(
                    'Não encontramos legislatura do senador %s' % nome_senador)
                logger.info(
                    'Criando legislatura para o senador %s' % nome_senador)
                legislatura = self._cria_legislatura(
                    voto_parlamentar_tree, votacao)
            voto = models.Voto()
            voto.legislatura = legislatura
            voto.votacao = votacao
            voto.opcao = self._voto_senado_to_model(
                voto_parlamentar_tree.find('Voto').text)
            voto.save()
            votos.append(voto)
        return votos

    def _periodo_arbitrario(self, dt):
        """Returns start and end of an arbitrary term that contains the date 
        entered"""

        periodo1 = (date(2011, 02, 01), date(2019, 01, 31))
        periodo2 = (date(2003, 02, 01), date(2011, 01, 31))
        if dt >= periodo1[0] and dt <= periodo1[1]:
            return periodo1[0], periodo1[1]
        elif dt >= periodo2[0] and dt <= periodo2[1]:
            return periodo2[0], periodo2[1]
        else:
            raise ValueError('Data %s inválida' % dt)

    def _nome_prop_from_tree(self, votacao_tree):

        sigla = votacao_tree.find('SiglaMateria').text
        numero = votacao_tree.find('NumeroMateria').text
        ano = votacao_tree.find('AnoMateria').text
        return '%s %s/%s' % (sigla, numero, ano)

    def _proposicao_from_tree(self, votacao_tree):

        prop_nome = self._nome_prop_from_tree(votacao_tree)
        if prop_nome in self.proposicoes:
            prop = self.proposicoes[prop_nome]
        else:
            prop = models.Proposicao()
            prop.sigla = votacao_tree.find('SiglaMateria').text
            prop.numero = votacao_tree.find('NumeroMateria').text
            prop.ano = votacao_tree.find('AnoMateria').text
            prop.casa_legislativa = self.senado
            prop.save()
            self.proposicoes[prop_nome] = prop
        return prop

    def _from_xml_to_bd(self, xml_file):
        """Save in the database and returns the Django voting list"""

        f = open(xml_file, 'r')
        xml = f.read()
        f.close()
        tree = etree.fromstring(xml)

        votacoes = []

        votacoes_tree = tree.find('Votacoes')
        if votacoes_tree is not None:
            for votacao_tree in votacoes_tree:

                votacao_secreta = votacao_tree.find('Secreta').text

                # If voting is not secret:
                if votacao_tree.tag == 'Votacao' and votacao_secreta == 'N':

                    codigo = votacao_tree.find('CodigoSessaoVotacao').text
                    votacoes_query = models.Votacao.objects.filter(
                        id_vot=codigo)

                    if votacoes_query:
                        votacao = votacoes_query[0]
                        votacoes.append(votacao)
                    else:
                        proposicao = self._proposicao_from_tree(votacao_tree)
                        nome = '%s %s/%s' % (
                            proposicao.sigla, proposicao.numero,
                            proposicao.ano)
                        logger.debug('Importando %s' % nome)
                        votacao = models.Votacao()
                        votacao.id_vot = codigo

                        # To create the primary key and assign the votes
                        votacao.save()
                        votacao.descricao = votacao_tree.find(
                            'DescricaoVotacao').text
                        votacao.data = self._converte_data(
                            votacao_tree.find('DataSessao').text)
                        if votacao_tree.find('Resultado') is not None:
                            votacao.resultado = votacao_tree.find(
                                'Resultado').text
                        votacao.proposicao = proposicao
                        votos_tree = votacao_tree.find('Votos')
                        if votos_tree is not None:
                            votos = self._votos_from_tree(votos_tree, votacao)
                            if not votos:
                                logger.warn(
                                    'Votação desconsiderada (sem votos)')
                                votacao.delete()
                            else:
                                votacao.save()
                                votacoes.append(votacao)
                        else:
                            logger.warn(
                                'Votação desconsiderada (votos_tree nulo)')
                            votacao.delete()
        return votacoes

    def progresso(self):
        """Indicates progress on screen"""

        print('.'),

    def _xml_file_names(self):
        """Returns a list of paths of XMLs files contained in the folder 
        VOTACOES_FOLDER"""

        files = os.listdir(VOTACOES_FOLDER)
        xmls = filter(lambda name: name.endswith('.xml'), files)
        xmls = map(lambda name: os.path.join(VOTACOES_FOLDER, name), xmls)
        return xmls

    def importar_votacoes(self):

        # for xml_file in ['importadores/dados/senado/ListaVotacoes2011.xml']:
        # Facilitates debuging
        for xml_file in self._xml_file_names():
            logger.info('Importando %s' % xml_file)
            self._from_xml_to_bd(xml_file)


class ImportadorSenadores:

    # This list needs to be updated year by year
    # 52 is the minimum legislature because we just have voting from 2005 to now
    LEGISLATURAS = [52, 53, 54, 55]
                                
    def __init__(self):
        self.senado = models.CasaLegislativa.objects.get(nome_curto=NOME_CURTO)

    def _converte_data2(self, data_str):
        """Converte string "dd/mm/aaaa para objeto datetime; retona None
        se data_str é inválido"""
        DATA_REGEX = '(\d\d?)/(\d\d?)/(\d{4})'
        res = re.match(DATA_REGEX, data_str)
        if res:
            new_str = '%s-%s-%s 0:0:0' % (
                res.group(3), res.group(2), res.group(1))
            return parse_datetime(new_str)
        else:
            raise ValueError

    def _find_partido(self, nome_partido):
        if nome_partido is not None:
            nome_partido = nome_partido.strip()
        partido = models.Partido.from_nome(nome_partido)
        if partido is None:
            logger.warn('Não achou o partido %s' % nome_partido)
            partido = models.Partido.get_sem_partido()
        return partido

    def _find_nome_partido(self, partidos_tree):
        """By hour, returns the last party in the list"""

        # TODO in some cases a senator shows with several parties during the
        # legislature. What do we have to do?
        for partido_tree in partidos_tree:
            last_partido_tree = partido_tree
        return last_partido_tree.find('SiglaPartido').text

    def processa_legislatura(self, leg_tree):

        parlamentares_tree = leg_tree.find('Parlamentar').find('Parlamentares')
        for parlamentar_tree in parlamentares_tree:
            codigo = parlamentar_tree.find('CodigoParlamentar').text
            nome = parlamentar_tree.find('NomeParlamentar').text
            uf = parlamentar_tree.find('SiglaUF').text
            partidos_tree = parlamentar_tree.find('Partidos')
            if partidos_tree is not None:
                nome_partido = self._find_nome_partido(partidos_tree)
            else:
                logger.warn('Senador %s não possui lista de partidos!' % nome)
                nome_partido = None
            ano_inicio = parlamentar_tree.find('AnoInicio').text
            ano_fim = parlamentar_tree.find('AnoFim').text

            if nome_partido == 'PC DO B':
                nome_partido = 'PCdoB'
            inicio_legislatura = self._converte_data2('01/01/%s' % ano_inicio)
            fim_legislatura = self._converte_data2('31/12/%s' % ano_fim)
            partido = self._find_partido(nome_partido)

            if not models.Legislatura.objects.filter(inicio=inicio_legislatura,
                                                     fim=fim_legislatura,
                                                     parlamentar__nome=nome,
                                                     partido__nome=nome_partido
                                                     ).exists():
                logger.info('Importando senador %s (%s-%s)' %
                            (nome, nome_partido, uf))

                if models.Parlamentar.objects.filter(nome=nome,
                                                     id_parlamentar=codigo
                                                     ).exists():
                    senador = models.Parlamentar.objects.get(
                        nome=nome, id_parlamentar=codigo)
                else:
                    senador = models.Parlamentar()
                    senador.id_parlamentar = codigo
                    senador.nome = nome
                    senador.save()

                leg = models.Legislatura()
                leg.parlamentar = senador
                leg.casa_legislativa = self.senado
                leg.inicio = inicio_legislatura
                leg.fim = fim_legislatura
                leg.partido = partido
                leg.localidade = uf
                leg.save()

    def importar_senadores(self):
        """Create parliamentaries and legislatures in database"""

        senws = SenadoWS()
        for id_leg in ImportadorSenadores.LEGISLATURAS:
            logger.info("Importando senadores da legislatura %s" % id_leg)
            leg_tree = senws.obter_senadores_from_legislatura(id_leg)
            self.processa_legislatura(leg_tree)


def main():
    """Imports Senate datas"""

    logger.info('IMPORTANDO DADOS DO SENADO')
    geradorCasaLeg = CasaLegislativaGerador()
    geradorCasaLeg.gera_senado()
    logger.info('IMPORTANDO SENADORES')
    importer = ImportadorSenadores()
    importer.importar_senadores()
    logger.info('IMPORTANDO VOTAÇÕES DO SENADO')
    importer = ImportadorVotacoesSenado()
    importer.importar_votacoes()
