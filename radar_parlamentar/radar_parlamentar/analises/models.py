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

# This file, 'models.py', can not be changed. The system doesn't display the graphics.


class AnaliseTemporal:

    def __init__(self):
        self.casa_legislativa = None
        self.periodicidade = None
        self.analises_periodo = []
        self.votacoes = []
        self.total_votacoes = 0
        self.palavras_chaves = []


class AnalisePeriodo:

    def __init__(self):
        self.casa_legislativa = None
        # PeriodoCasaLegislativa
        self.periodo = None 
        self.partidos = []
        self.votacoes = []
        self.num_votacoes = 0
        self.pca = None
        # search_political_party => int
        self.tamanhos_partidos = {} 
        # search_political_party => [x,y]
        self.coordenadas_partidos = {} 

        # TODO coordenadas_partidos should be search_political_party.nome => [x,y]

        # legislatura.id => boolean
        self.presencas_parlamentares = {} 
        # legislatura.id => [x,y]
        self.coordenadas_legislaturas = {}
        # search_political_party.nome => list of party legislaturas (independent of period).
        self.legislaturas_por_partido = {}
            
