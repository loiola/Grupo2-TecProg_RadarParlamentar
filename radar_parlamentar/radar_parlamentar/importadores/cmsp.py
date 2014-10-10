# !/usr/bin/python
# coding=utf8

# Copyright (C) 2012, Leonardo Leite, Guilherme Januário, Diego Rabatone
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

"""CMSP Module (Câmara Municipal de São Paulo)"""

from __future__ import unicode_literals
from django.utils.dateparse import parse_datetime
from modelagem import models
import re
import sys
import os
import xml.etree.ElementTree as etree


def main():
    """Imports all data from XML by importer"""

    print 'IMPORTANDO DADOS DA CAMARA MUNICIPAL DE SAO PAULO (CMSP)'
    gerador_casa = GeradorCasaLegislativa()
    cmsp = gerador_casa.generate_cmsp()
    importer = importerCMSP(cmsp)
    for xml in [XML2010, XML2011, XML2012, XML2013, XML2014]:
        importer.import_from(xml)
    print 'Importacao dos dados da Camara Municipal de Sao Paulo (CMSP) terminada'


# Date on which the XML files were updated
ULTIMA_ATUALIZACAO = parse_datetime('2012-12-31 0:0:0')

MODULE_DIR = os.path.abspath(os.path.dirname(__file__))

# Files with the data provided by CMSP
XML2010 = os.path.join(MODULE_DIR, 'dados/cmsp/cmsp2010.xml')
XML2011 = os.path.join(MODULE_DIR, 'dados/cmsp/cmsp2011.xml')
XML2012 = os.path.join(MODULE_DIR, 'dados/cmsp/cmsp2012.xml')
XML2013 = os.path.join(MODULE_DIR, 'dados/cmsp/cmsp2013.xml')
XML2014 = os.path.join(MODULE_DIR, 'dados/cmsp/cmsp2014.xml')

# Types of propositions found in the PBMC XMLs. Be list helps identify the votes 
# that are propositions. Examples of votes that are not propositions: Postponement 
# of prolongation Expedient; Other items postponement of the Tariff.
TIPOS_PROPOSICOES = ['PL', 'PLO', 'PDL']

# Regex that captures a proposition name (ex: PL 12/2010)
PROP_REGEX = '([a-zA-Z]{1,3}) ([0-9]{1,4}) ?/([0-9]{4})'

#Receives the initial date of the period of data
initial_period_parseCMSP = parse_datetime('2010-01-01 0:0:0')

#Receives the end date of the period of data
final_period_parseCMSP = parse_datetime('2012-12-31 0:0:0')


class GeradorCasaLegislativa(object):

    def generate_cmsp(self):
        try:
            cmsp = models.CasaLegislativa.objects.get(nome_curto='cmsp')
        except models.CasaLegislativa.DoesNotExist:
            cmsp = self.save_cmsp()
        return cmsp

    def save_cmsp(self):
        cmsp = models.CasaLegislativa()
        cmsp.nome = 'Câmara Municipal de São Paulo'
        cmsp.nome_curto = 'cmsp'
        cmsp.esfera = models.MUNICIPAL
        cmsp.local = 'São Paulo - SP'
        cmsp.atualizacao = ULTIMA_ATUALIZACAO
        cmsp.save()
        return cmsp


class XmlCMSP:

    def __init__(self, cmsp, verbose=False):
        self.parlamentares = {}
        self.cmsp = cmsp
        self.verbose = verbose

    def convert_data(self, data_str):
        """Converts string "d/m/y" to datetime object;
        returns None if data_str is invalid"""

        DATA_REGEX = '(\d\d?)/(\d\d?)/(\d{4})'
        res = re.match(DATA_REGEX, data_str)
        if res:
            new_str = '%s-%s-%s 0:0:0' % (
                res.group(3), res.group(2), res.group(1))
            return parse_datetime(new_str)
        else:
            return None

    def search_propostition_by_name(self, texto):
        """Search "type num/ano" in the text"""

        res = re.search(PROP_REGEX, texto)
        if res:
            proposition_name = res.group(1).upper()
            if self.return_valid_propositions(proposition_name, texto):
                return res.group(0).upper()
        return None

    def return_valid_propositions(self, nome_prop, texto):
        return nome_prop in TIPOS_PROPOSICOES and not 'Inversão' in texto

    def extract_year_from_num_and_year(self, prop_nome):
        """Extract year from "tipo num/ano" """
        res = re.search(PROP_REGEX, prop_nome)
        if res:
            return res.group(1), res.group(2), res.group(3)
        else:
            return None, None, None

    def interpret_vote(self, voto):
        """Interprets as voting is up in XML and responds suitability modeling 
        in models.py"""

        if voto == 'Não':
            return models.NAO
        elif voto == 'Sim':
            return models.SIM
        elif voto == 'Não votou':
            return models.AUSENTE
        elif voto == 'Abstenção':
            return models.ABSTENCAO
        else:
            print 'tipo de voto (%s) nao mapeado!' % voto
            return models.ABSTENCAO

    # The 'partido' method can not be renamed or break the code.
    def partido(self, ver_tree):

        # Political parties stores coming to ver_tree.
        political_party_name = ver_tree.get('Partido').strip()

        # Stores political party name coming from 'partido' method (in models)
        political_party = models.Partido.from_name(political_party_name)

        if political_party is None:
            print 'Nao achou o search_political_party %s' % political_party_name
            political_party = models.Partido.get_no_party()
        return political_party

    def list_parliamentary(self, ver_tree):

        # Store 'IDParlamentar' coming from 'ver_tree'
        parliamentary_id = ver_tree.get('IDParlamentar')

        if parliamentary_id in self.parlamentares:

            # Receives the parliamentary list with their IDs.
            voter = self.parlamentares[parliamentary_id]

        else:
            voter = models.Parlamentar()
            voter.save()
            voter.id_parlamentar = parliamentary_id
            voter.nome = ver_tree.get('NomeParlamentar')
            voter.save()
            if self.verbose:
                print 'Vereador %s salvo' % voter
            self.parlamentares[parliamentary_id] = voter
            # TODO gender
        return voter

    # The 'legislatura' method can not be renamed or break the code.
    def legislatura(self, ver_tree):
        """Creates and returns legislatura for the given political party"""

        #Initializing the variable, passing as parameter 'ver_tree'.
        political_party = self.partido(ver_tree)

        # Initializing the variable, passing as parameter 'ver_tree'.
        voter = self.list_parliamentary(ver_tree)

        # Store filtered objects of class 'Legislatura'.
        legislatures = models.Legislatura.objects.filter(
            parlamentar=voter, partido=political_party, casa_legislativa=self.cmsp)

        if legislatures:

            # Get list of objects contained in 'Legislatures'. If the objects don't exist, the list will be created.
            legislature = legislatures[0]

        else:
            legislature = models.Legislatura()
            legislature.parlamentar = voter
            legislature.partido = political_party
            legislature.casa_legislativa = self.cmsp
            legislature.inicio = initial_period_parseCMSP
            legislature.fim = final_period_parseCMSP
            legislature.save()

        return legislature

    def get_votes_from_tree(self, vot_tree, votacao):
        """Extract list of votes the vote of XML and saved in the database
        Arguments:
           vot_tree -- tree of votes
           votacao -- object of 'Votacao' type"""

        for ver_tree in vot_tree.getchildren():
            if ver_tree.tag == 'Vereador':
                leg = self.legislatura(ver_tree)
                vote = models.Voto()
                vote.legislatura = leg
                vote.votacao = votacao
                vote.opcao = self.interpret_vote(ver_tree.get('Voto'))
                if vote.opcao is not None:
                    vote.save()

    def get_votings_from_tree(self, proposicoes, votacoes, vot_tree):

        # If the votation is nominal, vot_tree gets the subject and the menu
        # Gets the type of voting from 'vot_tree'.
        type_of_votating = vot_tree.get('TipoVotacao')

        if vot_tree.tag == 'Votacao' and type_of_votating == 'Nominal':

            # Receive 'Materia' and 'Ementa' from 'vot_tree'.
            abstract = '%s -- %s' % (
                vot_tree.get('Materia'), vot_tree.get('Ementa'))

            # Prop_nome is as internally identifies the proposals
            # We want to know which proposition the analyzed voting is associated
            # Will return if search_propostition_by_name vote for Proposition
            proposition_name = self.search_propostition_by_name(abstract)

            # If the voting was associable to a proposition, so..
            if (proposition_name):
                id_vote = vot_tree.get('VotacaoID')
                voting_blank = models.Votacao.objects.filter(
                    id_vot=id_vote)
                if voting_blank:
                    vot = voting_blank[0]
                else:
                    if proposition_name in proposicoes:
                        proposition = proposicoes[proposition_name]

                    # The propositon was not in dictionary yet, so we have to create and
                    # register it on dictionary
                    else:
                        proposition = models.Proposicao()
                        proposition.sigla, proposition.numero, proposition.ano = self.extract_year_from_num_and_year(
                            proposition_name)
                        proposition.casa_legislativa = self.cmsp
                        proposicoes[proposition_name] = proposition

                    if self.verbose:
                        print 'Proposicao %s salva' % proposition
                    proposition.save()
                    vot = models.Votacao()

                    # To create de primary key and assign the votes
                    vot.save()
                    vot.id_vot = id_vote
                    vot.descricao = abstract
                    vot.data = self.convert_data(vot_tree.get('DataDaSessao'))
                    vot.resultado = vot_tree.get('Resultado')
                    self.get_votes_from_tree(vot_tree, vot)
                    vot.proposicao = proposition
                    if self.verbose:
                        print 'Votacao %s salva' % vot
                    else:
                        self.show_progress()
                    vot.save()

                votacoes.append(vot)

    def show_progress(self):
        """Show progress on screen"""
        sys.stdout.write('x')
        sys.stdout.flush()


class importerCMSP:
    """Save the CMSP XML archives datas in database"""

    def __init__(self, cmsp, verbose=False):
        """verbose (booleano) -- activate/desactivate prints on screen"""

        self.verbose = verbose
        self.xml_cmsp = XmlCMSP(cmsp, verbose)

    def import_from(self, xml_file):
        """Save in Django's database and returns the voting list"""

        if self.verbose:
            print "importando de: " + str(xml_file)

        tree = importerCMSP.open_xml(xml_file)
        propositions = {}
            # The ley is a string (ex: 'pl 127/2004'); value ix object from
            # Proposiction type
        votings = []
        self.analyze_xml(propositions, votings, tree)
        return votings

    def analyze_xml(self, proposicoes, votacoes, tree):
        for vot_tree in tree.getchildren():
            self.xml_cmsp.get_votings_from_tree(proposicoes, votacoes, vot_tree)

    @staticmethod
    def open_xml(xml_file):
    # f = open(xml_file, 'r')
    # xml = f.read()
    # f.close()
    # return etree.fromstring(xml)
        return etree.parse(xml_file).getroot()
