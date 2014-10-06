# !/usr/bin/python
# coding=utf8

# Copyright (C) 2013, David Carlos de Araujo Silva
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
# along with Radar Parlamentar.  If not, see
# <http://www.gnu.org/licenses/>.from __future__ import unicode_literals
import xml.etree.ElementTree as etree
import os
from modelagem import models

import logging
logger = logging.getLogger("radar")

MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
RESOURCES_FOLDER = os.path.join(MODULE_DIR, '../exportadores/dados/')

class importador_interno:

    def __init__(self):
        self.verifica_voto = False
        self.verifica_votacao = False

    def carrega_xml(self, short_name):
        directory = RESOURCES_FOLDER + short_name + '.xml'
        try:
            tree = etree.parse(directory)
            root = tree.getroot()
        except Exception:
            logger.error("Arquivo não encontrado: %s.xml" % short_name)
            print "Xml não encontrado"
            return None

        models.CasaLegislativa.deleta_casa(short_name)
        print "Voltei"

        legislativeHouse = models.CasaLegislativa()
        legislativeHouse.nome_curto = root.attrib.get("short_name")
        legislativeHouse.nome = root.attrib.get("nome")
        legislativeHouse.esfera = root.attrib.get("esfera")
        legislativeHouse.local = root.attrib.get("local")
        legislativeHouse.atualizacao = root.attrib.get("atualizacao")
        legislativeHouse.save()

        for child_proposition in root.iter("Proposicao"):

            proposition = models.Proposicao()
            proposition.casa_legislativa = legislativeHouse
            proposition.id_prop = child_proposition.attrib.get("id_prop")
            proposition.sigla = child_proposition.attrib.get("sigla")
            proposition.numero = child_proposition.attrib.get("numero")
            proposition.ano = child_proposition.attrib.get("ano")
            proposition.ementa = child_proposition.attrib.get("ementa")
            proposition.descricao = child_proposition.attrib.get("descricao")
            proposition.indexacao = child_proposition.attrib.get("indexacao")

            if(child_proposition.attrib.get("data_apresentacao") == "None"):

                # Default value if the date comes in white
                proposition.data_apresentacao = "1900-01-01"
                proposition.save()
            else:
                proposition.data_apresentacao = child_proposition.attrib.get(
                    "data_apresentacao")
                proposition.save()

            # Get the daughter of the subtree being traversed.
            for child_voting in child_proposition.findall("Votacao"):

                voting = models.Votacao()
                voting.proposicao = proposition
                voting.id_votacao = child_voting.attrib.get("id_votacao")
                voting.id_vot = child_voting.attrib.get("id_vot")
                voting.descricao = child_voting.attrib.get("descricao")
                voting.data = child_voting.attrib.get("data")
                voting.resultado = child_voting.attrib.get("resultado")
                voting.save()

                for child_vote in child_voting.findall("Voto"):

                    party = models.Partido()
                    party.numero = child_vote.attrib.get("numero")
                    party.nome = child_vote.attrib.get("partido")
                    partido_existente = models.Partido.objects.filter(
                        numero=party.numero, nome=party.nome)

                    if len(partido_existente) > 0:
                        party = partido_existente[0]
                    else:
                        party.save()

                    parliamentarian = models.Parlamentar()
                    parliamentarian.nome = child_vote.attrib.get("nome")
                    parliamentarian.id_parlamentar = child_vote.attrib.get(
                        "id_parlamentar")
                    parliamentarian.genero = child_vote.attrib.get("genero")
                    existing_parliamentarian = models.Parlamentar.objects.filter(
                        nome=parliamentarian.nome,
                        id_parlamentar=parliamentarian.id_parlamentar,
                        genero=parliamentarian.genero)

                    if len(existing_parliamentarian) > 0:
                        parliamentarian = existing_parliamentarian[0]
                    else:
                        parliamentarian.save()

                    legislature = models.Legislatura()
                    legislature.partido = party
                    legislature.parlamentar = parliamentarian
                    legislature.casa_legislativa = legislativeHouse
                    legislature.inicio = child_vote.attrib.get("inicio")
                    legislature.fim = child_vote.attrib.get("fim")
                    legislature.localidade = child_vote.attrib.get(
                        "localidade")

                    if legislature.localidade is None:
                        legislature.localidade = ""
                    else:
                        legislature.localidade = "" + legislature.localidade
                    existing_legislature = models.Legislatura.objects.filter(
                        party=legislature.partido,
                        parliamentarian=legislature.parlamentar,
                        legislative_house=legislature.casa_legislativa,
                        init=legislature.inicio, fim=legislature.fim)

                    if len(existing_legislature) > 0:
                        legislature = existing_legislature[0]
                    else:
                        legislature.save()

                    vote = models.Voto()
                    vote.votacao = voting
                    vote.legislatura = legislature
                    vote.opcao = child_vote.attrib.get("opcao")
                    vote.save()


def main(short_name):
    x = importador_interno()
    x.carrega_xml(short_name)
