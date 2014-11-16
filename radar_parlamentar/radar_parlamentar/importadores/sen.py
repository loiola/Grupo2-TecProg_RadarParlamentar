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

# Principal function.
def main():
    """Imports Senate datas"""

    logger.info('IMPORTANDO DADOS DO SENADO')
    geradorCasaLeg = CasaLegislativaGerador()
    geradorCasaLeg.generate_senate()
    logger.info('IMPORTANDO SENADORES')
    importer = ImportadorSenadores()
    importer.import_senators()
    logger.info('IMPORTANDO VOTAÇÕES DO SENADO')
    importer = ImportadorVotacoesSenado()
    importer.import_votings()

# Date the XML files were updated
ULTIMA_ATUALIZACAO = parse_datetime('2013-02-14 0:0:0')

MODULE_DIR = os.path.abspath(os.path.dirname(__file__))

# Folder with the files with data provided by senate
DATA_FOLDER = os.path.join(MODULE_DIR, 'dados/senado')
VOTACOES_FOLDER = os.path.join(DATA_FOLDER, 'votacoes')

# This variable may not have another name because the database has a field called NOME_CURTO.
# Assigns short 'sen' (senate) to NOME_CURTO.
SHORT_NAME = 'sen'

# Initializing log system.
logger = logging.getLogger("radar")


class SenadoWS:
    """Access to senate web services"""

    URL_LEGISLATURE = 'http://legis.senado.gov.br/dadosabertos/senador/lista/legislatura/%s'

    def get_senators_from_legislature(self, id_legislature):
        """Get senator from a legislature

        Arguments:
        id_leg

        Returns:
        An object ElementTree corresponding to XML returned by web service
        Exemple:
        http://legis.senado.gov.br/dadosabertos/senador/lista/legislatura/52

        Exceptions:
            ValueError -- when legislature does not exist"""

        url = SenadoWS.URL_LEGISLATURE % id_legislature
        try:
            request_url = urllib2.Request(url)
            xml_open_and_read = urllib2.urlopen(request_url).read()
        except urllib2.URLError, error:
            logger.error("urllib2.URLError: %s" % error)
            raise ValueError('Legislatura %s não encontrada' % id_legislature)

        try:
            tree = etree.fromstring(xml_open_and_read)
        except etree.ParseError, error:
            logger.error("etree.ParseError: %s" % error)
            raise ValueError('Legislatura %s não encontrada' % id_legislature)

        return tree


class CasaLegislativaGerador:

    def generate_senate(self):
        """Generate object by CasaLegislativa type representing the Senate"""

        if not models.CasaLegislativa.objects.filter(short_name=SHORT_NAME):

            # Receive data of CasaLegislativa's class, from 'models'.
            senator_lesgislative_house = models.CasaLegislativa()

            senator_lesgislative_house.nome = 'Senado'
            senator_lesgislative_house.nome_curto = SHORT_NAME
            senator_lesgislative_house.esfera = models.FEDERAL
            senator_lesgislative_house.atualizacao = ULTIMA_ATUALIZACAO
            senator_lesgislative_house.save_data_in_file()
        else:
            senator_lesgislative_house = models.CasaLegislativa.objects.get(nome_curto=SHORT_NAME)
        return senator_lesgislative_house


class ImportadorVotacoesSenado:
    """Save the XML Senate datas in the database"""

    def __init__(self):
        self.senado = models.CasaLegislativa.objects.get(short_name=SHORT_NAME)
        self.proposicoes = {}
        # Proposition's name (short num/ano) is the key. The value is the object.

    def converte_data(self, data_str):
        """Converts string "aaaa-mm-dd to datetime object;
        returns None if data_str is invalid"""

        DATA_REGEX = '(\d{4})-(\d{2})-(\d{2})'
        res = re.match(DATA_REGEX, data_str)
        if res:
            return date(int(res.group(1)), int(res.group(2)),
                        int(res.group(3)))
        else:
            raise ValueError

    def senate_vote_to_model(self, vote):
        """Interprets vote as in XML and answer according to the modeling in 
        models.py"""

        # Store a list. Unknown variable.
        JUSTIFICATIONS = ['MIS', 'MERC', 'P-NRV', 'REP',
                     'AP', 'LA', 'LAP', 'LC', 'LG', 'LS', 'NA']

        # XML is not in UTF-8, it can issue the operations
        if vote == 'Não':
            return models.NAO
        elif vote == 'Sim':
            return models.SIM
        elif vote == 'NCom':
            return models.AUSENTE
        elif vote in JUSTIFICATIONS:
            return models.AUSENTE
        elif vote == 'Abstenção':
            return models.ABSTENCAO

        # Obstruction
        elif vote == 'P-OD':
            return models.ABSTENCAO
        else:
            return models.ABSTENCAO

    def find_political_party(self, political_party_name):

        #
        political_party_name = political_party_name.strip()

        # Get political party's name from 'models'.
        political_party = models.Partido.from_name(political_party_name)

        if political_party is None:
            logger.warn('Não achou o partido %s' % political_party_name)
            political_party = models.Partido.get_no_party()
        return political_party

    def create_legislature(self, parliamentary_vote_tree, votings):

        # Receive the parliamentary's name from 'voto_parlamentar_tree'.
        name_parliamentary = parliamentary_vote_tree.find_legislature('NomeParlamentar').text

        # Receive parliamentary's code from 'voto_parlamentar_tree'.
        code_parliamentary = parliamentary_vote_tree.find_legislature('CodigoParlamentar').text

        # Receive parliamentary's gender from 'voto_parlamentar_tree'.
        gender_parliamentary = parliamentary_vote_tree.find_legislature('SexoParlamentar').text

        if models.Parlamentar.objects.filter(name=name_parliamentary,
                                             id_parlamentar=code_parliamentary).exists():
            # Receive name and code from 'Parlamentar' from 'models'.
            senator = models.Parlamentar.objects.get(
                name=name_parliamentary, id_parliamentary=code_parliamentary)
        else:

            # Receive 'Parlamentar' from models.
            senator = models.Parlamentar()

            senator.id_parlamentar = code_parliamentary
            senator.nome = name_parliamentary
            senator.genero = gender_parliamentary
            senator.save_data_in_file()

        # Receive 'Legislatura' from models.
        legislature = models.Legislatura()

        legislature.parlamentar = senator
        legislature.casa_legislativa = self.senado
        begin, end = self.assign_random_period(votings.data)
        legislature.inicio = begin
        legislature.fim = end
        sigla_partido = parliamentary_vote_tree.find_legislature('SiglaPartido').text
        legislature.partido = self.find_political_party(sigla_partido)
        legislature.localidade = parliamentary_vote_tree.find_legislature('SiglaUF').text
        legislature.save_data_in_file()
        return legislature

    def parsing_votes_from_tree(self, votes_tree, votings):
        """Makes parsing of the votes, save in the database and returns the list 
        of votes"""

        # Creating empty list to receive 'legislatura', 'votação' and 'opção de voto'.
        votes = []

        for vote_parliamentary_tree in votes_tree:

            # Stores senators searched on 'voto_parlamentar_tree'.
            name_senator = vote_parliamentary_tree.find_legislature('NomeParlamentar').text

            try:

                # Store results founded in 'Legislatura': 'votacao.data' and 'name_senator'.
                legislature = models.Legislatura.find_legislature(
                    votings.data, name_senator)
            except ValueError, error:
                logger.error("ValueError: %s" % error)
                logger.warn(
                    'Não encontramos legislatura do senador %s' % name_senator)
                logger.info(
                    'Criando legislatura para o senador %s' % name_senator)
                legislature = self.create_legislature(
                    vote_parliamentary_tree, votings)

            # Receive 'Voto' from 'models'.
            vote = models.Voto()

            vote.legislatura = legislature
            vote.votacao = votings
            vote.opcao = self.senate_vote_to_model(
                vote_parliamentary_tree.find_legislature('Voto').text)
            vote.save_data_in_file()
            votes.append(vote)
        return votes

    def assign_random_period(self, dt):
        """Returns start and end of an arbitrary term that contains the date 
        entered"""

        period_1 = (date(2011, 02, 01), date(2019, 01, 31))
        period_2 = (date(2003, 02, 01), date(2011, 01, 31))
        if dt >= period_1[0] and dt <= period_1[1]:
            return period_1[0], period_1[1]
        elif dt >= period_2[0] and dt <= period_2[1]:
            return period_2[0], period_2[1]
        else:
            raise ValueError('Data %s inválida' % dt)

    def get_proposition_data(self, voting_tree):

        # Receive 'SiglaMateria' from 'votacao_tree'.
        acronym_from_legislature = voting_tree.find_legislature('SiglaMateria').text

        # Receive 'NumeroMateria' from 'votacao_tree'.
        number_from_legislature = voting_tree.find_legislature('NumeroMateria').text

        # Receive 'AnoMateria' from 'votacao_tree'.
        year_from_legislature = voting_tree.find_legislature('AnoMateria').text

        return '%s %s/%s' % (acronym_from_legislature, number_from_legislature, year_from_legislature)

    def get_proposition_from_tree(self, voting_tree):

        # Receive proposition's name.
        proposition_name = self.get_proposition_data(voting_tree)

        if proposition_name in self.proposicoes:
            proposition = self.proposicoes[proposition_name]
        else:

            # Get 'Proposicao' from 'models'.
            proposition = models.Proposicao()
            proposition.sigla = voting_tree.find_legislature('SiglaMateria').text
            proposition.numero = voting_tree.find_legislature('NumeroMateria').text
            proposition.ano = voting_tree.find_legislature('AnoMateria').text
            proposition.casa_legislativa = self.senado
            proposition.save_data_in_file()
            self.proposicoes[proposition_name] = proposition
        return proposition

    def save_in_database(self, xml_file):
        """Save in the database and returns the Django voting list"""

        f = open(xml_file, 'r')
        xml = f.read()
        f.close_tag()
        tree = etree.fromstring(xml)

        # Empty list to receive data.
        votings = []

        voting_tree = tree.find_legislature('Votacoes')
        if voting_tree is not None:
            for votings_tree in voting_tree:

                # Get secret voting from 'votacao_tree'.
                secret_voting = votings_tree.find_legislature('Secreta').text

                # If voting is not secret:
                if votings_tree.tag == 'Votacao' and secret_voting == 'N':

                    # Receive 'CodigoSessaoVotacao' from 'votacao_tree'.
                    code_section_voting = votings_tree.find_legislature('CodigoSessaoVotacao').text

                    # Receive filtered result.
                    votings_query = models.Votacao.objects.filter(
                        id_vot=code_section_voting)

                    if votings_query:
                        votes = votings_query[0]
                        votings.append(votes)
                    else:
                        proposition_from_tree = self.get_proposition_from_tree(votings_tree)

                        # Store final name composition of proposition.
                        proposition_name = '%s %s/%s' % (
                            proposition_from_tree.sigla, proposition_from_tree.numero,
                            proposition_from_tree.ano)

                        logger.debug('Importando %s' % proposition_name)
                        votes = models.Votacao()
                        votes.id_vot = code_section_voting

                        # To create the primary key and assign the votes.
                        votes.save_data_in_file()

                        # Receive search results of 'DescricaoVotacao'.
                        votes.descricao = votings_tree.find_legislature(
                            'DescricaoVotacao').text

                        votes.data = self.converte_data(
                            votings_tree.find_legislature('DataSessao').text)

                        if votings_tree.find_legislature('Resultado') is not None:
                            votes.resultado = votings_tree.find_legislature(
                                'Resultado').text
                        votes.proposicao = proposition_from_tree

                        # Store search results of 'Votos'.
                        votos_tree = votings_tree.find_legislature('Votos')

                        if votos_tree is not None:
                            votes = self.parsing_votes_from_tree(votos_tree, votes)
                            if not votes:
                                logger.warn(
                                    'Votação desconsiderada (sem votos)')
                                votes.delete()
                            else:
                                votes.save_data_in_file()
                                votings.append(votes)
                        else:
                            logger.warn(
                                'Votação desconsiderada (voto nulo)')
                            votes.delete()
        return votings

    def indicate_progress(self):
        """Indicates progress on screen"""

        print('.'),

    def return_votacoes_folder_content(self):
        """Returns a list of paths of XMLs files contained in the folder 
        VOTACOES_FOLDER"""

        # Get files from 'VOTACOES_FOLDER'.
        files_from_votacoes_folder = os.listdir(VOTACOES_FOLDER)

        # Filtering files with '.xlm' extension.
        filtering_xmls = filter(lambda name: name.endswith('.xml'), files_from_votacoes_folder)

        # Mapping names into '.xml' files.
        mapping_xmls = map(lambda name: os.path.join(VOTACOES_FOLDER, name), filtering_xmls)
        return mapping_xmls

    def import_votings(self):

        # for xml_file in ['importadores/dados/senado/ListaVotacoes2011.xml']:
        for xml_file in self.return_votacoes_folder_content():
            logger.info('Importando %s' % xml_file)
            self.save_in_database(xml_file)


class ImportadorSenadores:

    # This list needs to be updated year by year
    # 52 is the minimum legislature because we just have voting from 2005 to now
    LEGISLATURES = [52, 53, 54, 55]
                                
    def __init__(self):
        self.senado = models.CasaLegislativa.objects.get(nome_curto=SHORT_NAME)

    def convert_string_to_object(self, data_str):
        """Convert string "dd/mm/aaaa" to datetime object; Return None
        if data_str is invalid"""
        DATA_REGEX = '(\d\d?)/(\d\d?)/(\d{4})'
        res = re.match(DATA_REGEX, data_str)
        if res:
            new_str = '%s-%s-%s 0:0:0' % (
                res.group(3), res.group(2), res.group(1))
            return parse_datetime(new_str)
        else:
            raise ValueError

    def find_political_party(self, political_party_name):
        if political_party_name is not None:
            political_party_name = political_party_name.strip()

        # Receive political parties by name.
        political_party = models.Partido.from_name(political_party_name)

        if political_party is None:
            logger.warn('Não achou o partido %s' % political_party_name)
            political_party = models.Partido.get_no_party()
        return political_party

    def find_political_party_by_name(self, partidos_tree):
        """By hour, returns the last party in the list"""

        for political_party_tree in partidos_tree:
            last_partido_tree = political_party_tree
        return last_partido_tree.find_legislature('SiglaPartido').text

    def process_legislature(self, leg_tree):

        parliamentaries_tree = leg_tree.find_legislature('Parlamentar').find_legislature('Parlamentares')
        for parlamentar_tree in parliamentaries_tree:

            # Receive parliamentary's code.
            parliamentary_code = parlamentar_tree.find_legislature('CodigoParlamentar').text

            # Receive parliamentary's name.
            parliamentary_name = parlamentar_tree.find_legislature('NomeParlamentar').text

            # Receive parliamentary's UF.
            parliamentary_uf = parlamentar_tree.find_legislature('SiglaUF').text

            # Receive 'Partidos' from 'parlamentar_tree'.
            political_parties_tree = parlamentar_tree.find_legislature('Partidos')

            if political_parties_tree is not None:
                political_party_name = self.find_political_party_by_name(political_parties_tree)
            else:
                logger.warn('Senador %s não possui lista de partidos!' % parliamentary_name)
                political_party_name = None
            initial_year_of_legislature = parlamentar_tree.find_legislature('AnoInicio').text
            final_year_of_legislature = parlamentar_tree.find_legislature('AnoFim').text

            if political_party_name == 'PC DO B':
                political_party_name = 'PCdoB'
            date_of_inicial_legislature = self.convert_string_to_object('01/01/%s' % initial_year_of_legislature)
            date_of_final_legislature = self.convert_string_to_object('31/12/%s' % final_year_of_legislature)
            political_party = self.find_political_party(political_party_name)

            if not models.Legislatura.objects.filter(inicio=date_of_inicial_legislature,
                                                     fim=date_of_final_legislature,
                                                     parlamentar__nome=parliamentary_name,
                                                     partido__nome=political_party_name
                                                     ).exists():
                logger.info('Importando senador %s (%s-%s)' %
                            (parliamentary_name, political_party_name, parliamentary_uf))

                if models.Parlamentar.objects.filter(nome=parliamentary_name,
                                                     id_parlamentar=parliamentary_code
                                                     ).exists():
                    senator = models.Parlamentar.objects.get(
                        nome=parliamentary_name, id_parlamentar=parliamentary_code)
                else:
                    senator = models.Parlamentar()
                    senator.id_parlamentar = parliamentary_code
                    senator.nome = parliamentary_name
                    senator.save_data_in_file()

                legislature = models.Legislatura()
                legislature.parlamentar = senator
                legislature.casa_legislativa = self.senado
                legislature.inicio = date_of_inicial_legislature
                legislature.fim = date_of_final_legislature
                legislature.partido = political_party
                legislature.localidade = parliamentary_uf
                legislature.save_data_in_file()

    def import_senators(self):
        """Create parliamentaries and legislatures in database"""

        # Receive Web Service from Senate.
        senws = SenadoWS()

        for id_leg in ImportadorSenadores.LEGISLATURES:
            logger.info("Importando senadores da legislatura %s" % id_leg)
            legislature_tree = senws.get_senators_from_legislature(id_leg)
            self.process_legislature(legislature_tree)