# coding=utf8

# Copyright (C) 2012, Leonardo Leite, Saulo Trento, Diego Rabatone,
# Guilherme Januário
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


"""Analysis module"""

from __future__ import unicode_literals
from math import hypot, atan2, pi
from models import AnalisePeriodo, AnaliseTemporal
from modelagem import models
from modelagem import utils
from analises import filtro
import logging
import numpy
import pca
import copy
# import time # timetrack

logger = logging.getLogger("radar")


class AnalisadorTemporal:

    """The AnalisadorTemporal class has methods to create the objects and make 
    AnalisadorPeriodo analyzes.
    An analysis of a period is a principal component analysis of the votes 
    in a given period, for example in the year 2010 to make an animated graphic, 
    you need to do analysis of two or more consecutive periods eg 2010, 2011 and 
    2012, and properly rotate the results for the partidos globally walk as little
    as possible from one side to the other (see algorithm of rotation).

    Attributes:
        data_inicio and data_fim -- strings in the format 'yyyy-mm-dd'.
        analises_periodo -- list of objects of class AnalisePeriodo 
        palavras_chave -- list of strings to be used in filtering 
        votacoes -- list of objects of type Voting for use in the analysis if not 
        specified, looking for votes in the database according data_inicio, data_fim 
        e palavras_chave."""

    def __init__(self, casa_legislativa, periodicidade,
                 palavras_chave=[], votacoes=[]):
        self.casa_legislativa = casa_legislativa
        retriever = utils.PeriodosRetriever(
            self.casa_legislativa, periodicidade)
        self.periodos = retriever.get_periodos()
        self.ini = self.periodos[0].ini
        self.fim = self.periodos[len(self.periodos) - 1].fim
        self.periodicidade = periodicidade
        self.analises_periodo = []
        self.palavras_chave = palavras_chave
        self.votacoes = []
        self.total_votacoes = 0
        self.json = ""

    def get_analise_temporal(self):
        """Returns instance of AnaliseTemporal"""

        if not self.analises_periodo:
            self._faz_analises()
        analise_temporal = AnaliseTemporal()
        analise_temporal.casa_legislativa = self.casa_legislativa
        analise_temporal.periodicidade = self.periodicidade
        analise_temporal.analises_periodo = self.analises_periodo
        analise_temporal.votacoes = self.votacoes
        analise_temporal.total_votacoes = self.total_votacoes
        analise_temporal.palavras_chaves = self.palavras_chave
        return analise_temporal

    def _faz_analises(self):
        """AnalisadorTemporal class method that creates objects and does 
        AnalisadorPeriodo analyzes"""

        for periodo in self.periodos:
            logger.info("Analisando periodo %s a %s." %
                        (str(periodo.ini), str(periodo.fim)))
            analisadorPeriodo = AnalisadorPeriodo(
                self.casa_legislativa, periodo, self.votacoes, self.palavras_chave)
            if analisadorPeriodo.votacoes:
                logger.info("O periodo possui %d votações." %
                            len(analisadorPeriodo.votacoes))
                analisePeriodo = analisadorPeriodo.analisa()
                self.analises_periodo.append(analisePeriodo)
                self.total_votacoes += len(analisadorPeriodo.votacoes)
            else:
                logger.info("O periodo não possui nenhuma votação.")

        # Rotates / mirrors each analysis based on its previous analysis
        logger.info("Rotacionando...")

        # From the second analysis
        for i in range(1, len(self.analises_periodo)):
            rotacionador = Rotacionador(
                self.analises_periodo[i], self.analises_periodo[i - 1])
            analiseRotacionada = rotacionador.espelha_ou_roda()
            self.analises_periodo[i] = analiseRotacionada
        logger.info("Rotacionado") 

    def votacoes_com_filtro(self):
        votacao_com_filtro = []
        for periodo in self.periodos:
            analisadorPeriodo = AnalisadorPeriodo(self.casa_legislativa, 
                periodo, self.votacoes, self.palavras_chave)
            votacao_com_filtro = analisadorPeriodo._inicializa_votacoes()    
        return votacao_com_filtro

class AnalisadorPeriodo:

    def __init__(self, casa_legislativa, periodo,
                 votacoes=[], palavras_chave=[]):
        """Arguments:
            casa_legislativa -- object of type CasaLegislativa;
            Only polls of this house will be analyzed.
            periodo -- object of type PeriodoCasaLegislativa;
            No period, the analysis is done on all the votes.
            votacoes -- list of objects of type Votacoes for use in the analysis if 
            not specified, looking for votes in the database according data_inicio, 
            data_fim and palavras_chave.
            palavras_chave -- list of strings to be used in the filtration of voting"""

        self.casa_legislativa = casa_legislativa
        self.periodo = periodo
        self.ini = periodo.ini if periodo is not None else None
        self.fim = periodo.fim if periodo is not None else None
        self.partidos = self.casa_legislativa.parties()
        self.legislaturas = self.casa_legislativa.legislatures()
        self.votacoes = votacoes
        self.palavras_chave = palavras_chave
        if not self.votacoes:
            self._inicializa_votacoes()

        self.num_votacoes = len(self.votacoes)
        
        # When the analysis is done, it True
        self.analise_ja_feita = False 

        # In degrees, rotation made ​​possible by self.espelha_ou_roda ()
        self.theta = 0

        # self._inicializa_vetores calculated by ():
        self.vetores_votacao = []
        self.vetores_presencas = []
        self.tamanhos_partidos = {}
        self.coordenadas_partidos = {}

        # Array of partido.nome's, one by por legislature
        self.partido_do_parlamentar = []

        # legislatura.id => {True,False}, being True if was present in
        # period.
        self.presencas_legislaturas = {}

        # partido.nome => list of party legislaturas (independent of period).
        self.legislaturas_por_partido = {}

        self.pca_legislaturas = None
        self.coordenadas_legislaturas = {}

    def _inicializa_votacoes(self):
        """Grab this voting period in the database, filtering by keyword and 
        arrow self.votacoes list"""

        filtro_votacao = filtro.FiltroVotacao(
            self.casa_legislativa, self.periodo, self.palavras_chave)
        self.votacoes = filtro_votacao.filtra_votacoes()
        return self.votacoes

    def analisa(self):
        """Returns instance of AnalisePeriodo"""

        self._calcula_legislaturas_2d()
        self._analisa_partidos()
        analisePeriodo = AnalisePeriodo()
        analisePeriodo.casa_legislativa = self.casa_legislativa
        analisePeriodo.periodo = self.periodo
        analisePeriodo.partidos = self.partidos
        analisePeriodo.votacoes = self.votacoes
        analisePeriodo.num_votacoes = self.num_votacoes
        analisePeriodo.pca = self.pca
        analisePeriodo.tamanhos_partidos = self.tamanhos_partidos
        analisePeriodo.coordenadas_legislaturas = self.coordenadas_legislaturas
        analisePeriodo.coordenadas_partidos = self.coordenadas_partidos
        analisePeriodo.legislaturas_por_partido = self.legislaturas_por_partido
        return analisePeriodo

    def _inicializa_vetores(self):
        matrizesBuilder = MatrizesDeDadosBuilder(
            self.votacoes, self.partidos, self.legislaturas)
        matrizesBuilder.gera_matrizes()
        self.vetores_votacao = matrizesBuilder.matriz_votacoes
        self.vetores_presencas = matrizesBuilder.matriz_presencas
        self.partido_do_parlamentar = matrizesBuilder.partido_do_parlamentar

    def _calcula_legislaturas_2d(self):
        """Returns map with the coordinates of legislaturas in the 2D plane formed by the
        first two principal components.
        
        The map key is the id of the legislature (int) and the value is a list of two positions 
        [x, y]."""

        if not self.analise_ja_feita:
            self.coordenadas_legislaturas = self._pca_legislaturas()
            if self.num_votacoes > 1:
                for partido in self.coordenadas_legislaturas.keys():

                    # If you only have one vote, one only has CP. Playing all zero in the 
                    # second CP
                    self.coordenadas_legislaturas[partido] = (
                        self.coordenadas_legislaturas[partido])[0:2]
            elif self.num_votacoes == 1:
                for partido in self.coordenadas_legislaturas.keys():
                    self.coordenadas_legislaturas[partido] = numpy.array(

                        # Zero votes in the period. The partidos are all the same. All zero
                        [(self.coordenadas_legislaturas[partido])[0], 0.])
            
            else:
                for legislatura in self.coordenadas_legislaturas.keys():
                    self.coordenadas_legislaturas[
                        legislatura] = numpy.array([0., 0.])
        return self.coordenadas_legislaturas

    def _pca_legislaturas(self):
        """Wheel analysis by principal components legislature.

        Returns a dictionary where the keys are the ids of the legislaturas and the value
        of each key is a vector with n dimensions of the pca analysis"""

        if not self.pca_legislaturas:
            if not self.vetores_votacao:
                self._inicializa_vetores()
            ilnn = self._lista_de_indices_de_legislaturas_nao_nulas()
            matriz = self.vetores_votacao

            # Excludes missing legislaturas in all voting period
            matriz = matriz[ilnn, :]

            # Centralyses datas
            matriz = matriz - matriz.mean(axis=0)

            # DO the pca  
            self.pca = pca.PCA(matriz, fraction=1)  
            self._preenche_pca_de_legislaturas_nulas(ilnn)
            logger.info("PCA terminada com sucesso. ini=%s, fim=%s" %
                        (str(self.ini), str(self.fim)))

        # Create dictionary to be returned:
        dicionario = {}
        for legislatura, vetor in zip(self.legislaturas, self.pca.U):
            dicionario[legislatura.id] = vetor
        return dicionario

    def _lista_de_indices_de_legislaturas_nao_nulas(self):
        return self.vetores_presencas.sum(axis=1).nonzero()[0].tolist()

    def _preenche_pca_de_legislaturas_nulas(self, ilnn):
        """Recovers missing legislaturas in the period, giving NaN in all
        dimensions in the space of principal components"""

        # Save result of pca in U2
        U2 = self.pca.U.copy()  
        matriz_de_nans = numpy.zeros(
            (len(self.legislaturas), self.num_votacoes)) * numpy.nan
        self.pca.U = matriz_de_nans
        il = -1
        ilnn2 = -1
        for l in self.legislaturas:
            il += 1

            # If this legislature be or not null
            if il in ilnn:  
                ilnn2 += 1
                cpmaximo = U2.shape[1]

                # Put in this line the values that i saved before in U2
                self.pca.U[il, 0:cpmaximo] = U2[ilnn2, :]

                # Avail to fill presencas_legislaturas
                # (legislatura.id => True / False)
                self.presencas_legislaturas[l.id] = True
            else:
                self.pca.U[il, :] = numpy.zeros(
                    (1, self.num_votacoes)) * numpy.NaN
                self.presencas_legislaturas[l.id] = False

    def _analisa_partidos(self):
        coordenadas_parlamentares = self.pca.U[:, 0:2]
        if coordenadas_parlamentares.shape[1] == 1:
            coordenadas_parlamentares = numpy.append(
                coordenadas_parlamentares, numpy.zeros(
                    [len(coordenadas_parlamentares), 1]), 1)
        analisador_partidos = AnalisadorPartidos(
            coordenadas_parlamentares, self.legislaturas, self.partidos,
            self.vetores_presencas, self.partido_do_parlamentar)
        analisador_partidos.analisa_partidos()
        self.coordenadas_partidos = analisador_partidos.coordenadas_partidos
        self.tamanhos_partidos = analisador_partidos.tamanhos_partidos
        self.legislaturas_por_partido = analisador_partidos.legislaturas_por_partido


class MatrizesDeDadosBuilder:

    def __init__(self, votacoes, partidos, legislaturas):
        self.votacoes = votacoes
        self.partidos = partidos
        self.legislaturas = legislaturas
        self.matriz_votacoes = numpy.zeros(
            (len(self.legislaturas), len(self.votacoes)))
        self.matriz_presencas = numpy.zeros(
            (len(self.legislaturas), len(self.votacoes)))

        # Array of partido.nome's, one by legislature
        self.partido_do_parlamentar = []

        # Key is the name of party, and value is VotoPartido
        self._dic_partido_votos = {}

        # legislatura.id => voto.opcao
        self._dic_legislaturas_votos = {}  

    def gera_matrizes(self):
        """Create two matrixcs:
            matriz_votacoes -- from voting (by legislaturas),
            matriz_presencas -- presences from legislaturas

        The possible values in voting matrix are:
        -1 (no), 0 (abteining/miss) and 1 (yes).
        The possible values in prences matrix are:
        0 (lack) e 1 (present).
        The lines index parliamentaries. The columns index the votings.
        The ordering of the rows follows the order of self.partidos or
        self.legislaturas, and the ordering of the columns follows the
        order of self.votacoes.
        
        Returns matriz_votacoes"""

        # Voting index
        iv = -1  
        for votacao in self.votacoes:
            iv += 1
            self._build_dic_legislaturas_votos(votacao)
            self._preenche_matrizes(votacao, iv)
        return self.matriz_votacoes

    def _build_dic_legislaturas_votos(self, votacao):

        # With the "select_related" we do a query eager
        votos = votacao.voto_set.select_related(
            'opcao', 'legislatura__id').all()
        for voto in votos:
            self._dic_legislaturas_votos[voto.legislatura.id] = voto.opcao

    def _preenche_matrizes(self, votacao, iv):

         # Legislature index
        il = -1 
        for legislatura in self.legislaturas:
            il += 1
            self.partido_do_parlamentar.append(legislatura.partido.nome)
            if legislatura.id in self._dic_legislaturas_votos:
                opcao = self._dic_legislaturas_votos[legislatura.id]
                self.matriz_votacoes[il][iv] = self._opcao_to_double(opcao)
                if (opcao == models.AUSENTE):
                    self.matriz_presencas[il][iv] = 0.
                else:
                    self.matriz_presencas[il][iv] = 1.
            else:
                self.matriz_votacoes[il][iv] = 0.
                self.matriz_presencas[il][iv] = 0.

    def _opcao_to_double(self, opcao):
        if opcao == 'SIM':
            return 1.
        if opcao == 'NAO':
            return -1.
        return 0.


class AnalisadorPartidos:
    """Analyse a party in a period"""

    def __init__(self, coordenadas_parlamentares, legislaturas, partidos,
                 matriz_presencas, partido_do_parlamentar):
        self.coordenadas_parlamentares = coordenadas_parlamentares
        self.legislaturas = legislaturas
        self.partidos = partidos
        self.matriz_presencas = matriz_presencas
        self.partido_do_parlamentar = partido_do_parlamentar
        self.coordenadas_partidos = {}
        self.tamanhos_partidos = {}
        self.legislaturas_por_partido = {}

    def analisa_partidos(self):
        """Generate the following outputs:
            self.coordenadas_partido # partido => [x,y]
            self.tamanhos_partidos # partido => int
            self.legislaturas_por_partido # partido => legislaturas"""

        for ip in range(0, len(self.partidos)):
            indices_deste_partido = []
            for il in range(0, len(self.legislaturas)):
                if self.partido_do_parlamentar[il] == self.partidos[ip].nome:
                    indices_deste_partido.append(il)
            coordenadas_medias = self._media_sem_nans(
                self.coordenadas_parlamentares[indices_deste_partido, :])
            tamanho_partido = len(self.matriz_presencas[
                                  indices_deste_partido, :].sum(
                                  axis=1).nonzero()[0])
            self.tamanhos_partidos[self.partidos[ip]] = tamanho_partido
            self.legislaturas_por_partido[self.partidos[ip].nome] = [
                self.legislaturas[x] for x in indices_deste_partido]
            self.coordenadas_partidos[self.partidos[ip]] = coordenadas_medias

    def _media_sem_nans(self, array_numpy):
        """ Returns average by array numpy columns, desregardin the nans."""
        
        mdat = numpy.ma.masked_array(array_numpy, numpy.isnan(array_numpy))
        mm = numpy.mean(mdat, axis=0)
        return mm.filled(numpy.nan)


class Rotacionador:

    def __init__(self, analisePeriodo, analisePeriodoReferencia):
        self.analisePeriodo = analisePeriodo
        self.analisePeriodoReferencia = analisePeriodoReferencia

    def _energia(self, dados_fixos, dados_meus, por_partido,
                 graus=0, espelho=0):
        """Calculates energy involved in the movement between two instants (fixed and mine), 
        where the mine is rotated (between 0 and 360 degrees), and the first axis multiplied 
        by -1 if the mirror = 1. See pdf entitled "Analytical Solution to the Problem of 
        Rotation Axes Representation of Parties in Parliamentary Radar" 
        (algoritmo_rotacao.pdf)."""

        e = 0
        dados_meus = dados_meus.copy()
        if espelho == 1:
            for partido, coords in dados_meus.items():
                dados_meus[partido] = numpy.dot(
                    coords, numpy.array([[-1., 0.], [0., 1.]]))
        if graus != 0:
            for partido, coords in dados_meus.items():
                dados_meus[partido] = numpy.dot(coords, self._matrot(graus))

        if por_partido:
            for p in dados_meus:
                e += self._zero_if_nan(numpy.dot(dados_fixos[p] - dados_meus[
                    p], dados_fixos[p] - dados_meus[p]) * self.analisePeriodo.tamanhos_partidos[p])
        else:
            for l in dados_meus:
                e += self._zero_if_nan(
                    numpy.dot(dados_fixos[l] - dados_meus[
                        l], dados_fixos[l] - dados_meus[l]))
        return e

    # Radian if deg=0; degree if deg=1
    def _polar(self, x, y, deg=0):		
        """Convert from rectangular (x,y) to polar (r,w)
        r = sqrt(x^2 + y^2)
        w = arctan(y/x) = [-\pi,\pi] = [-180,180]"""

        if deg:
            return hypot(x, y), 180.0 * atan2(y, x) / pi
        else:
            return hypot(x, y), atan2(y, x)

    def _matrot(self, graus):
        """Returns 2x2 rotation that rotates the axes in degrees (0-360) in 
        counterclockwise array (as if the points spun clockwise around fixed axes)."""

        graus = float(graus)
        rad = numpy.pi * graus / 180.
        c = numpy.cos(rad)
        s = numpy.sin(rad)
        return numpy.array([[c, -s], [s, c]])

    def _zero_if_nan(self, x):
        x = x if not numpy.isnan(x) else 0
        return x

    def espelha_ou_roda(self, por_partido=False, so_espelha=True):
        """Returns new AnalisePeriodo cwith rotated coordinates
        if por_partido == True:
        the operation minimizes how much the partidos walked
        if por_partido == False:
        minimizes how much the parliamentarian walked intself
        if so_espelha == True:
        it does not spin, just mirrors the components if necessary"""

        if por_partido:
            dados_meus = self.analisePeriodo.coordenadas_partidos
            dados_fixos = self.analisePeriodoReferencia.coordenadas_partidos
        else:
            dados_meus = self.analisePeriodo.coordenadas_legislaturas
            dados_fixos = self.analisePeriodoReferencia.coordenadas_legislaturas
        epsilon = 0.001

        if not so_espelha:
            print "Calculando teta1 e teta2..."
            numerador = 0
            denominador = 0
            for key, coords in dados_meus.items():
                meu_polar = self._polar(coords[0], coords[1], 0)
                alheio_polar = self._polar(
                    dados_fixos[key][0], dados_fixos[key][1], 0)
                tamanho = self.analisePeriodo.tamanhos_partidos[
                    key] if por_partido else 1
                numerador += self._zero_if_nan(
                    tamanho * meu_polar[0] * alheio_polar[0] * numpy.sin(
                        alheio_polar[1]))
                denominador += self._zero_if_nan(
                    tamanho * meu_polar[0] * alheio_polar[0] * numpy.cos(
                        alheio_polar[1]))
            if denominador < epsilon and denominador > -epsilon:
                teta1 = 90
                teta2 = 270
            else:
                teta1 = numpy.arctan(numerador / denominador) * 180 / 3.141592
                teta2 = teta1 + 180
            print "teta 1 = " + str(teta1) + "; teta2 = " + str(teta2)
        else:
            teta1 = 0
            teta2 = 180

        ex = numpy.array(
            [self._energia(
                dados_fixos, dados_meus, por_partido,
                graus=teta1, espelho=0), self._energia(
             dados_fixos, dados_meus, por_partido,
             graus=teta2, espelho=0),
             self._energia(dados_fixos, dados_meus, por_partido, graus=teta1,
                           espelho=1), self._energia(dados_fixos, dados_meus,
                                                     por_partido, graus=teta2,
                                                     espelho=1)])
        print ex

        dados_partidos = self.analisePeriodo.coordenadas_partidos
        dados_legislaturas = self.analisePeriodo.coordenadas_legislaturas
        ganhou = ex.argmin()
        campeao = [0, 0]

        # Mirror
        if ganhou >= 2:  
            campeao[0] = 1
            for partido, coords in dados_partidos.items():
                dados_partidos[partido] = numpy.dot(
                    coords, numpy.array([[-1., 0.], [0., 1.]]))
            for legislatura, coords in dados_legislaturas.items():
                dados_legislaturas[legislatura] = numpy.dot(
                    coords, numpy.array([[-1., 0.], [0., 1.]]))

        # Spin from teta1
        if ganhou == 0 or ganhou == 2:  
            campeao[1] = teta1
        else:
            campeao[1] = teta2
        for partido, coords in dados_partidos.items():
            dados_partidos[partido] = numpy.dot(
                coords, self._matrot(campeao[1]))
        for legislatura, coords in dados_legislaturas.items():
            dados_legislaturas[legislatura] = numpy.dot(
                coords, self._matrot(campeao[1]))

        self.theta = campeao[1]
        print "campeao = [espelha,theta] = " + str(campeao)

        analiseRotacionada = copy.copy(self.analisePeriodo)
        analiseRotacionada.coordenadas_partidos = dados_partidos
        analiseRotacionada.coordenadas_legislaturas = dados_legislaturas

        return analiseRotacionada
