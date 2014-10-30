# !/usr/bin/python
# coding=utf8

# Copyright (C) 2013, Arthur Del Esposte, David Carlos de Araujo Silva,
# Luciano Endo, Diego Rabatone
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

from modelagem import models
from xml.etree.ElementTree import Element, ElementTree
import sys
import os

MODULE_DIR = os.path.abspath(os.path.dirname(__file__))


def serialize_casa_legislativa(short_name):

    # Identifying house:
    legislative_house = models.CasaLegislativa.objects.filter(nome_curto=short_name)
    without_legislative_houses = 0
    if len(legislative_house) <= without_legislative_houses:
        raise ValueError('Casa Legislativa não encontrada\n')

    reload(sys)
    sys.setdefaultencoding("utf-8")

    print "\nExportando dados de %s\n" % legislative_house[0].nome

    root = Element('CasaLegislativa',
                   nome = legislative_house[0].nome,
                   nome_curto = legislative_house[0].nome_curto,
                   esfera=legislative_house[0].esfera,
                   local = legislative_house[0].local,
                   atualizacao = str(legislative_house[0].atualizacao))

    # Identifying propositions:
    proposition = models.Proposicao.objects.filter(
        casa_legislativa_id__nome_curto = short_name)

    for proposition_aux in proposition:

        id_proposition = str(proposition_aux.id_prop);
        number_proposition = str(proposition_aux.numero);

        print "Exportando todas as votações e votos da Proposicao com id: "
        print id_proposition + ", numero: " + number_proposition
        proposition_xml = Element(
            'Proposicao',
            id_prop = str(proposition_aux.id_prop),
            sigla=proposition_aux.sigla,
            numero = str(proposition_aux.numero),
            ano = str(proposition_aux.ano),
            ementa = proposition_aux.ementa,
            descricao = proposition_aux.descricao,
            indexacao = str(proposition_aux.indexacao),
            data_apresentacao = str(proposition_aux.data_apresentacao),
            situacao=proposition_aux.situacao)

        voting = models.Votacao.objects.filter(
            proposicao_id=proposition_aux)

        for vote_aux in voting:
            voting_xml = Element('Votacao',
                id_vot=str(vote_aux.id_vot),
                descricao = vote_aux.descricao,
                data = str(vote_aux.data),
                resultado = vote_aux.resultado)

            # Vote:
            votes = models.Voto.objects.filter(votacao_id=vote_aux)
            for vote in votes:

                legislature = vote.legislatura
                parliamentary = legislature.parlamentar
                party = legislature.partido

                vote_xml = Element(
                    'Voto', nome = parliamentary.nome, id_parlamentar = str(
                        parliamentary.id_parlamentar), genero = parliamentary.genero,
                    partido = party.nome, inicio = str(legislature.inicio),
                    fim = str(legislature.fim), numero = str(party.numero),
                    opcao = vote.opcao)

                voting_xml.append(vote_xml)

            proposition_xml.append(voting_xml)

        root.append(proposition_xml)

    filepath = os.path.join(MODULE_DIR, 'dados/' + short_name + '.xml')
    out = open(filepath, "w")
    ElementTree(root).write(out)
    out.close_tag()

print "Exportação realizada com sucesso"
