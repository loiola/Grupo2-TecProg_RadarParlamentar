# coding=utf8

# Copyright (C) 2012, Leonardo Leite, Eduardo Hideo, Saulo Trento, Diego Rabatone
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
from django.db import models
import re
import logging
import os

logger = logging.getLogger("radar")
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))

SIM = 'SIM'
NAO = 'NAO'
ABSTENCAO = 'ABSTENCAO'
OBSTRUCAO = 'OBSTRUCAO'
AUSENTE = 'AUSENTE'

OPCOES = (
    (SIM, "Sim"),
    (NAO, "Não"),
    (ABSTENCAO, "Abstenção"),
    (OBSTRUCAO, "Obstrução"),
    (AUSENTE, "Ausente"),
)

M = "M"
F = "F"

GENEROS = (
    (M, "Masculino"),
    (F, "Feminino"),
)

MUNICIPAL = 'MUNICIPAL'
ESTADUAL = 'ESTADUAL'
FEDERAL = 'FEDERAL'

ESFERAS = (
    (MUNICIPAL, 'Municipal'),
    (ESTADUAL, 'Estadual'),
    (FEDERAL, 'Federal'),
)

QUADRIENIO = "QUADRIENIO"
BIENIO = 'BIENIO'
ANO = 'ANO'
SEMESTRE = 'SEMESTRE'
MES = 'MES'

PERIODOS = (
    (QUADRIENIO, 'QUADRIENIO'),
    (BIENIO, 'BIENIO'),
    (ANO, 'ano'),
    (SEMESTRE, 'semestre'),
    (MES, 'mes')
)

SEM_PARTIDO = 'Sem partido'
COR_PRETA = '#000000'


class Indexadores(models.Model):
    """Terms used in the indexing of propositions

     attributes:
         party_term - string; ex: "woman" or "political party"
         principa_party_term - bool; identifying whether a term is the main
                     a line of synonyms, the term being used."""

    party_term = models.CharField(max_length=120)
    principa_party_term = models.BooleanField()

    def __unicode__(self):
        return '%s-%s-%s' % (self.party_name, self.party_number, self.party_color)


class Partido(models.Model):
    """Political party.

     attributes:
         party_name - string; eg 'EN'
         party_number - int; ex: '13 '
         party_color - string; eg #FFFFFF

     Class methods:
         from_nome (name): returns object of type Party
         from_party_number (number): returns object of type Party
         get_sem_partido (): returns a party called 'NO PARTY'"""

    LISTA_PARTIDOS = os.path.join(MODULE_DIR, 'recursos/partidos.txt')

    party_name = models.CharField(max_length=12)
    party_number = models.IntegerField()
    party_color = models.CharField(max_length=7)

    @classmethod
    def from_party_name(cls, party_name):
        """Given a name and return an object of type Party
             or None if name is invalid"""

        if party_name is None:
            return None

        # procura primeiro no banco de dados
        party_p = Partido.objects.filter(party_name=party_name)
        if party_p:
            return party_p[0]
        else:
            # se não estiver no BD, procura hardcoded
            return cls._from_regex(1, party_name.strip())

    @classmethod
    def from_party_number(cls, party_number):
        """Receives a number (int) and returns an object of type Party
        or None if name is invalid"""

        if party_number is None:
            return None

        # procura primeiro no banco de dados
        party_p = Partido.objects.filter(party_number=party_number)
        if party_p:
            return party_p[0]
        else:
            # se não estiver no BD, procura no arquivo hardcoded
            return cls._from_regex(2, str(party_number))

    @classmethod
    def get_sem_partido(cls):
        """Returns a party called 'NO PARTY'"""

        no_party_list = Partido.objects.filter(party_name=SEM_PARTIDO)
        if not no_party_list:
            party = Partido()
            party.party_name = SEM_PARTIDO
            party.party_number = 0
            party.party_color = COR_PRETA
            party.save()
        else:
            party = no_party_list[0]
        return party

    @classmethod
    def _from_regex(cls, idx, key):
        PARTIDO_REGEX = '([a-zA-Z]*) *([0-9]{2}) *(#+[0-f]{6})'
        party_list = open(cls.LISTA_PARTIDOS)
        for line in party_list:
            res = re.search(PARTIDO_REGEX, line)
            if res and res.group(idx) == key:
                party = Partido()
                party.party_name = res.group(1)
                party.party_number = int(res.group(2))
                party.party_color = res.group(3)
                party.save()
                return party
        return None

    def __unicode__(self):
        return '%s-%s' % (self.party_name, self.party_number)


class CasaLegislativa(models.Model):
    """IType institution Senate, House etc.

     attributes:
         name - string; eg 'City Hall of São Paulo'
         acronym_legislative_house - string; will be used to generate links.
                         ex 'PBMC' to 'Municipality of São Paulo'
         sphere - string (municipal, state, federal)
         location - string; ex 'Sao Paulo' for CMSP
         UPDATE - date the database was updated by
                             last time with this house polls"""

    legislative_house_name = models.CharField(max_length=100)
    acronym_legislative_house = models.CharField(max_length=50, unique=True)
    sphere = models.CharField(max_length=10, choices=ESFERAS)
    legislative_house_place = models.CharField(max_length=100)
    db_atualization_date = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return self.legislative_house_name

    def partidos(self):
        #Returns the existing parties this legislative house
        return Partido.objects.filter(
            legislatura__casa_legislativa=self).distinct()

    def legislaturas(self):
        #Returns existing legislative legislatures this house
        return Legislatura.objects.filter(casa_legislativa=self).distinct()

    def num_votacao(self, data_inicial=None, data_final=None):
        #returns the number of voting on a legislative house
        return Votacao.por_casa_legislativa(
            self, data_inicial, data_final).count()

    def num_votos(self, data_inicio=None, data_fim=None):
        #returns the number of votes in a legislative house
        votings = Votacao.por_casa_legislativa(self, data_inicio, data_fim)
        Votos = []
        for votacao in votings:
            Votos += votacao.Votos()
        return len(Votos)

    @staticmethod
    def deleta_casa(nome_casa_curto):
        """Method that deletes certain record of legislative house
             cascade
             arguments:
                 nome_casa - Name of the house to be deleted"""

        try:
            try:
                CasaLegislativa.objects.get(
                    acronym_legislative_house=nome_casa_curto).delete()

            except CasaLegislativa.DoesNotExist:
                print 'Casa legislativa ' + nome_casa_curto + ' não existe'
        except:
            print('Possivelmente a operacao extrapolou o limite de '
                  'operacoes do SQLite, tente utilizar o MySQL')


class PeriodoCasaLegislativa(object):
    """attributes:
         ini, end - datetime objects
         period_description - Description of the period
         votings_amount - whole"""

    def __init__(self, data_inicio, data_fim, votings_amount=0):
        # TODO self.casa_legislativa = ...
        self.inicial_voting_date = data_inicio
        self.final_voting_date = data_fim
        self.votings_amount = votings_amount
        self.period_description = ""
        self.period_description = unicode(self)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        if not self.period_description:
            self._build_string()
        return self.period_description

    def _build_string(self):
        description_string = ''
        days_amount = self.final_voting_date - self.inicial_voting_date
        if days_amount.days < 35:  # período é de um mês
            meses = ['',
                     'Jan',
                     'Fev',
                     'Mar',
                     'Abr',
                     'Maio',
                     'Jun',
                     'Jul',
                     'Ago',
                     'Set',
                     'Out',
                     'Nov',
                     'Dez']
            description_string += str(self.inicial_voting_date.year)
            description_string += " " + str(meses[self.inicial_voting_date.month])
        elif days_amount.days < 200:  # periodo é de um semestre
            description_string += str(self.inicial_voting_date.year)
            if self.inicial_voting_date.month < 6:
                description_string += " 1o Semestre"
            else:
                description_string += " 2o Semestre"
        elif days_amount.days < 370:  # periodo é de um ano
            description_string += str(self.inicial_voting_date.year)
        elif days_amount.days < 750:  # periodo é um biênio
            description_string += str(self.inicial_voting_date.year) + " e "
            description_string += str(self.final_voting_date.year)
        elif days_amount.days < 1500:  # periodo é um quadriênio
            description_string += str(self.inicial_voting_date.year) + " a "
            description_string += str(self.final_voting_date.year)
        self.period_description = description_string


class Parlamentar(models.Model):
    """Um parlamentar.

    Atributos:
        parliamentary_id - string identificadora de acordo a fonte de dados
        parliamentary_name, parliamentary_gender -- strings"""

    # obs: parliamentary_id não é chave primária!
    parliamentary_id = models.CharField(max_length=100, blank=True)
    parliamentary_name = models.CharField(max_length=100)
    parliamentary_gender = models.CharField(max_length=10, choices=GENEROS, blank=True)

    def __unicode__(self):
        return self.parliamentary_name


class Legislatura(models.Model):
    """A continuous period of time in which a policy acts as parliamentarian.
     It's different mandate. A term lasts four years. If the holder leaves
     and alternate takes, then we have an exchange of legislature.

     attributes:
         Parliament - Parliamentary exercising the legislature;
                         object of type Parliamentary
         lesgilative_house - object type CasaLegislativa
         start, end - dates indicating the period
         party - object of type Party
         location - string; eg 'SP', 'RJ' if the Senate or
                                     Chamber of Deputies

     methods:
         find - search by date legislature and parliamentary"""

    parliamentary = models.ForeignKey(Parlamentar)
    lesgilative_house = models.ForeignKey(CasaLegislativa, null=True)
    lesgilature_initial_date = models.DateField(null=True)
    lesgilature_final_date = models.DateField(null=True)
    party = models.ForeignKey(Partido)
    legislature_place = models.CharField(max_length=100, blank=True)

    @staticmethod
    def find(data, nome_parlamentar):
        """Search the legislature of a parliamentary by name
             on a certain date
            arguments:
              date - the date object type
              nome_parlamentar - string
            Return: object of type Legislature
            If not, throws exception ValueError"""

        # Assumimos que uma pessoa não pode assumir
        # duas legislaturas em um dado período!
        search_by_parliamentary_name = Legislatura.objects.filter(parlamentar__nome=nome_parlamentar)
        for leg in search_by_parliamentary_name:
            if data >= leg.lesgilature_initial_date and data <= leg.lesgilature_final_date:
                return leg
        raise ValueError('Não achei legislatura para %s em %s' %
                         (nome_parlamentar, data))

    def __unicode__(self):
        return "%s - %s@%s [%s, %s]" % (
            self.parliamentary,
            self.party,
            self.lesgilative_house.acronym_legislative_house,
            self.lesgilature_initial_date,
            self.lesgilature_final_date)


class Proposicao(models.Model):
    """Parliamentary proposition (bill).

     attributes:
         proposition_name - identifier string according to data source
         abbreviation, number, year - strings that form the legal name of the proposition
         proposition_menu-- succinct and official description
         Description - more detailed description
         indexing - key words
         authors - list of objects of type Parliamentary
         data_apresentacao - when it was proposed
         situation - as is now
         lesgilative_house - object type CasaLegislativa

     methods:
         name: return symbol number / year"""

    # obs: proposition_name is not a primary key!
    proposition_id = models.CharField(max_length=100, blank=True)
    proposition_acronym = models.CharField(max_length=10)
    proposition_number = models.CharField(max_length=10)
    proposition_year = models.CharField(max_length=4)
    proposition_menu = models.TextField(blank=True)
    proposition_description = models.TextField(blank=True)
    proposition_index = models.TextField(blank=True)
    proposition_date = models.DateField(null=True)
    proposition_status = models.TextField(blank=True)
    lesgilative_house = models.ForeignKey(CasaLegislativa, null=True)
    principal_author = models.TextField(blank=True)
    #TODO
    #principal_author = models.ForeignKey(
    #    Parlamentar,
    #    null=True,
    #    related_name='Autor principal')
    authors = models.ManyToManyField(
        Parlamentar,
        null=True,
        related_name='demais_autores')

    def nome(self):
        return "%s %s/%s" % (self.proposition_acronym, self.proposition_number, self.proposition_year)

    def __unicode__(self):
        return "[%s] %s" % (self.nome(), self.proposition_menu)


class Votacao(models.Model):
    """Vote in planário.

     attributes:
         voting_id - identifier string according to data source
         voting_description, results - strings
         voting_date - date of the vote (type date)
         voting_result - string
         proposition - Proposition object of type
    #    null=True,
    #    related_name='Autor principal')
     methods:
         vote ()
         por_partido ()"""

    # obs: voting_id is not a primary key!
    voting_id = models.CharField(max_length=100, blank=True)
    voting_description = models.TextField(blank=True)
    voting_date = models.DateField(blank=True, null=True)
    voting_result = models.TextField(blank=True)
    propositon_voted = models.ForeignKey(Proposicao, null=True)

    def Votos(self):
        #Returns the votes vote (depends on database)
        return self.voto_set.all()

    def por_partido(self):
        """Returns aggregate vote by party.

         Return: a dictionary whose key is the name of the party (string)
         and the value is a VotoPartido"""

        dictionary_party_votes = {}
        for voto in self.Votos():
            # TODO poderia ser mais complexo:
                # checar se a data da votação bate com
                # o período da legislatura mais recente
            part = voto.legislatura.party.nome
            if part not in dictionary_party_votes:
                dictionary_party_votes[part] = VotoPartido(part)
            voto_partido = dictionary_party_votes[part]
            voto_partido.add(voto.vote_option)
        return dictionary_party_votes

    @staticmethod
    def por_casa_legislativa(lesgilative_house,
                             data_inicial=None,
                             data_final=None):
        votings_by_legislative_house = Votacao.objects.filter(
            proposicao__casa_legislativa=lesgilative_house)
        from django.utils.dateparse import parse_datetime
        if data_inicial is not None:
            inicial_voting_date = parse_datetime('%s 0:0:0' % data_inicial)
            votings_by_legislative_house = votings_by_legislative_house.filter(data__gte=inicial_voting_date)
        if data_final is not None:
            final_voting_date = parse_datetime('%s 0:0:0' % data_final)
            votings_by_legislative_house = votings_by_legislative_house.filter(data__lte=final_voting_date)
        return votings_by_legislative_house

    # TODO def por_uf(self):

    def __unicode__(self):
        if self.voting_date:
            return "[%s] %s" % (self.voting_date, self.voting_description)
        else:
            return self.voting_description


class Voto(models.Model):
    """A vote given in a parliamentary vote.

     attributes:
         legislature - type object Legislature
         option - which was the vote of the parliamentary
                 (yes, no, abstain, obstruction, did not vote)"""

    voting = models.ForeignKey(Votacao)
    legislature = models.ForeignKey(Legislatura)
    vote_option = models.CharField(max_length=10, choices=OPCOES)

    def __unicode__(self):
        return "%s votou %s" % (self.legislature, self.vote_option)


class VotosAgregados:
    """A set of votes.

     attributes:
         yes, no, abstention -
             integers representing the number of votes in the set

     method:
         add
         Total
         voto_medio"""

    def __init__(self):
        self.yes_number = 0
        self.no_number = 0
        self.abstention_number = 0

    def add(self, voto):
        """Adds a set of votes to vote.

         arguments:
             vote - string \ in {YES, NO, ABSTAIN, AWAY, OBSTRUCTION}
             OBSTRUCTION counts as a vote abstention
             MISSING does not count as a vote"""

        if (voto == SIM):
            self.yes_number += 1
        if (voto == NAO):
            self.no_number += 1
        if (voto == ABSTENCAO):
            self.abstention_number += 1
        if (voto == OBSTRUCAO):
            self.abstention_number += 1

    def total_votes(self):
        return self.yes_number + self.no_number + self.abstention_number

    def voto_medio(self):
        """Real value representing the 'average opnion' of
             aggregate votes; 1 is yes and no is -1."""

        total_votes = self.total_votes()
        if total_votes > 0:
            return 1.0 * (self.yes_number - self.no_number) / self.total_votes()
        else:
            return 0

    def __unicode__(self):
        return '(%s, %s, %s)' % (self.yes_number, self.no_number, self.abstention_number)

    def __str__(self):
        return unicode(self).encode('utf-8')


class VotoPartido(VotosAgregados):
    """A set of votes a party.

     attributes:
         party - object of type Party
         yes, no, abstention -
             integers representing the number of votes in the set"""

    def __init__(self, party):
        VotosAgregados.__init__(self)
        self.party = party

# TODO class VotoUF(VotosAgregados):
