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

from __future__ import unicode_literals
from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from modelagem import models
from modelagem import utils
from grafico import JsonAnaliseGenerator
from analise import AnalisadorTemporal
import datetime
import logging

logger = logging.getLogger("radar")


def party_analysis(request):

    return render_to_response('analises.html', {},
                              context_instance = RequestContext(request))

def analise(request, nome_curto_casa_legislativa):
    """Returns the party list to assemble the chart legends"""

    parties = models.Partido.objects.order_by('numero').all()

    casa_legislativa = get_object_or_404(
        models.CasaLegislativa, nome_curto = nome_curto_casa_legislativa)

    try:
        periodicity = request.GET["periodicidade"]
    except:
        periodicity = models.BIENIO

    try:
        keywords = request.GET["palavras_chave"]
    except:
        keywords = ""

    vote_number = casa_legislativa.get_voting_number()

    return render_to_response(
        'analise.html',
        {'casa_legislativa': casa_legislativa,
         'partidos': parties,
         'num_votacao': vote_number,
         'periodicidade': periodicity,
         'palavras_chave': keywords},
        context_instance = RequestContext(request)
    )


def json_analise(request, nome_curto_casa_legislativa,
                 periodicidade, palavras_chave=""):
    """Returns the JSON with the coordinates of chart PrincipalComponentAnalysis"""

    casa_legislativa = get_object_or_404(
        models.CasaLegislativa, nome_curto = nome_curto_casa_legislativa)

    list_of_keywords = utils.StringUtils.transforms_text_in_string_list(
        palavras_chave)

    analyzer = AnalisadorTemporal(
        casa_legislativa, periodicidade, list_of_keywords)

    time_analyzer = analyzer.get_analise_temporal()

    analysis_generator = JsonAnaliseGenerator(time_analyzer)

    json = analysis_generator.get_json()

    return HttpResponse(json, mimetype = 'application/json')

def lista_de_votacoes_filtradas(request, nome_curto_casa_legislativa,
                periodicidade=models.BIENIO, palavras_chave=""):
    """Returns the filtered voting list"""

    casa_legislativa = get_object_or_404(
        models.CasaLegislativa, nome_curto = nome_curto_casa_legislativa)

    list_of_keywords = utils.StringUtils.transforms_text_in_string_list(
        palavras_chave)

    analyzer = AnalisadorTemporal(casa_legislativa, periodicidade,
        list_of_keywords)

    time_anazyler = analyzer.votacoes_com_filtro()

    return render_to_response(
                'lista_de_votacoes_filtradas.html',
                {'casa_legislativa':casa_legislativa,
                'lista_de_palavras_chave':list_of_keywords,
                'analise_temporal': time_anazyler,
                'periodicidade':periodicidade} 
                )

