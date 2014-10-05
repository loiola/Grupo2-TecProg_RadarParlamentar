# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.template import RequestContext
from django.shortcuts import render_to_response


def index(request):
    return render_to_response('index.html', {},
                              context_instance=RequestContext(request))


def origem(request):
    return render_to_response('origem.html', {},
                              context_instance=RequestContext(request))


def ogrupo(request):
    return render_to_response('grupo.html', {},
                              context_instance=RequestContext(request))


def awards(request):
    return render_to_response('premiacoes.html', {},
                              context_instance=RequestContext(request))


def radar_na_midia(request):
    return render_to_response('radar_na_midia.html', {},
                              context_instance=RequestContext(request))


def openvote(request):
    return render_to_response('votoaberto.html', {},
                              context_instance=RequestContext(request))


def importers(request):
    return render_to_response('importadores.html', {},
                              context_instance=RequestContext(request))


def alternative_graph(request):
    return render_to_response('grafico_alternativo.html', {},
                              context_instance=RequestContext(request))


def gender(request):
    return render_to_response('genero.html', {},
                              context_instance=RequestContext(request))


def cloud_terms_gender(request):
    return render_to_response('genero_tagcloud.html', {},
                              context_instance=RequestContext(request))


def matrix_gender(request):
    return render_to_response('genero_matriz.html', {},
                              context_instance=RequestContext(request))


def treemap_gender(request):
    return render_to_response('genero_treemap.html', {},
                              context_instance=RequestContext(request))


def legislatures_history_gender(request):
    return render_to_response('genero_historia.html', {},
                              context_instance=RequestContext(request))


def party_profile_gender(request):
    return render_to_response('genero_perfil_partido.html', {},
                              context_instance=RequestContext(request))


def party_comparative_gender(request):
    return render_to_response('genero_comparativo_partidos.html', {},
                              context_instance=RequestContext(request))


def future_gender(request):
    return render_to_response('genero_futuro.html', {},
                              context_instance=RequestContext(request))


def genero_perfil_legis(request):
    return render_to_response('perfil_legis.html', {},
                              context_instance=RequestContext(request))


def used_data(request):
    return render_to_response('dados_utilizados.html', {},
                              context_instance=RequestContext(request))
