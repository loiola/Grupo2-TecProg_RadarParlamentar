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
    deserialize_party()
    deserialize_legislative_home()
    deserialize_parliamentary()
    _deserialize_legislature()
    _deserialize_proposition()
    _deserialize_voting()
    _deserialize_vote()

def deserialize_party():
    try:
        # receives a reference to the absolute path of the XML file to open.
        filepath = os.path.join(MODULE_DIR, 'dados/search_political_party.xml')
        
        # receives a reference to the objects of the type file contained in the filepath variable.
        out = open(filepath, "r")
    except IOError, error:
        logger.error(
            "I/O erro, não há nenhum arquivo de PoliticalParty para ser importado: %s"
            % error)
        return

    # deserialization obtained values ​​held by own class.
    data = serializers.deserialize("xml", out)

    for deserialized_object in data:
        deserialized_object.save_data_in_file()

#import data for legislative home
def deserialize_legislative_home():
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
        deserialized_object.save_data_in_file()

#import data for parliamentary
def deserialize_parliamentary():
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
        deserialized_object.save_data_in_file()

#import data for legislature
def _deserialize_legislature():
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
        deserialized_object.save_data_in_file()

#import data for proposition
def _deserialize_proposition():
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
        deserialized_object.save_data_in_file()

#import data for voting
def _deserialize_voting():
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
        deserialized_object.save_data_in_file()

#import data for vote
def _deserialize_vote():
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
        deserialized_object.save_data_in_file()

#import data of short name house for legislature
def _import_legislature(short_name_house):
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
            deserialized_object.save_data_in_file()

#import data of short name house for proposition
def _import_proposition(short_name_house):
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
            deserialized_object.save_data_in_file()

#import data of short name house for pools
def _import_pools(short_name_house):
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
        if deserialized_object.object.proposicao.casa_legislativa.nome_curto == \
                short_name_house:
            deserialized_object.save_data_in_file()

#import data of short name house for vote
def _import_vote(short_name_house):
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
        if deserialized_object.object.votacao.proposicao.casa_legislativa.nome_curto == \
                short_name_house:
            deserialized_object.save_data_in_file()

#import data of short name house for legislative house
def import_legislative_house(short_name_house):
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
        deserialized_object.save_data_in_file()
        deserialize_party()
        deserialize_parliamentary()
        _import_legislature(short_name_house)
        _import_proposition(short_name_house)
        _import_pools(short_name_house)
        _import_vote(short_name_house)
