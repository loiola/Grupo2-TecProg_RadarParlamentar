# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.template import RequestContext
from django.shortcuts import render_to_response

#index => return index.html data

def index(request):
    return render_to_response('index.html', {},
                              context_instance=RequestContext(request))

#origin => return origem.html data

def origin(request):
    return render_to_response('origem.html', {},
                              context_instance=RequestContext(request))

#thegroup => return grupo.html data

def thegroup(request):
    return render_to_response('grupo.html', {},
                              context_instance=RequestContext(request))

#awards => return premiacoes.html data

def awards(request):
    return render_to_response('premiacoes.html', {},
                              context_instance=RequestContext(request))

#ered_in_midia => return radar_na_midia.html data

def ered_in_midia(request):
    return render_to_response('radar_na_midia.html', {},
                              context_instance=RequestContext(request))

#openvote => return votoaberto.html data

def openvote(request):
    return render_to_response('votoaberto.html', {},
                              context_instance=RequestContext(request))

#importers => return importadores.html data

def importers(request):
    return render_to_response('importadores.html', {},
                              context_instance=RequestContext(request))

#alternative_graph => return grafico_alternativo.html data

def alternative_graph(request):
    return render_to_response('grafico_alternativo.html', {},
                              context_instance=RequestContext(request))

#gender => return genero.html data

def gender(request):
    return render_to_response('genero.html', {},
                              context_instance=RequestContext(request))

#cloud_terms_gender => return genero_tagcloud.html data

def cloud_terms_gender(request):
    return render_to_response('genero_tagcloud.html', {},
                              context_instance=RequestContext(request))

#matrix_gender => return genero_matriz.html data

def matrix_gender(request):
    return render_to_response('genero_matriz.html', {},
                              context_instance=RequestContext(request))

#treemap => return genero_treemap.html data

def treemap_gender(request):
    return render_to_response('genero_treemap.html', {},
                              context_instance=RequestContext(request))

#legilature_history_gender => return genero_historia.html data

def legislatures_history_gender(request):
    return render_to_response('genero_historia.html', {},
                              context_instance=RequestContext(request))

#party_profile => return genero_perfil_partido.html data

def party_profile_gender(request):
    return render_to_response('genero_perfil_partido.html', {},
                              context_instance=RequestContext(request))

#party_comparative => return genero_comparativo_partidos.html data

def party_comparative_gender(request):
    return render_to_response('genero_comparativo_partidos.html', {},
                              context_instance=RequestContext(request))

#future_gender => return genero_futuro.html data

def future_gender(request):
    return render_to_response('genero_futuro.html', {},
                              context_instance=RequestContext(request))

#legilative_profile_gender => return perfil_legis.html data

def legislative_profile_gender(request):
    return render_to_response('perfil_legis.html', {},
                              context_instance=RequestContext(request))

#used_data => return dados_utilizados.html data

def used_data(request):
    return render_to_response('dados_utilizados.html', {},
                              context_instance=RequestContext(request))
