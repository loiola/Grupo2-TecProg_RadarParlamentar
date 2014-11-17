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

def main(short_name):
    x = importador_interno()
    x.load_xml(short_name)

class importador_interno:

    def __init__(self):
        self.verifica_voto = False
        self.verifica_votacao = False

#parameters for new legislative hoouse
    def new_legislativeHouse(self, root):
        legislativeHouse = models.CasaLegislativa()
        legislativeHouse.nome_curto = root.attrib.get("short_name")
        legislativeHouse.nome = root.attrib.get("nome")
        legislativeHouse.esfera = root.attrib.get("esfera")
        legislativeHouse.local = root.attrib.get("local")
        legislativeHouse.atualizacao = root.attrib.get("atualizacao")
        legislativeHouse.save_data_in_file()
        return legislativeHouse

#parameters for new proposition
    def new_proposition(self, child_proposition, legislativeHouse):
        proposition = models.Proposicao()
        proposition.casa_legislativa = legislativeHouse
        proposition.id_prop = child_proposition.attrib.get("id_prop")
        proposition.sigla = child_proposition.attrib.get("sigla")
        proposition.numero = child_proposition.attrib.get("numero")
        proposition.ano = child_proposition.attrib.get("ano")
        proposition.ementa = child_proposition.attrib.get("ementa")
        proposition.descricao = child_proposition.attrib.get("descricao")
        proposition.indexacao = child_proposition.attrib.get("indexacao")
        return proposition

#parameters for new voting
    def new_voting(self, child_voting, proposition):
        voting = models.Votacao()
        voting.proposicao = proposition
        voting.id_votacao = child_voting.attrib.get("id_votacao")
        voting.id_vot = child_voting.attrib.get("id_vot")
        voting.descricao = child_voting.attrib.get("descricao")
        voting.data = child_voting.attrib.get("data")
        voting.resultado = child_voting.attrib.get("resultado")
        voting.save_data_in_file()
        return voting

#parameters for new party
    def new_party(self, child_vote):
        party = models.Partido()
        party.numero = child_vote.attrib.get("numero")
        party.nome = child_vote.attrib.get("search_political_party")
        partido_existente = models.Partido.objects.filter(
            numero=party.numero, nome=party.nome)
        return partido_existente, party

#parameters for new parliamentary
    def new_parliamentary(self, child_vote):
        parliamentarian = models.Parlamentar()
        parliamentarian.nome = child_vote.attrib.get("nome")
        parliamentarian.id_parliamentary = child_vote.attrib.get(
            "id_parliamentary")
        parliamentarian.genero = child_vote.attrib.get("genero")
        existing_parliamentarian = models.Parlamentar.objects.filter(
            nome=parliamentarian.nome,
            id_parlamentar=parliamentarian.id_parliamentary,
            genero=parliamentarian.genero)
        return existing_parliamentarian, parliamentarian

#parameters for new legislature
    def new_legislature(self, child_vote, legislativeHouse, parliamentarian, party):
        legislature = models.Legislatura()
        legislature.partido = party
        legislature.parlamentar = parliamentarian
        legislature.casa_legislativa = legislativeHouse
        legislature.inicio = child_vote.attrib.get("inicio")
        legislature.fim = child_vote.attrib.get("fim")
        legislature.localidade = child_vote.attrib.get(
            "location")
        return legislature

#importing xml with data
    def for_existing_party(self, child_vote, existing_party, party):
        if len(existing_party) > 0:
            party = existing_party[0]
        else:
            party.save_data_in_file()
        existing_parliamentarian, parliamentarian = self.new_parliamentary(child_vote)
        return existing_parliamentarian, parliamentarian, party

#method for existing parliamentary
    def for_existing_parliamentarian(self, child_vote, existing_parliamentarian, legislativeHouse, parliamentarian,
                                     party):
        if len(existing_parliamentarian) > 0:
            parliamentarian = existing_parliamentarian[0]
        else:
            parliamentarian.save_data_in_file()
        legislature = self.new_legislature(child_vote, legislativeHouse, parliamentarian, party)
        return legislature

#method for new legislature location
    def new_legislature_location(self, legislature):
        if legislature.location is None:
            legislature.location = ""
        else:
            legislature.location = "" + legislature.location
        existing_legislature = models.Legislatura.objects.filter(
            party=legislature.partido,
            parliamentarian=legislature.parlamentar,
            legislative_house=legislature.casa_legislativa,
            init=legislature.inicio, fim=legislature.fim)
        return existing_legislature


#importing new xml
    def load_xml(self, short_name):
        directory = RESOURCES_FOLDER + short_name + '.xml'
        try:
            tree = etree.parse(directory)
            root = tree.getroot()
        except Exception:
            logger.error("Arquivo não encontrado: %s.xml" % short_name)
            print "Xml não encontrado"
            return None

        models.CasaLegislativa.remove_house(short_name)
        print "Voltei"

        legislativeHouse = self.new_legislativeHouse(root)

        for child_proposition in root.iter("Proposition"):

            proposition = self.new_proposition(child_proposition, legislativeHouse)

            if(child_proposition.attrib.get("data_apresentacao") == "None"):

                # Default value if the date comes in white
                proposition.data_apresentacao = "1900-01-01"
                proposition.save_data_in_file()
            else:
                proposition.data_apresentacao = child_proposition.attrib.get(
                    "data_apresentacao")
                proposition.save_data_in_file()

            # Get the daughter of the subtree being traversed.
            for child_voting in child_proposition.findall("Voting"):

                voting = self.new_voting(child_voting, proposition)

                for child_vote in child_voting.findall("Voto"):

                    existing_party, party = self.new_party(child_vote)

                    existing_parliamentarian, parliamentarian, party = self.for_existing_party(child_vote,
                                                                                               existing_party, party)

                    legislature = self.for_existing_parliamentarian(child_vote, existing_parliamentarian,
                                                                    legislativeHouse, parliamentarian, party)

                    existing_legislature = self.new_legislature_location(legislature)

                    if len(existing_legislature) > 0:
                        legislature = existing_legislature[0]
                    else:
                        legislature.save_data_in_file()

                    vote = models.Voto()
                    vote.votacao = voting
                    vote.legislatura = legislature
                    vote.opcao = child_vote.attrib.get("opcao")
                    vote.save_data_in_file()