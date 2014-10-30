#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2012, Leonardo Leite, Saulo Trento, Diego Rabatone
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Módulo analise -- Set Analysis class, which has methods for various
analysis, including similarity analysis and principal components. each
instance of this class stores the results of the analysis of a subset of data,
defined by a time interval, by type of proposition and consider the
partidos to consider."""

import re
import numpy
import pca
import sys
import sqlite3 as lite
import model
from matplotlib.pyplot import figure, show, scatter,text
from matplotlib.patches import Ellipse
import matplotlib.colors
from radar_parlamentar.py.model_old import inicializar_diclistadeps


class Analise:
    """Each instance custody analysis results in a period of time between
    self.data_inicial and self.data_final, where the partidos are considered
    listed in self.lista_partidos and the propositions of the  listed in self.
    tipos_proposicao.

    Constructor:

    To create a ANLS instance, which corresponds to an analysis by example of the
    first half of 2010, use:

    import analise
    ANLS = analise.Analise('2010-01-01','2010-30-06')

    If it is desired to include only a few types of proposition, using the third
    argument, and if it is desired to include only a few partidos use the room, for
    example:

    ANLS2 = analise.Analise('2010-01-01','2010-30-06',['MPV','PEC'],['PT','PMDB',
    'PSDB','DEM','PSOL'])

    Instead of a list of partidos, the fourth argument can be an integer N to include
    only partidos with N or more deputies. For example, to use all types of
    proposition but only partidos with six or more Members:

    ANLS3 = analise.Analise('2010-01-01','2010-30-06',[],6)

    Attributes:

    Be ANLS an object of type analysis, then ANLS possesses the attributes below,
    where the letters in braces indicate the dimensions of objects (arrays) of
    numpy.array type:
        ANLS.data_inicial : string 'aaaa-mm-dd'
        ANLS.data_final : string 'aaaa-mm-dd'
        ANLS.tipos_proposicao : string list
        TODO: Replace 'lista_partidos' by 'partidos'
        ANLS.lista_partidos : string list with P partidos
        ANLS.partidos : objects list type Parties
        ANLS.lista_votacoes : tuple list (idProp,idVot) with V voting
        ANLS.vetores_votacao [P]x[V]: elemento ij é o voto médio do search_political_party i na votação
            j, entre -1(não) e 1(sim)
        ANLS.quadrivet_vot [P]x[V]: ij element is a tuple of four elements representing
            the number of votes yes, no, abst. and obstr. of party i in voting j
        ANLS.vetores_tamanho [P]x[V]: ij elements is a number of deputies of party i
            present in voting j
        ANLS.vetores_presenca [P]x[V]: ij element is a fraction of deputies of party i
            presentna in voting j (uss a.tamanho_partidos with aproximação for partidos size)
        ANLS.tamanho_partidos [P]: List with total number of deputies, with minimal presence
            of 1 voting in period, of party i
        ANLS.vetores_votacao_uf [E]x[V]: average voting by state. 'E' is a number of UFs
        ANLS.vetores_tamanho_uf [E]x[V]: Deputies present by state by voting
        ANLS.tamanho_uf [E]: Total number of deputies, with minimal presence of 1 voting in
            period, of state i
        ANLS.pca : Object of class pca.PCA
        ANLS.pca_partido : Object of class pca.PCA analyzed by party
        ANLS.pca_uf : Object of class pca.PCA analyzed by UF
        ANLS.semelhancas_escalar [P]x[P] : symmetric matrix of values ​​between 0 and 100
            representing the percentage of similarity between the partidos i and j (calculated
            by scalar product)
        ANLS.semelhancas_convolucao [P]x[P] : symmetric matrix of values ​​between 0 and 100
            representing the similarity between partidos i and j, calculated by the
            convolution method

       Objects of class pca.PCA has among other attributes:
        a.pca.U [P][C] : cHowever vectors containing the vote identified as the main
        components
            (C V = number), not more of the voting
        a.pca.Vt [C][V] : tells how to build major components from
            polls
        a.pca.eigen [C] :eigenvalues​​. To get variance explained by each cp, just
            do eigen[j]/eigen.sum()

    Methods (dynamics):

    Be ANLS one analysis object type, apply the methods:

        TODO: Add 'tamanho_sigla' and 'tamanho_estado' in a single method, passing as
            parameter entity that wants to have the size (party or UF)
        ANLS.tamanho_sigla(siglaPartido) : returns the size of the party by its acronym, ie,
            number of different deputies found during the study period
        ANLS.tamanho_estado(siglaUF) : returns the size of the state by the acronym
        TODO: Add 'partidos_2d' and 'estados_2d' in a single method
        ANLS.partidos_2d(), a.partidos_2d(arquivo) : returns array with the coordinates of
            partidos in the first two principal components, and provided the name of a file
            write them upon the same
        ANLS.estados_2d(), a.estados_2d(arquivo) : analogously to PCA by states
        ANLS.sem(siglaP1,siglaP2,tipo=2) : prints and returns the similarity between
            the two partidos data by acronyms, calculated by the scalar product (type = 1) or
            by the method method convolution (type = 2) (default)
        ANLS.figura(escala=10) : presents a bubble chart of the partidos with the first
            second major component in the x axis and the y-axis proportional to the size of
            the bubble party size"""

    # Constant:
    ufs_list = ['AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB',
                 'PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO']
    db = 'resultados/camara.db'

    def __init__(self,inicial_date='2011-01-01',final_date='2011-12-31',propositions_type=[],
                 list_political_parties=[],political_parties=[]):
        """ Constructor objects of type analysis, asks as arguments:
        *The start and end dates between which should be considered votes;
        *A list of strings with the types of proposition analyze, leave empty to consider
        all types;
        *A list of strings with the partidos to include in the analysis (leave blank to include all
        partidos), or an integer N to use partidos that have N or more Members in the period
        Size analyzes of partidos and UFs, principal component analysis (PCA) are made
        by party and by state, and percentage similarity analysis by two methods."""

        self.inicial_date = inicial_date
        self.final_date = final_date
        self.propositions_type = propositions_type
        self.list_political_parties = list_political_parties
        self.political_parties = political_parties
        self.number_of_votings = 0
        self.list_of_votings = []
        self.vectors_voting = []
        self.quadrivet_vot = []
        self.vectors_size = []
        self.vectors_presence = []
        self.political_parties_size = []
        self.vectors_votings_uf = []
        self.vectors_size_uf = []
        self.size_uf = []
        self.principal_components_analysis_political_party = None
        self.principal_components_analysis_uf = None
        self.similarities_scalar = []
        self.similarities_convolution = []

        # Check if dates were entered correctly:
        if not (re.match('(19)|(20)\d\d-[01]\d-[0123]\d',inicial_date) and re.match(
                '(19)|(20)\d\d-[01]\d-[0123]\d',final_date)):
            raise StandardError('Datas devem estar no formato "aaaa-mm-dd", mês e dia obrigatoriamente '
                                'com dois dígitos.')

        # If the list 'tipos_proposicao' is empty, use all kinds of proposition:
        if not self.propositions_type:
            connection = lite.connect(Analise.db)
            list_of_types = connection.execute('SELECT distinct tipo FROM PROPOSICOES')
            for tipo in list_of_types:
                self.propositions_type.append(tipo[0])
            connection.close_tag()

        # If the list is empty, use all political partidos:
        if not self.list_political_parties:
            fill_parties = 0
            if not self.political_parties:
                fill_parties = 1
            connection = lite.connect(Analise.db)
            list_of_types = connection.execute('SELECT * FROM PARTIDOS')
            improvisation_list = ['PT', 'PSDB', 'PV', 'PSOL', 'PCdoB', 'PP', 'PR', 'DEM', 'PMDB',
                               'PSC', 'PTB', 'PDT', 'PSB', 'PPS', 'PRB']
            for item in list_of_types:
                if item[1] in improvisation_list:
                    self.list_political_parties.append(item[1])
                    if fill_parties:
                        party = model.Partido(item[1],item[0])
                        self.political_parties.append(party)
            connection.close_tag()

        # If integer, use greater than or equal to this whole political parties:
        elif isinstance(self.list_political_parties,int):
            N = self.list_political_parties
            self.list_political_parties = list_expressive_political_parties(N,self.inicial_date,self.final_date,
                                                       self.propositions_type)

    # Print key information class 'analise'. Used to give 'print' of object 'ANA':
    def __str__(self):
        feedback = ''
        feedback = feedback + 'Data inicial da análise : ' + self.inicial_date + '\n'
        feedback = feedback + 'Data final da análise: ' + self.final_date + '\n'
        feedback = feedback + 'Total de Votações analisadas: ' + str(self.number_of_votings) + '\n'
        feedback = feedback + 'Tipos de matérias analisadas: ' + '\n'
        for tipo in self.propositions_type:
            feedback = feedback + '    ' + tipo + '\n'
        feedback = feedback + 'Partidos analisados: ' + '\n'
        for partido in self.political_parties:
            feedback = feedback + '    ' + partido.nome + '\n'
        return feedback

    def search_votings(self):
        """Paste polls BD (sqlite) to a list (python), and returns."""

        filter_types='('
        for type in self.propositions_type:
            filter_types = filter_types + "'" + type + "',"
        filter_types = filter_types[0:len(filter_types)-1] + ")"
        connection = lite.connect(Analise.db)
        votings = connection.execute('SELECT votacoes.idProp,idVot,data,sim,nao,abstencao,obstrucao '
                               'FROM VOTACOES,PROPOSICOES WHERE votacoes.idProp=proposicoes.idProp '
                               'AND date(data)>date(?) AND date(data)<date(?) AND proposicoes.tipo IN %s'
                               % filter_types,(self.inicial_date,self.final_date)).fetchall()
        self.number_of_votings = len(votings)
        for i in range(len(votings)):
            self.list_of_votings.append(votings[:][i][0:2])
        return votings

    def get_total_votes(self):

        total_number = 0

        for e in range(3,6):
            total_number = total_number + numpy.where(
                (numpy.array(eval(vote[e]))/100000)==political_party_id[party])[0].size      

        return total_number


    def get_list_of_duputies_presents(self):

        list_of_present_deputies = []

        for e in range(3,6):        
            list_of_present_deputies = list_of_present_deputies + list(numpy.array(eval(vote[e]))[numpy.where(
                    numpy.array(eval(vote[e]))/100000==political_party_id[party])])
        return list_of_present_deputies


    def inicialize_vectors(self):
        """Creates the 'vectors' and 'Four-Vectors' aggregate voting party. for leverages
        calculate the size of the partidos, presence of Members, etc.
        The 'vector' uses a number between -1 (no) and 1 (yes) to represent the global
        position of vote in each party, being in itself a vector of dimension N formed
        by the N votes.
        The 'quadrivetor' uses a tuple of four integers to represent the party's position
        on each vote, the integers are the number of MPs who voted yes, no, and
        abstention obstruction. The quadrivetor itself is a vector of these N tuples."""

        # Pick up votes in the database:
        votings = self.search_votings()

        # Create dictionary with id of political partidos:
        connection = lite.connect(Analise.db)
        table_parties = connection.execute('select numero,nome from partidos').fetchall()
        political_party_id = {}
        for table in table_parties:
            political_party_id[table[1]] = table[0]

        self.vectors_voting = numpy.zeros((len(self.list_political_parties),
                                           self.number_of_votings))
        self.quadrivet_vot = numpy.empty((len(self.list_political_parties),
                                          self.number_of_votings),dtype=object)
        self.vectors_size = numpy.zeros((len(self.list_political_parties),
                                         self.number_of_votings))
        self.vectors_presence = numpy.zeros((len(self.list_political_parties),
                                             self.number_of_votings))
        self.political_parties_size = [0]*len(self.list_political_parties)
        party_index =-1

        for party in self.list_political_parties:
            party_index += 1

            # Number of different members of a political party that appeared in at least one vote
            # in the period.
            deputies_number = set()
            vote_index =-1

            for vote in votings:
                vote_index += 1

                total_number = self.get_total_votes()             

                self.quadrivet_vot[party_index][vote_index] = (
                    number_of_yes,number_of_no,number_of_abstain,number_of_obstruction)
                if total_number != 0:
                    self.vectors_voting[party_index][vote_index] = (float(
                        number_of_yes) - float(number_of_no)) / float(total_number)
                else:
                    self.vectors_voting[party_index][vote_index] = 0

                # Tell deputies present:
                list_of_present_deputies = self.get_list_of_duputies_presents()

                self.vectors_size[party_index][vote_index] = numpy.size(list_of_present_deputies)
                for deputy in list_of_present_deputies[0]:

                    # Not enter repeated twice on set, allowing calculate tamanho_partidos:
                    deputies_number.add(deputy)

            self.political_parties_size[party_index] = len(deputies_number)

            # Figure out:
            ivv = -1
            for vote in votings:
                ivv += 1
                self.vectors_presence[party_index][ivv] = self.vectors_size[party_index][ivv]/\
                                                          self.political_parties_size[party_index]
        return


    def political_party_pca(self):
        """Run analysis of main components for political parties.
        Stores the result in self.pca
        Returns a dictionary where the keys are the symbols of political political parties
        and the value of each key is a vector with 'n' dimensions of the pca analysis"""

        if not bool(self.principal_components_analysis_political_party):
            if self.vectors_voting==[]:
                self.inicialize_vectors()
            matrix = self.vectors_voting - self.vectors_voting.mean(axis=0)
            self.principal_components_analysis_political_party = pca.PCA(matrix)
        dictionary = {}
        for party, vector in zip(self.political_parties, self.principal_components_analysis_political_party.U):
            dictionary[party.nome] = vector
        return dictionary


    def get_total_votes_uf(self):

        total_number = 0

        for e in range(3,6):
            total_number = total_number + numpy.where(
                ((numpy.array(eval(v[e]))/1000)%100)==(ie+1))[0].size
         
         return total_number

    def get_list_of_duputies_presents_uf(self):

        list_of_present_deputies = []

        for e in range(3,6):
            list_of_present_deputies = list_of_present_deputies + list(numpy.array(eval(v[e]))[numpy.where((numpy.array(
                        eval(v[e]))/1000)%100==(ie+1))])
        return list_of_present_deputies

    def inicialize_vectors_uf(self):
        """Analogous to 'inicialize_vectors'(self), but aggregated by states and not by political parties."""

        # Pick up votes in the database:
        votings = self.search_votings()

        self.vectors_votings_uf = numpy.zeros((len(Analise.ufs_list),self.number_of_votings))
        self.vectors_size_uf = numpy.zeros((len(Analise.ufs_list),self.number_of_votings))
        self.size_uf = [0]*len(Analise.ufs_list)
        ie =-1
        for e in Analise.ufs_list:

            ie += 1

            # Number of different members of a state that appeared in at least one vote in the
            # period:
            number_of_deputies_uf = set()
            iv =-1

            for v in votings:
                iv += 1

                total_number = self.get_total_votes_uf()

                if total_number != 0:
                    self.vectors_votings_uf[ie][iv] = (float(
                        number_of_yes) - float(number_of_no)) / float(total_number)
                else:
                    self.vectors_votings_uf[ie][iv] = 0

                # Tell deputies present::
                list_of_present_deputies_uf = self.get_list_of_duputies_presents_uf()

                self.vectors_size_uf[ie][iv] = numpy.size(list_of_present_deputies_uf)
                for deputy in list_of_present_deputies_uf[0]:

                    # Not enter repeated twice on set, allowing calculate tamanho_partidos:
                    number_of_deputies_uf.add(deputy)

            self.size_uf[ie] = len(number_of_deputies_uf)
        return

    def pca_uf(self):
        """Run the principal components analysis by UF.
        Stores the result in self.pca
        Returns a dictionary where the keys are the symbols of political parties
        and the value of each key is a vector with n dimensions of the pca analysis."""

        if not bool(self.principal_components_analysis_uf):
            if self.vectors_votings_uf==[]:
                self.inicialize_vectors_uf()
            matrix = self.vectors_votings_uf - self.vectors_votings_uf.mean(axis=0)
            self.principal_components_analysis_uf = pca.PCA(matrix)
        dictionary = {}
        for uf, vector in zip(self.ufs_list, self.principal_components_analysis_uf.U):
            dictionary[uf]=vector
        return dictionary

    def calculate_similarities(self):
        """Calculates similarities between all political parties of the analysis, two by two, according to the
         scalar product and the method of convolution, normalized between 0 and 100 [%].
         The result is stored in self.semelhancas attributes (scalar product) and
         self.semelhancas2 (convolution)."""

        if self.vectors_voting==[]:
            self.inicialize_vectors()
        self.similarities_scalar = numpy.zeros((len(self.list_political_parties),len(self.list_political_parties)))
        self.similarities_convolution = numpy.zeros((len(self.list_political_parties),len(self.list_political_parties)))

        for i in range(0,len(self.list_political_parties)):
            for j in range(0,len(self.list_political_parties)):

                percentage_conversion_factor = 100

                # Method 1:
                self.similarities_scalar[i][j] = percentage_conversion_factor *( ( numpy.dot(self.vectors_voting[i],
                                                                    self.vectors_voting[j]) /
                                                          (numpy.sqrt(numpy.dot(
                                                              self.vectors_voting[i],
                                                              self.vectors_voting[i])) *
                                                           numpy.sqrt(numpy.dot(
                                                               self.vectors_voting[j],
                                                               self.vectors_voting[j])))) + 1)/2

                # Method 2:
                x = 0
                for k in range(self.number_of_votings) :
                    x += Analise.do_convolution(self.quadrivet_vot[i][k],self.quadrivet_vot[j][k])
                x = percentage_conversion_factor * x / self.number_of_votings
                self.similarities_convolution[i][j] = x
        return

    @staticmethod
    def do_convolution(quantity_per_type_vote, tuple_of_types_vote):
        """Receives two integers 'u' and 'v' 4 tuples, representing the votes of two
        political parties in a vote. For example if u = (4,3,0,3) there were 4 yes, 3 no, 0
        and 3 abstentions obstructions party vote.
        Each tuple is normalized by dividing by the sum of the squares of the elements, and
        the function returns the dot product of two normalized tuples."""

        if sum(quantity_per_type_vote)==0 or sum(tuple_of_types_vote)==0:
            return numpy.NaN
        un= numpy.array(quantity_per_type_vote,dtype=float)
        vn= numpy.array(tuple_of_types_vote,dtype=float)
        x = numpy.dot(un,vn)

        # Normalize:
        x = x / ( numpy.sqrt(numpy.dot(un,un)) * numpy.sqrt(numpy.dot(vn,vn)) )
        return x


    def check_acronym_size(self,acronym_party):
        """Return the size of political party giver your acronym."""

        if self.political_parties_size==0:
            self.inicialize_vectors()
        try:
            return self.political_parties_size[self.list_political_parties.index(acronym_party)]
        except ValueError:
            print "WARNING: Partido %s não presente na análise. Dados da análise:\n%s" % \
                  (acronym_party,self)
            return 0

    def check_state_size(self,acronym_country):
        """Returns the size of the state (number of seats) given its acronym."""

        if self.size_uf==[]:
            self.inicialize_vectors_uf()
        try:
            return self.size_uf[Analise.ufs_list.index(acronym_country.upper())]
        except ValueError:
            raise ValueError('Estado "%s" inválido.'%acronym_country)

    def do_coordinates_2d_of_political_parties(self,file=''):
        """Returns array with the coordinates of the political parties in the 2d plane formed by the two
        first principal components.

        If passed as argument the name (not empty) of a file, the result of PCA
        is written to this file, otherwise it is written to stdout."""

        coordinates = self.political_party_pca()
        for party in coordinates.keys():
            coordinates[party] = (coordinates[party])[0:2]
        close = False
        if file:
            fo = open(file,'w')
            close = True
        else:
            fo = sys.stdout
        ip = -1
        fo.write('Análise PCA - por search_political_party\n')
        fo.write('de %s a %s (ano-mês-dia)\n\n' % (self.inicial_date,self.final_date))
        fo.write('Fração da variância explicada pelas dimensões:\n')
        fo.write('%f\n' % (self.principal_components_analysis_political_party.eigen[0]/
                           self.principal_components_analysis_political_party.eigen.sum()))
        fo.write('%f\n' % (self.principal_components_analysis_political_party.eigen[1]/
                           self.principal_components_analysis_political_party.eigen.sum()))
        fo.write('%f\n' % (self.principal_components_analysis_political_party.eigen[2]/
                           self.principal_components_analysis_political_party.eigen.sum()))
        fo.write('%f\n' % (self.principal_components_analysis_political_party.eigen[3]/
                           self.principal_components_analysis_political_party.eigen.sum()))
        fo.write('\nCoordenadas:\n')

        for party in coordinates.keys():
            fo.write('%s: [%f, %f]\n' % (party,coordinates[party][0],coordinates[party][1]))
        fo.write('Tamanhos=%s\n' % str(self.political_parties_size))
        if close:
            fo.close_tag()
        return coordinates


    def do_coordinates_2d_of_states(self,archive=''):
        """Returns array with the coordinates of the states in the 2d plane formed by the two
        first principal components.

        If passed as argument the name (not empty) of a file, the result of
        pca is written to this file, otherwise it is written to 'stdout'."""

        if not bool(self.principal_components_analysis_uf):
            self.principal_components_analysis_uf()
        coordinates = self.principal_components_analysis_uf.U[:,0:2]
        close = False
        if archive:
            fo = open(archive,'w')
            close = True
        else:
            fo = sys.stdout
        ie = -1
        fo.write('Análise PCA - por estado\n')
        fo.write('de %s a %s (ano-mês-dia)\n\n' % (self.inicial_date,self.final_date))
        fo.write('Fração da variância explicada pelas dimensões:\n')
        fo.write('%f\n' % (self.principal_components_analysis_uf.eigen[0]/self.principal_components_analysis_uf.eigen.sum()))
        fo.write('%f\n' % (self.principal_components_analysis_uf.eigen[1]/self.principal_components_analysis_uf.eigen.sum()))
        fo.write('%f\n' % (self.principal_components_analysis_uf.eigen[2]/self.principal_components_analysis_uf.eigen.sum()))
        fo.write('%f\n' % (self.principal_components_analysis_uf.eigen[3]/self.principal_components_analysis_uf.eigen.sum()))
        fo.write('\nCoordenadas:\n')
        for e in Analise.ufs_list:
            ie += 1
            fo.write('%s: [%f, %f]\n' % (e,coordinates[ie,0],coordinates[ie,1]) )
        fo.write('Tamanhos=%s\n' % str(self.size_uf))
        if close:
            fo.close_tag()
        return coordinates

    def calculate_similarities_between_political_parties(self,acronym_party_1,acronym_party_2,type=2):
        if self.similarities_scalar==[]:
            self.calculate_similarities()
        x = self.similarities_scalar[self.list_political_parties.index(acronym_party_1),
                                     self.list_political_parties.index(acronym_party_2)]
        x2 = self.similarities_convolution[self.list_political_parties.index(acronym_party_1),
                                         self.list_political_parties.index(acronym_party_2)]
        print 'Semelhança entre %s e %s:' % (acronym_party_1,acronym_party_2)
        if type==1:
            print 'Método 1 (p. escalar): %5.1f%% <- valor retornado' % x
            print 'Método 2 (convolução): %5.1f%%' % x2
            return x
        elif type==2:
            print 'Método 1 (p. escalar): %5.1f%%' % x
            print 'Método 2 (convolução): %5.1f%% <- valor retornado' % x2
            return x2


    def plot_bubbles(self, scale=10):
        """Presents a plot of bubbles (using matplotlib) with political parties of size
        'tamanho_min' greater than or equal to the first principal component in the 'x-axis'
        second 'y-axis'."""

        data = self.do_coordinates_2d_of_political_parties()

        fig = figure(1)
        fig.clf()

        political_parties_colors = {'PT'   :'#FF0000',
                      'PSOL' :'#FFFF00',
                      'PV'   :'#00CC00',
                      'DEM'  :'#002664',
                      'PSDB' :'#0059AB',
                      'PSD'  :'#80c341',
                      'PMDB' :'#CC0000',
                      'PR'   :'#110274',
                      'PSC'  :'#25b84a',
                      'PSB'  :'#ff8d00',
                      'PP'   :'#203487',
                      'PCdoB':'#da251c',
                      'PTB'  :'#1f1a17',
                      'PPS'  :'#fea801',
                      'PDT'  :'#6c85b1',
                      'PRB'  :'#67a91e'}

        list_political_parties_colors = []
        for party in self.political_parties:
            if party.nome in political_parties_colors:
                list_political_parties_colors.append(political_parties_colors[party.nome])
            else:
                list_political_parties_colors.append((1,1,1))

        political_parties_colormap = matplotlib.colors.ListedColormap(list_political_parties_colors,
                                                             name='partidos')

        ax = fig.add_subplot(111, autoscale_on=True)
        x = []
        y = []
        for party in self.political_parties:
            x.append(data[party.nome][0])
            y.append(data[party.nome][1])
        size = numpy.array(self.political_parties_size) * scale
        scatter(x, y, size, range(len(x)), marker='o', cmap=political_parties_colormap)
        for party in self.political_parties:
            text(data[party.nome][0]+.005,data[party.nome][1],party.numero,
                 fontsize=12,stretch=100,alpha=1)

        show()


def list_expressive_political_parties (N=1,data_inicial='2011-01-01',data_final='2011-12-31',tipos_proposicao=[]):
    """Returns a list of political parties with at least 'N' different deputies who
    polls have come in between 'start_date' and 'end_date'. Consider themselves
    propositions in 'proposition_type', or if all 'proposition_type = []'."""

    # Create dictionary with id of political parties:
    connection = lite.connect(Analise.db)
    political_parties_table = connection.execute('select numero,nome from partidos').fetchall()
    political_party_id = {}
    for table in political_parties_table:
        political_party_id[table[1]] = table[0]

    # Create list of all political partidos:
    lists_all_parties = connection.execute('SELECT nome FROM PARTIDOS').fetchall()
    connection.close_tag()

    # Pick up votes in the database:
    analysis = Analise(data_inicial,data_final,tipos_proposicao)
    votings = analysis.search_votings()

    # Initialize variables:
    political_parties_size = [0]*len(lists_all_parties)
    vectors_size = numpy.zeros((len(lists_all_parties),analysis.number_of_votings))

    # Transform list of tuples in list of strings:
    i = 0
    for lp in lists_all_parties:
        lists_all_parties[i] = lp[0]
        i += 1

    # Calculate size of political partidos:
    ip =-1
    for p in lists_all_parties:

        ip += 1

        # Number of different members of a political party that appeared in at least
        # one vote in the period..
        deputies_number = set()
        vote_index =-1

    for vote in votings:
            vote_index += 1

            # Tell deputies present:
            list_of_present_deputies = [list(numpy.array(eval(vote[3]))[numpy.where(
                numpy.array(eval(vote[3]))/100000==political_party_id[p])]) + list(
                numpy.array(eval(vote[4]))[numpy.where(numpy.array(
                    eval(vote[4]))/100000==political_party_id[p])]) + list(
                numpy.array(eval(vote[5]))[numpy.where(numpy.array(eval(vote[5]))
                                                    /100000==political_party_id[p])]) + list(
                numpy.array(eval(vote[6]))[numpy.where(numpy.array(eval(vote[6]))/100000==political_party_id[p])])]

            vectors_size[ip][vote_index] = numpy.size(list_of_present_deputies)
            for deputy in list_of_present_deputies[0]:

        # Not enter repeated twice on set, allowing calculate tamanho_partidos:
                deputies_number.add(deputy)
        political_parties_size[ip] = len(deputies_number)

    # Make list of major political partidos than N:
    expressives = []
    ip = -1
    for p in lists_all_parties:
        ip += 1
        if political_parties_size[ip] >= N:
            expressives.append(p)
    return expressives

if __name__ == "__main__":
    Analise().plot_bubbles()
