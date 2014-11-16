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

"""Convencao Module (Convenção Nacional Francesa)

Classes:
    ImportadorConvencao generate datas for fictitious legislative house called 
    Convenção Nacional Francesa"""

from __future__ import unicode_literals
from django.utils.dateparse import parse_datetime
from models import models

# Date of last refresh on data.
LAST_REFRESH = parse_datetime('2012-06-01 0:0:0')

# Date on begin of period of voting.
BEGIN_PERIOD = parse_datetime('1989-01-01 0:0:0')

# Date on end of period of voting.
END_PERIOD = parse_datetime('1989-12-30 0:0:0')

# Date on begin the first semester.
BEGIN_FIRST_SEMESTER = parse_datetime('1989-02-02 0:0:0')

# Date on begin the second semester.
BEGIN_SECOND_SEMESTER = parse_datetime('1989-10-10 0:0:0')

PARLAMENTS_PER_PARTY = 3

GIRONDINES = 'Girondinos'
JACOBINES = 'Jacobinos'
MONARQUIST = 'Monarquistas'

def main():

    print 'IMPORTANDO DADOS DA CONVENÇÃO NACIONAL FRANCESA'
    importer = ImportadorConvencao()
    importer.import_data()

    return None

class ImportadorConvencao:

    # Get instance of the new legislative house:
    def create_new_legislative_house(self):

        conv = models.CasaLegislativa()
        conv.name = 'Convenção Nacional Francesa'
        conv.short_name = 'conv'
        conv.sphere = models.FEDERAL
        conv.local = 'Paris (FR)'
        conv.update = LAST_REFRESH
        conv.save_data_in_file()

        return conv

    # Get instance the new party:
    def create_new_political_party(self):

        girondinos = models.Partido()
        girondinos.name = GIRONDINES
        girondinos.number = 27
        girondinos.color = '#008000'
        girondinos.save_data_in_file()
        jacobinos = models.Partido()
        jacobinos.name = JACOBINES
        jacobinos.number = 42
        jacobinos.color = '#FF0000'
        jacobinos.save_data_in_file()
        monarquistas = models.Partido()
        monarquistas.name = MONARQUIST
        monarquistas.number = 79
        monarquistas.color = '#800080'
        monarquistas.save_data_in_file()
        self.political_parties = {girondinos, jacobinos, monarquistas}

        return None


    # Get instance the new legislature:
    def get_instance_new_legislature(self):

        # Name search_political_party => list of party legislaturas
        self.legislatures = {}
        for p in self.political_parties:
            self.legislatures[p.nome] = []
            for i in range(0, PARLAMENTS_PER_PARTY):

                parliamentary = models.Parlamentar()
                parliamentary.id_parlamentar = '%s%s' % (p.nome[0], str(i))
                parliamentary.name = 'Pierre'
                parliamentary.save_data_in_file()

                leg = models.Legislatura()
                leg.legislative_house = self.casa
                leg.begin = BEGIN_PERIOD
                leg.end = END_PERIOD
                leg.political_party = p
                leg.parliamentary = parliamentary
                leg.save_data_in_file()
                self.legislatures[p.nome].append(leg)

        return None


    # Get instance the new proposition:
    def get_instance_new_proposition(self, number, descripcion):

        proposition = models.Proposicao()
        proposition.id_prop = number
        proposition.sigla = 'PL'
        proposition.numero = number
        proposition.ementa = descripcion
        proposition.descricao = descripcion
        proposition.casa_legislativa = self.casa
        proposition.save_data_in_file()

        return proposition


    # Get instance the new voting:
    def get_instance_new_voting(self, number, description, data, proposition):

        voting = models.Votacao()
        voting.id_vot = number
        voting.description = description
        voting.date = data
        voting.proposition = proposition
        voting.save_data_in_file()

        return voting


    # Get instance the new vote:
    def get_instance_new_vote(self, votation, name_party, options):

        # Options is an options list (YES, NO...):
        for i in range(0, PARLAMENTS_PER_PARTY):
            vote = models.Voto()
            vote.legislature = self.legislatures[name_party][i]
            vote.option = options[i]
            vote.voting = votation
            vote.save_data_in_file()

        return None


    # Get instance the new voting:
    def get_instance_girondine_votes(self, votacao):

        votes_girondinos = [models.SIM, models.ABSTENCAO, models.NAO]
        self.get_instance_new_vote(votacao, GIRONDINES, votes_girondinos)

        return None

    def get_instance_jaconbine_votes(self, votacao):

        votes_jacobinos = [models.SIM, models.SIM, models.SIM]
        self.get_instance_new_vote(votacao, JACOBINES, votes_jacobinos)

        return None


    def get_instance_monarquist_votes(self, votacao):

        votes_monarquistas = [models.NAO, models.NAO, models.NAO]
        self.get_instance_new_vote(votacao, MONARQUIST, votes_monarquistas)

        return None


    def create_new_voting_1(self):

        NUMBER = '1'
        DESCRIPTION = 'Reforma agrária'
        proposition = self.get_instance_new_proposition(NUMBER, DESCRIPTION)
        voting = self.get_instance_new_voting(
            NUMBER, DESCRIPTION, BEGIN_FIRST_SEMESTER, proposition)

        self.get_instance_girondine_votes(voting)

        self.get_instance_jaconbine_votes(voting)

        self.get_instance_monarquist_votes(voting)

        return None


    # Get instance the new voting:
    def get_instance_girondine_votes2(self, votacao):

        votes_girondinos = [models.NAO, models.NAO, models.NAO]
        self.get_instance_new_vote(votacao, GIRONDINES, votes_girondinos)

        return None

    def get_instance_jaconbine_votes2(self, votacao):

        votes_jacobinos = [models.NAO, models.NAO, models.NAO]
        self.get_instance_new_vote(votacao, JACOBINES, votes_jacobinos)

        return None

    def get_instance_monarquist_votes2(self, votacao):

        votes_monarquistas = [models.SIM, models.SIM, models.SIM]
        self.get_instance_new_vote(votacao, MONARQUIST, votes_monarquistas)

        return None

    def create_new_voting2(self):

        NUMBER = '2'
        DESCRIPTION = 'Aumento da pensão dos nobres'
        proposition = self.get_instance_new_proposition(NUMBER, DESCRIPTION)
        voting = self.get_instance_new_voting(
            NUMBER, DESCRIPTION, BEGIN_FIRST_SEMESTER, proposition)

        self.get_instance_girondine_votes2(voting)

        self.get_instance_jaconbine_votes2(voting)

        self.get_instance_monarquist_votes2(voting)

        return None


    # Get instance the new voting:
    def get_instance_girondine_votes3(self, votacao):

        votes_girondinos = [models.NAO, models.NAO, models.SIM]
        self.get_instance_new_vote(votacao, GIRONDINES, votes_girondinos)

        return None

    def _new_votation3(self):

        NUMBER = '3'
        DESCRIPTION = 'Institui o Dia de Carlos Magno'
        proposition = self.get_instance_new_proposition(NUMBER, DESCRIPTION)
        voting = self.get_instance_new_voting(
            NUMBER, DESCRIPTION, BEGIN_FIRST_SEMESTER, proposition)

        self.get_instance_girondine_votes3(voting)

        self.get_instance_jaconbine_votes2(voting)

        self.get_instance_monarquist_votes2(voting)

        return None


    # Get instance the new voting:
    def get_instance_girondine_votes4(self, votacao):

        votos_girondinos = [models.SIM, models.SIM, models.SIM]
        self.get_instance_new_vote(votacao, GIRONDINES, votos_girondinos)

        return None

    def get_instance_jaconbine_votes4(self, votacao):

        votos_jacobinos = [models.SIM, models.ABSTENCAO, models.NAO]
        self.get_instance_new_vote(votacao, JACOBINES, votos_jacobinos)

        return None

    def get_instance_monarquist_votes4(self, votacao):

        votos_monarquistas = [models.SIM, models.NAO, models.AUSENTE]
        self.get_instance_new_vote(votacao, MONARQUIST, votos_monarquistas)

        return None

    def _new_votation4(self):

        NUMBER = '4'
        DESCRIPTION = 'Diminuição de impostos sobre a indústria'
        proposition = self.get_instance_new_proposition(NUMBER, DESCRIPTION)
        voting = self.get_instance_new_voting(
            NUMBER, DESCRIPTION, BEGIN_FIRST_SEMESTER, proposition)

        self.get_instance_girondine_votes4(voting)

        self.get_instance_jaconbine_votes4(voting)

        self.get_instance_monarquist_votes4(voting)

        return None


    # Get instance the new voting:
    def get_instance_girondine_votes5(self, votacao):

        votes_girondinos = [models.SIM, models.SIM, models.ABSTENCAO]
        self.get_instance_new_vote(votacao, GIRONDINES, votes_girondinos)

        return None

    def create_new_voting5(self):

        NUMBER = '5'
        DESCRIPTION = 'Guilhotinar o Conde Pierre'
        proposition = self.get_instance_new_proposition(NUMBER, DESCRIPTION)
        voting = self.get_instance_new_voting(
            NUMBER, DESCRIPTION, BEGIN_SECOND_SEMESTER, proposition)

        self.get_instance_girondine_votes5(voting)

        self.get_instance_jaconbine_votes(voting)

        self.get_instance_monarquist_votes(voting)

        return None


    # Get instance the new voting:
    def get_instance_monarquist_votes6(self, votacao):

        votes_monarquistas = [models.AUSENTE, models.SIM, models.SIM]
        self.get_instance_new_vote(votacao, MONARQUIST, votes_monarquistas)

        return None

    def create_new_voting6(self):

        NUMBER = '6'
        DESCRIPTION = 'Criação de novas escolas'
        proposition = self.get_instance_new_proposition(NUMBER, DESCRIPTION)
        voting = self.get_instance_new_voting(
            NUMBER, DESCRIPTION, BEGIN_SECOND_SEMESTER, proposition)

        self.get_instance_girondine_votes4(voting)

        self.get_instance_jaconbine_votes(voting)

        self.get_instance_monarquist_votes6(voting)

        return None


    # Get instance the new voting:
    def get_instance_monarquist_votes7(self, votacao):

        votes_monarquistas = [models.SIM, models.AUSENTE, models.SIM]
        self.get_instance_new_vote(votacao, MONARQUIST, votes_monarquistas)

        return None

    def create_new_votation7(self):

        NUMBER = '7'
        DESCRIPTION = 'Aumento do efetivo militar'
        proposition = self.get_instance_new_proposition(NUMBER, DESCRIPTION)
        voting = self.get_instance_new_voting(
            NUMBER, DESCRIPTION, BEGIN_SECOND_SEMESTER, proposition)

        self.get_instance_girondine_votes5(voting)

        self.get_instance_jaconbine_votes(voting)

        self.get_instance_monarquist_votes7(voting)

        return None


    # Voting with different attributes for test:
    def get_instance_jacobine_votes8(self, votacao):

        votes_jacobinos = [models.ABSTENCAO, models.NAO, models.NAO]
        self.get_instance_new_vote(votacao, JACOBINES, votes_jacobinos)

        return None

    def create_new_votation8(self):

        NUMBER = '8'
        DESCRIPTION = 'Guerra contra a Inglaterra'
        proposition = models.Proposicao()
        proposition.id_prop = NUMBER
        proposition.acronym = 'PL'
        proposition.number = NUMBER
        proposition.menu = 'o uso proibido de armas químicas'
        proposition.description = 'descricao da guerra'
        proposition.legislative_house = self.casa
        proposition.indexing = 'bombas, efeitos, destruições'
        proposition.save_data_in_file()
        voting = self.get_instance_new_voting(
            NUMBER, DESCRIPTION, BEGIN_SECOND_SEMESTER, proposition)

        self.get_instance_girondine_votes2(voting)

        self.get_instance_jacobine_votes8(voting)

        self.get_instance_monarquist_votes7(voting)

        return None

    def import_data(self):

        self.casa = self.create_new_legislative_house()
        self.create_new_political_party()
        self.get_instance_new_legislature()
        self.create_new_voting_1()
        self.create_new_voting2()
        self._new_votation3()
        self._new_votation4()
        self.create_new_voting5()
        self.create_new_voting6()
        self.create_new_votation7()
        self.create_new_votation8()
        self.get_instance_new_proposition('9', 'Legalizacao da maconha')

        return None