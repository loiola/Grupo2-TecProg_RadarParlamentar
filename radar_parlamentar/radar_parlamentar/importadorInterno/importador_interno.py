# !/usr/bin/python
# coding=utf8

# Copyright (C) 2013, Gustavo Corrêia, Arthur Del Esposte,
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

from django.core import serializers
from modelagem import models
import os
import logging
logger = logging.getLogger("radar")

MODULE_DIR = os.getcwd() + '/exportadores/'

"""Methods that deserialize objects for reading."""

def main():
    deserialize_partido()
    deserialize_casa_legislativa()
    deserialize_parlamentar()
    _deserialize_legislatura()
    _deserialize_proposicao()
    _deserialize_votacao()
    _deserialize_voto()

def deserialize_partido():
    try:
        # receives a reference to the absolute path of the XML file to open.
        filepath = os.path.join(MODULE_DIR, 'dados/search_political_party.xml')
        
        # receives a reference to the objects of the type file contained in the filepath variable.
        out = open(filepath, "r")
    except IOError, error:
        logger.error(
            "I/O erro, não há nenhum arquivo de Partido para ser importado: %s"
            % error)
        return

    # deserialization obtained values ​​held by own class.
    data = serializers.deserialize("xml", out)

    for deserialized_object in data:
        deserialized_object.save()

def deserialize_casa_legislativa():
    try:
        filepath = os.path.join(MODULE_DIR, 'dados/casa_legislativa.xml')
        out = open(filepath, "r")
    except IOError, error:
        logger.error(
            "I/O erro, não há nenhum arquivo de CasaLegislativa para ser"
            "importado: %s" % error)
        return

    data = serializers.deserialize("xml", out)

    # receiving variable object to be deserialized from the repeating structure
    for deserialized_object in data:
        deserialized_object.save()

def deserialize_parlamentar():
    try:
        filepath = os.path.join(MODULE_DIR, 'dados/parlamentar.xml')
        out = open(filepath, "r")
    except IOError, error:
        logger.error(
            "I/O erro, não há nenhum arquivo de Parlamentar a ser importado:"
            " %s" % error)
        return

    data = serializers.deserialize("xml", out)

    for deserialized_object in data:
        deserialized_object.save()

def _deserialize_legislatura():
    try:
        filepath = os.path.join(MODULE_DIR, 'dados/legislatura.xml')
        out = open(filepath, "r")
    except IOError, error:
        logger.error(
            "I/O erro, não há nenhum arquivo de Legislatura a ser importado:"
            " %s" % error)
        return

    data = serializers.deserialize("xml", out)

    for deserialized_object in data:
        deserialized_object.save()

def _deserialize_proposicao():
    try:
        filepath = os.path.join(MODULE_DIR, 'dados/proposicao.xml')
        out = open(filepath, "r")
    except IOError, error:
        logger.error(
            "I/O erro, não há nenhum arquivo de Proposição para ser importado:"
            " %s" % error)
        return

    data = serializers.deserialize("xml", out)

    for deserialized_object in data:
        deserialized_object.save()

def _deserialize_votacao():
    try:
        filepath = os.path.join(MODULE_DIR, 'dados/votacao.xml')
        out = open(filepath, "r")
    except IOError, error:
        logger.error(
            "I/O erro, não há nenhum arquivo de Votacação para ser importado:"
            " %s" % error)
        return

    data = serializers.deserialize("xml", out)

    for deserialized_object in data:
        deserialized_object.save()

def _deserialize_voto():
    try:
        filepath = os.path.join(MODULE_DIR, 'dados/voto.xml')
        out = open(filepath, "r")
    except IOError, error:
        logger.error(
            "I/O erro, não há nenhum arquivo de Voto para ser importado: %s"
            % error)
        return

    data = serializers.deserialize("xml", out)

    for deserialized_object in data:
        deserialized_object.save()

def _importa_legislatura(short_name_house):
    try:
        filepath = os.path.join(MODULE_DIR, 'dados/legislatura.xml')
        out = open(filepath, "r")
    except IOError, error:
        logger.error(
            "I/O erro, não há nenhum arquivo de Legislatura a ser importado:"
            " %s" % error)
        return

    data = serializers.deserialize("xml", out)

    for deserialized_object in data:
        if deserialized_object.object.casa_legislativa.nome_curto == short_name_house:
            deserialized_object.save()

def _importa_proposicao(short_name_house):
    try:
        filepath = os.path.join(MODULE_DIR, 'dados/proposicao.xml')
        out = open(filepath, "r")
    except IOError, error:
        logger.error(
            "I/O erro, não há nenhum arquivo de Proposição para ser importado:"
            " %s" % error)
        return

    data = serializers.deserialize("xml", out)

    for deserialized_object in data:
        if deserialized_object.object.casa_legislativa.nome_curto == short_name_house:
            deserialized_object.save()

def _importa_votacao(short_name_house):
    try:
        filepath = os.path.join(MODULE_DIR, 'dados/votacao.xml')
        out = open(filepath, "r")
    except IOError, error:
        logger.error(
            "I/O erro, não há nenhum arquivo de Votacação para ser importado:"
            " %s" % error)
        return

    data = serializers.deserialize("xml", out)

    for deserialized_object in data:
        if deserialized_object.object.proposicao.casa_legislativa.nome_curto == short_name_house:
            deserialized_object.save()

def _importa_voto(short_name_house):
    try:
        filepath = os.path.join(MODULE_DIR, 'dados/voto.xml')
        out = open(filepath, "r")
    except IOError, error:
        logger.error(
            "I/O erro, não há nenhum arquivo de Voto para ser importado: %s"
            % error)
        return

    data = serializers.deserialize("xml", out)

    for deserialized_object in data:
        if deserialized_object.object.votacao.proposicao.casa_legislativa.nome_curto == short_name_house:
            deserialized_object.save()

def importa_casa_legislativa(short_name_house):
    try:
        filepath = os.path.join(MODULE_DIR, 'dados/casa_legislativa.xml')
        out = open(filepath, "r")
    except IOError, error:
        logger.error(
            "I/O erro, não há nenhum arquivo de CasaLegislativa para ser"
            "importado: %s" % error)
        return

    data = serializers.deserialize("xml", out)
    for deserialized_object in data:
        if deserialized_object.object.nome_curto == short_name_house:
            models.CasaLegislativa.remove_house(short_name_house)
        deserialized_object.save()
        deserialize_partido()
        deserialize_parlamentar()
        _importa_legislatura(short_name_house)
        _importa_proposicao(short_name_house)
        _importa_votacao(short_name_house)
        _importa_voto(short_name_house)
