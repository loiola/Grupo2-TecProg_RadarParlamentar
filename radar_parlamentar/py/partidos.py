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

"""Module parties - functions for characterization and comparison of parties

functions:
vetor_votacoes - calculates the vector of voting for a party
similarity - calculates the similarity between two parties
semelhanca_pca - calculates similarities party generating a two-dimensional graph

constants:
PARTIES: List the names of the parties
"""

import algebra
import numpy
import pca

PARTIDOS = ['PT', 'PSDB', 'PV', 'PSOL', 'PCdoB', 'PP', 'PR', 'DEM', 'PMDB', 'PSC', 'PTB', 'PDT', 'PSB', 'PPS', 'PRB']

def vetor_votacoes(partido, proposicoes):
    """Calculates the vector of voting for a party
     arguments:
     party - party name (string)
     propositions - propositions containing list of polls

     returns:
     A list representing the vector of party polls
    """    
    vetor = []
    for prop in proposicoes:
        for votacao in prop.votacoes:
            dic = votacao.por_partido()
            voto = dic[partido]
            #vi = (voto.sim + 0.5*voto.abstencao) / (voto.sim + voto.nao + voto.abstencao) # análise antigo
            vi = (1.0*voto.sim + 0*voto.abstencao -1.0*voto.nao) / (voto.sim + voto.nao + voto.abstencao)
            vetor.append(vi)
    return vetor  

def semelhanca_vetores(vetor1, vetor2):
    nv1 = algebra.normaliza(vetor1)
    nv2 = algebra.normaliza(vetor2)
    return algebra.prod_escalar(nv1, nv2)

def semelhanca(partido1, partido2, proposicoes):
    """Computes the similarity between two parties
     The similarity is implemented as the scalar product of vectors normalized polls
     arguments:
     partido1, partido2 - names of parties (string)
     propositions - propositions containing list of polls

     returns:
     A real value \ in [0,1] representing the similarity between the parties
    """    
    v1 = vetor_votacoes(partido1, proposicoes)
    v2 = vetor_votacoes(partido2, proposicoes)
    sem = semelhanca_vetores(v1, v2)
    return (sem+1)/2.0

def semelhanca_pca(vetores):
    """Calculates similarities party generating a two-dimensional graph
     This is done with the Principal Component Analysis (PCA)
     arguments:
     vectors - a list of lists, where each list is a vector of voting for a party
     returns:
     A list where the ith position represents the two-dimensional coordinate of the party
     whose vector voting was the i-th argument list of vectors
    """
    # PCA: lines are samples. Columns are variable 
    # We do: linhas = partidos and colunas = votações
    # Should centralize values.
    # As all values ​​\ in [0,1], we need not to scale.
    matriz =  numpy.array(vetores)

    # Centralization:
    
    matriz -= matriz.mean(axis=0)  
    p = pca.PCA(matriz)
    return p



