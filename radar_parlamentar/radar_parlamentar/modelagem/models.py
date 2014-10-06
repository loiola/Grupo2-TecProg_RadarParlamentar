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


class Indexers(models.Model):
    """Terms used in the indexing of propositions

     attributes:
         termo - string; ex: "woman" or "political party"
         principal - bool; identifying whether a term is the main
                     a line of synonyms, the term being used."""

    # Terms used in the indexing of propositions
    termo = models.CharField(max_length=120)

    # Identifies if a term is the main line of synonyms
    principal = models.BooleanField()

    def __unicode__(self):
        return '%s-%s-%s' % (self.nome, self.numero, self.cor)


class Partido(models.Model):
    """Political party.

     attributes:
         name - string; eg 'EN'
         number - int; ex: '13 '
         color - string; eg #FFFFFF

     Class methods:
         from_name (name): returns object of type Partido
         from_number (number): returns object of type Partido
         get_no_party (): returns a party called 'NO PARTY'"""

    LISTA_PARTIDOS = os.path.join(MODULE_DIR, 'recursos/partidos.txt')

    # Partido name
    nome = models.CharField(max_length=12)

    # Partido number
    numero = models.IntegerField()

    # Partido color
    cor = models.CharField(max_length=7)

    @classmethod
    def from_name(cls, nome):
        """Given a name and return an object of type Partido
             or None if name is invalid"""

        if nome is None:
            return None

        # Search first at database
        # Receives the object filter of party (in from_name method by name; in
        # from_number method, by number)
        party = Partido.objects.filter(nome=nome)

        if party:
            return party[0]
        else:
            # If is not on database, search in hardcoded file
            return cls._from_regex(1, nome.strip())

    @classmethod
    def from_number(cls, numero):
        """Receives a number (int) and returns an object of type Partido
             or None if name is invalid"""

        if numero is None:
            return Nonecor

        # Search first at database
        party = Partido.objects.filter(numero=numero)
        if party:
            return party[0]
        else:
            # If is not on database, search in hardcoded file
            return cls._from_regex(2, str(numero))

    @classmethod
    def get_no_party(cls):
        """Returns a party called 'NO PARTY'"""

        # List that receives the object filter of party where the name is equal SEM_PARTIDO
        no_party_list = Partido.objects.filter(nome=SEM_PARTIDO)

        if not no_party_list:
            partido = Partido()
            partido.nome = SEM_PARTIDO
            partido.numero = 0
            partido.cor = COR_PRETA
            partido.save()
        else:
            partido = no_party_list[0]
        return partido

    @classmethod
    def _from_regex(cls, idx, key):
        PARTIDO_REGEX = '([a-zA-Z]*) *([0-9]{2}) *(#+[0-f]{6})'

        # Receives list of partidos
        party_list = open(cls.LISTA_PARTIDOS)

        for line in party_list:
            res = re.search(PARTIDO_REGEX, line)
            if res and res.group(idx) == key:
                partido = Partido()
                partido.nome = res.group(1)
                partido.numero = int(res.group(2))
                partido.cor = res.group(3)
                partido.save()
                return partido
        return None

    def __unicode__(self):
        return '%s-%s' % (self.nome, self.numero)


class CasaLegislativa(models.Model):
    """IType institution Senate, House etc.

     attributes:
         nome - string; eg 'City Hall of São Paulo'
         nome_curto - string; will be used to generate links.
                         ex 'PBMC' to 'Municipality of São Paulo'
         esfera - string (municipal, state, federal)
         location - string; ex 'Sao Paulo' for CMSP
         atualizacao - date the database was updated by last time with
         this house polls"""

    # Name of the legislative house
    nome = models.CharField(max_length=100)

    # Short name of legislative house used to link generation
    # (eg .: sen to Senate and cmsp for Municipality of São Paulo
    nome_curto = models.CharField(max_length=50, unique=True)

    # Sphere of legislative house (federal, state, municipal)
    esfera = models.CharField(max_length=10, choices=ESFERAS)

    # Local of legislative house (ex .: São Paulo)
    local = models.CharField(max_length=100)

    # Date the database was updated by last time with this house polls
    atualizacao = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return self.nome

    def parties(self):

        #Returns the existing partidos this legislative house
        return Partido.objects.filter(
            legislatura__casa_legislativa=self).distinct()

    def legislatures(self):

        # Returns existing legislative legislaturas this house
        return Legislatura.objects.filter(casa_legislativa=self).distinct()

    def voting_number(self, data_inicial=None, data_final=None):

        # Returns the number of voting on a legislative house
        return Votacao.by_legislative_house(
            self, data_inicial, data_final).count()

    def votes_number(self, data_inicio=None, data_fim=None):

        # Receives votes for legislative house, with start and end date
        votings = Votacao.by_legislative_house(self, data_inicio, data_fim)

        # List votes in a vote by a legislative house
        votes = []

        for votacao in votings:
            votes += votacao.votes()

        # Returns the number of votes in a legislative house
        return len(votes)

    @staticmethod
    def remove_house(nome_casa_curto):
        """Method that deletes certain record of legislative house
        cascade
             arguments:
                 nome_casa - Name of the house to be deleted"""

        try:
            try:
                CasaLegislativa.objects.get(
                    nome_curto=nome_casa_curto).delete()

            except CasaLegislativa.DoesNotExist:
                print 'Casa legislativa ' + nome_casa_curto + ' não existe'
        except:
            print('Possivelmente a operacao extrapolou o limite de '
                  'operacoes do SQLite, tente utilizar o MySQL')


class PeriodoCasaLegislativa(object):
    """attributes:
         ini, end - datetime objects
         string - Description of the period
         quantidade_votacoes - whole"""

    def __init__(self, data_inicio, data_fim, quantidade_votacoes=0):
        # TODO self.casa_legislativa = ...

        # Start date of the vote period
        self.ini = data_inicio

        # End date of the vote period
        self.fim = data_fim

        # Total voting by voting
        self.quantidade_votacoes = quantidade_votacoes

        # Period description
        self.string = ""
        self.string = unicode(self)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        if not self.string:
            self._build_string()
        return self.string

    def _build_string(self):

        # Storing the description of the period
        data_string = ''

        # Stores the time (number of days) for the description of period be built
        delta = self.fim - self.ini

        if delta.days < 35:  # período é de um mês
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
            data_string += str(self.ini.year)
            data_string += " " + str(meses[self.ini.month])
        elif delta.days < 200:  # periodo é de um semestre
            data_string += str(self.ini.year)
            if self.ini.month < 6:
                data_string += " 1o Semestre"
            else:
                data_string += " 2o Semestre"
        elif delta.days < 370:  # periodo é de um ano
            data_string += str(self.ini.year)
        elif delta.days < 750:  # periodo é um biênio
            data_string += str(self.ini.year) + " e "
            data_string += str(self.fim.year)
        elif delta.days < 1500:  # periodo é um quadriênio
            data_string += str(self.ini.year) + " a "
            data_string += str(self.fim.year)
        self.string = data_string


class Parlamentar(models.Model):
    """Um parlamentar.

    Atributos:
        id_parlamentar - string identificadora de acordo a fonte de dados
        nome, genero -- strings"""

    # Parliamentary identifier
    # Obs: id_parlamentar is not a  primary key!
    id_parlamentar = models.CharField(max_length=100, blank=True)

    # Parliamentaru name
    nome = models.CharField(max_length=100)

    # Paliamentary gender
    genero = models.CharField(max_length=10, choices=GENEROS, blank=True)

    def __unicode__(self):
        return self.nome


class Legislatura(models.Model):
    """A continuous period of time in which a policy acts as parliamentarian.
     It's different mandate. A term lasts four years. If the holder leaves
     and alternate takes, then we have an exchange of legislature.

     attributes:
         parlamentar - Parliamentary exercising the legislature;
                         object of type Parliamentary
         casa_legislativa - object type CasaLegislativa
         inicio, fim - dates indicating the period
         partido - object of type Partido
         localidade - string; eg 'SP', 'RJ' if the Senate or
                                     Chamber of Deputies

     methods:
         find - search by date legislature and parliamentary"""

    # Which exerts a parliamentary legislature
    parlamentar = models.ForeignKey(Parlamentar)

    # Legislative house where the parliamentary exerts its legislature
    casa_legislativa = models.ForeignKey(CasaLegislativa, null=True)

    # Start date of the parliamentary legislature
    inicio = models.DateField(null=True)

    # End date of the parliamentary legislatur
    fim = models.DateField(null=True)

    # Partido to which the member belongs
    partido = models.ForeignKey(Partido)

    # Where parliamentary exerts its legislature (eg .: SP, RJ)
    localidade = models.CharField(max_length=100, blank=True)

    @staticmethod
    def find_legislature(data, nome_parlamentar):
        """Search the legislature of a parliamentary by name
             on a certain date
            arguments:
              date - the date object type
              nome_parlamentar - string
            Return: object of type Legislature
            If not, throws exception ValueError"""

        # Temporary variable that stores the filter objects by the Legislature
        # name of the parliamentary
        search_by_parliamentary_name = Legislatura.objects.filter(
            parlamentar__nome=nome_parlamentar)
        for leg in search_by_parliamentary_name:
            if data >= leg.inicio and data <= leg.fim:
                return leg
        raise ValueError('Não achei legislatura para %s em %s' %
                         (nome_parlamentar, data))

    def __unicode__(self):
        return "%s - %s@%s [%s, %s]" % (
            self.parlamentar,
            self.partido,
            self.casa_legislativa.nome_curto,
            self.inicio,
            self.fim)


class Proposicao(models.Model):
    """Parliamentary proposition (bill).

     attributes:
         id_prop - identifier string according to data source
         abbreviation, number, year - strings that form the legal name of
         the proposition
         ementa-- succinct and official description
         Description - more detailed description
         indexing - key words
         authors - list of objects of type Parliamentary
         data_apresentacao - when it was proposed
         situation - as is now
         casa_legislativa - object type CasaLegislativa

     methods:
         name: return "symbol number / year" """

    # Proposition identifier
    # Obs: id_prop is not a primary key!
    id_prop = models.CharField(max_length=100, blank=True)

    # Forms, along with the number and the year, the legal name of the
    # proposition
    sigla = models.CharField(max_length=10)

    # Forms, along with the initials and the year, the legal name of the
    # proposition
    numero = models.CharField(max_length=10)


    # Forms, along with the initials and number, the legal name of the
    # proposition
    ano = models.CharField(max_length=4)

    # Succinct and official description of the proposition
    ementa = models.TextField(blank=True)

    # Detailed description of the proposition
    descricao = models.TextField(blank=True)

    # Keywords of proposition
    indexacao = models.TextField(blank=True)

    # Date on which the statement was made
    data_apresentacao = models.DateField(null=True)

    # Current situation of the proposition (eg Proposition with veto)
    situacao = models.TextField(blank=True)

    # Legislative house where the proposition was made (it's a foreign key)
    casa_legislativa = models.ForeignKey(CasaLegislativa, null=True)

    # Self the main proposition
    autor_principal = models.TextField(blank=True)

    # Other authors of the proposition
    autores = models.ManyToManyField(
        Parlamentar,
        null=True,
        related_name='demais_autores')

    def nome(self):
        return "%s %s/%s" % (self.sigla, self.numero, self.ano)

    def __unicode__(self):
        return "[%s] %s" % (self.nome(), self.ementa)


class Votacao(models.Model):
    """Vote in planário.

     attributes:
         id_vot - identifier string according to data source
         description, results - strings
         date - date of the vote (type date)
         result - string
         proposition - Proposition object of type

     methods:
         vote ()
         por_partido ()"""

    # The vote identifier
    # Obs: id_vot is not a primary key!
    id_vot = models.CharField(max_length=100, blank=True)

    # Description of vote
    descricao = models.TextField(blank=True)

    # Date on which the vote was made
    data = models.DateField(blank=True, null=True)

    # Outcome of the vote
    resultado = models.TextField(blank=True)

    # Proposition that was passed (it is a foreign key)
    proposicao = models.ForeignKey(Proposicao, null=True)

    def votes(self):
        #Returns the votes vote (depends on database)
        return self.voto_set.all()

    def by_party(self):
        """Returns aggregate vote by party.

         Return: a dictionary whose key is the name of the party
         (string)
         and the value is a VotoPartido"""

        # Dictionary where the key is the name of the party and the value are the
        # votes that are added to the party
        dictionary_party_votes = {}

        for voto in self.votes():
            part = voto.legislatura.partido.nome
            if part not in dictionary_party_votes:
                dictionary_party_votes[part] = VotoPartido(part)
            voto_partido = dictionary_party_votes[part]
            voto_partido.add(voto.opcao)
        return dictionary_party_votes

    @staticmethod
    def by_legislative_house(casa_legislativa, data_inicial=None,
                             data_final=None):

        # Stores the filter of objects Voting for legislative house
        votacoes = Votacao.objects.filter(
            proposicao__casa_legislativa=casa_legislativa)

        from django.utils.dateparse import parse_datetime
        if data_inicial is not None:
            ini = parse_datetime('%s 0:0:0' % data_inicial)
            votacoes = votacoes.filter(data__gte=ini)
        if data_final is not None:
            fim = parse_datetime('%s 0:0:0' % data_final)
            votacoes = votacoes.filter(data__lte=fim)
        return votacoes

    def __unicode__(self):
        if self.data:
            return "[%s] %s" % (self.data, self.descricao)
        else:
            return self.descricao


class Voto(models.Model):
    """A vote given in a parliamentary vote.

     attributes:
         legislature - type object Legislature
         option - which was the vote of the parliamentary
                 (yes, no, abstain, obstruction, did not vote)"""

    # Voting object of type (is a foreign key)
    votacao = models.ForeignKey(Votacao)

    # Object of type Legislature (is a foreign key)
    legislatura = models.ForeignKey(Legislatura)

    # Represents a vote of the parliamentary (eg .: yes, no, abstain,
    # obstruction, did not vote)
    opcao = models.CharField(max_length=10, choices=OPCOES)

    def __unicode__(self):
        return "%s votou %s" % (self.legislatura, self.opcao)


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

        # Represents the number of votes to "yes" option
        self.sim = 0

        # Represents the number of votes to "no" option
        self.nao = 0

        # Represents the number of votes to "abstain" option
        self.abstencao = 0

    def add(self, voto):
        """Adds a set of votes to vote.

         arguments:
             vote - string \ in {YES, NO, ABSTAIN, AWAY, OBSTRUCTION}
             OBSTRUCTION counts as a vote abstention
             MISSING does not count as a vote"""

        if (voto == SIM):
            self.sim += 1
        if (voto == NAO):
            self.nao += 1
        if (voto == ABSTENCAO):
            self.abstencao += 1
        if (voto == OBSTRUCAO):
            self.abstencao += 1

    def total_of_votes(self):
        return self.sim + self.nao + self.abstencao

    def medium_vote(self):
        """Real value representing the 'average opnion' of
             aggregate votes; 1 is yes and no is -1."""

        # Total of added votes
        total = self.total_of_votes()
        if total > 0:
            return 1.0 * (self.sim - self.nao) / self.total_of_votes()
        else:
            return 0

    def __unicode__(self):
        return '(%s, %s, %s)' % (self.sim, self.nao, self.abstencao)

    def __str__(self):
        return unicode(self).encode('utf-8')


class VotoPartido(VotosAgregados):
    """A set of votes a party.

     attributes:
         party - object of type Partido
         yes, no, abstention -
             integers representing the number of votes in the set"""

    def __init__(self, partido):
        VotosAgregados.__init__(self)
        self.partido = partido

# TODO class VotoUF(VotosAgregados):
