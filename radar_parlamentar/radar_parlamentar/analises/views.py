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


def analises(request):
    return render_to_response('analises.html', {}, context_instance=RequestContext(request))


def analise(request, nome_curto_casa_legislativa):
    """Returns the party list to assemble the chart legends"""

    partidos = models.Partido.objects.order_by('numero').all()
    casa_legislativa = get_object_or_404(
        models.CasaLegislativa, nome_curto=nome_curto_casa_legislativa)
    try:
        periodicidade = request.GET["periodicidade"]
    except:
        periodicidade = models.BIENIO
    try:
        palavras_chave = request.GET["palavras_chave"]
    except:
        palavras_chave = ""

    num_votacao = casa_legislativa.voting_number()

    return render_to_response(
        'analise.html',
        {'casa_legislativa': casa_legislativa,
         'partidos': partidos,
         'num_votacao': num_votacao,
         'periodicidade': periodicidade,
         'palavras_chave': palavras_chave},
        context_instance=RequestContext(request)
    )


def json_analise(request, nome_curto_casa_legislativa,
                 periodicidade, palavras_chave=""):
    """Returns the JSON with the coordinates of chart PCA"""

    casa_legislativa = get_object_or_404(
        models.CasaLegislativa, nome_curto=nome_curto_casa_legislativa)
    lista_de_palavras_chave = utils.StringUtils.transforma_texto_em_lista_de_string(
        palavras_chave)
    analisador = AnalisadorTemporal(
        casa_legislativa, periodicidade, lista_de_palavras_chave)
    analise_temporal = analisador.get_analise_temporal()
    gen = JsonAnaliseGenerator(analise_temporal)
    json = gen.get_json()
    return HttpResponse(json, mimetype='application/json')


def lista_de_votacoes_filtradas(request, nome_curto_casa_legislativa,
                periodicidade=models.BIENIO, palavras_chave=""):
    """Returns the filtered voting list"""

    casa_legislativa = get_object_or_404(
        models.CasaLegislativa,nome_curto=nome_curto_casa_legislativa)
    lista_de_palavras_chave = utils.StringUtils.transforma_texto_em_lista_de_string(palavras_chave)
    analisador = AnalisadorTemporal(casa_legislativa, periodicidade, 
        lista_de_palavras_chave)
    analise_temporal = analisador.votacoes_com_filtro()

    return render_to_response(
                'lista_de_votacoes_filtradas.html',
                {'casa_legislativa':casa_legislativa,
                'lista_de_palavras_chave':lista_de_palavras_chave,
                'analise_temporal': analise_temporal,
                'periodicidade':periodicidade} 
                )

