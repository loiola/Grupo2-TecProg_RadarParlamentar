# -*- coding: utf-8 -*-

# Copyright (C) 2012, Leonardo Leite
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

"""Module partidos - functions for characterization and comparison of partidos

functions:
    vetor_votacoes - calculates the vector of voting for a party
    similarity - calculates the similarity between two partidos
    semelhanca_pca - calculates similarities party generating a two-dimensional
    graph

constants:
    PARTIES: List the names of the partidos."""

import algebralinha
import numpy
import pca

# Constant that gets list of existing partidos
PARTIDOS = ['PT', 'PSDB', 'PV', 'PSOL', 'PCdoB', 'PP', 'PR', 'DEM', 'PMDB', 'PSC', 
	'PTB', 'PDT', 'PSB', 'PPS', 'PRB']

def votings_vector(partido, proposicoes):
    """Calculates the vector of voting for a party
    arguments:
        party - party name (string)
        propositions - propositions containing list of polls

    returns:
        A list representing the vector of party polls."""

    # Receives a list that is the vector of a research party
    vector = []

    # prop: temporary variable loop that generates the list vector
    for prop in proposicoes:

        for votacao in prop.votacoes:

            # Receives the votes by party
            dic = votacao.by_party()

            # Receives list of vote of a particular party
            vote = dic[partido]

            # Receives reseultado calculating the search of votes by party
            vi = (1.0*vote.sim + 0*vote.abstencao -1.0*vote.nao) / (
                vote.sim + vote.nao + vote.abstencao)
            vector.append(vi)
    return vector

def vectors_similarity(vetor1, vetor2):

    # Receives the result of normalizing the vector 1
    nv1 = algebra.normaliza(vetor1)

    # Receives the result of normalizing the vector 2
    nv2 = algebra.normaliza(vetor2)

    return algebra.prod_escalar(nv1, nv2)

def similarity(partido1, partido2, proposicoes):
<<<<<<< HEAD
    """Computes the similarity between two partidos"""
=======

	""" Computes the similarity between two partidos"""

>>>>>>> estilo-e-design

    """The similarity is implemented as the scalar product of vectors normalized polls
    arguments:
        partido1, partido2 - names of partidos (string)
        propositions - propositions containing list of polls

    returns:
        A real value \ in [0,1] representing the similarity between the partidos."""

    v1 = votings_vector(partido1, proposicoes)
    v2 = votings_vector(partido2, proposicoes)

    # Receives similarity between vectors 1 and 2
    sem = vectors_similarity(v1, v2)

    similarity_between_parties = (sem+1)/2.0

    return similarity_between_parties

def similarity_pca(vetores):
    """Calculates similarities party generating a two-dimensional graph
    This is done with the Principal Component Analysis (PCA)
    arguments:
    vectors - a list of lists, where each list is a vector of voting for a party
    returns:
    A list where the ith position represents the two-dimensional coordinate of the party
    whose vector voting was the i-th argument list of vectors."""

    # PCA: lines are samples. Columns are variable 
    # We do: linhas = partidos and colunas = votações
    # Should centralize values.
    # As all values ​​\ in [0,1], we need not to scale.
    #
    # Receive a list of lists of vectors of voting of a party
    matriz =  numpy.array(vetores)

    # Centralization:
    matriz -= matriz.mean(axis=0)

    # Receives centering matrix with PCA
    p = pca.PCA(matriz)

    return p



