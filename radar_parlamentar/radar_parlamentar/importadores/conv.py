# !/usr/bin/python
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

"""Convencao Module (Convenção Nacional Francesa)

Classes:
    ImportadorConvencao generate datas for fictitious legislative house called 
    Convenção Nacional Francesa"""

from __future__ import unicode_literals
from django.utils.dateparse import parse_datetime
from modelagem import models
#last_refresh => date of last refresh on data

LAST_REFRESH = parse_datetime('2012-06-01 0:0:0')

#begin_period => date on begin of period of votation

BEGIN_PERIOD = parse_datetime('1989-01-01 0:0:0')

#end_period => date on end of period of votation

END_PERIOD = parse_datetime('1989-12-30 0:0:0')

#begin_first_semester => date on begin the first semester

BEGIN_FIRST_SEMESTER = parse_datetime('1989-02-02 0:0:0')

#begin_second_semester => date on begin the second semester

BEGIN_SECOND_SEMESTER = parse_datetime('1989-10-10 0:0:0')

PARLAMENTS_PER_PARTY = 3

GIRONDINOS = 'Girondinos'
JACOBINOS = 'Jacobinos'
MONARQUISTAS = 'Monarquistas'


class ImportadorConvencao:

    #new_legislative_hause => get instance the new legislative house

    def _new_legislative_house(self):

        conv = models.CasaLegislativa()
        conv.nome = 'Convenção Nacional Francesa'
        conv.short_name = 'conv'
        conv.esfera = models.FEDERAL
        conv.local = 'Paris (FR)'
        conv.atualizacao = LAST_REFRESH
        conv.save()
        return conv

    # new_party => get instance the new party

    def _new_party(self):

        girondinos = models.Partido()
        girondinos.nome = GIRONDINOS
        girondinos.numero = 27
        girondinos.cor = '#008000'
        girondinos.save()
        jacobinos = models.Partido()
        jacobinos.nome = JACOBINOS
        jacobinos.numero = 42
        jacobinos.cor = '#FF0000'
        jacobinos.save()
        monarquistas = models.Partido()
        monarquistas.nome = MONARQUISTAS
        monarquistas.numero = 79
        monarquistas.cor = '#800080'
        monarquistas.save()
        self.partidos = {girondinos, jacobinos, monarquistas}

    #new_legislature => get instance the new legislature

    def _new_legislature(self):

        # Name partido => list of party legislatures
        self.legs = {}  
        for p in self.partidos:
            self.legs[p.nome] = []
            for i in range(0, PARLAMENTS_PER_PARTY):

                parlamentar = models.Parlamentar()
                parlamentar.id_parlamentar = '%s%s' % (p.nome[0], str(i))
                parlamentar.nome = 'Pierre'
                parlamentar.save()

                leg = models.Legislatura()
                leg.casa_legislativa = self.casa
                leg.inicio = BEGIN_PERIOD
                leg.fim = END_PERIOD
                leg.partido = p
                leg.parlamentar = parlamentar
                leg.save()
                self.legs[p.nome].append(leg)

    #new_proposition => get instance the new proposition

    def _new_proposition(self, num, descricao):

        prop = models.Proposicao()
        prop.id_prop = num
        prop.sigla = 'PL'
        prop.numero = num
        prop.ementa = descricao
        prop.descricao = descricao
        prop.casa_legislativa = self.casa
        prop.save()
        return prop

    #new_votation => get instance the new votation

    def _new_votation(self, num, descricao, data, prop):

        votacao = models.Votacao()
        votacao.id_vot = num
        votacao.descricao = descricao
        votacao.data = data
        votacao.proposicao = prop
        votacao.save()
        return votacao

    #new_vote => get instance the new vote

    def _new_votes(self, votacao, nome_partido, opcoes):

        # opcoes is an options list (YES, NO...)
        for i in range(0, PARLAMENTS_PER_PARTY):
            voto = models.Voto()
            voto.legislatura = self.legs[nome_partido][i]
            voto.opcao = opcoes[i]
            voto.votacao = votacao
            voto.save()

    #new_votation1 => get instance the new votation

    def _new_votation1(self):

        NUM = '1'
        DESCRICAO = 'Reforma agrária'
        prop = self._new_proposition(NUM, DESCRICAO)
        votacao = self._new_votation(
            NUM, DESCRICAO, BEGIN_FIRST_SEMESTER, prop)

        votos_girondinos = [models.SIM, models.ABSTENCAO, models.NAO]
        self._new_votes(votacao, GIRONDINOS, votos_girondinos)

        votos_jacobinos = [models.SIM, models.SIM, models.SIM]
        self._new_votes(votacao, JACOBINOS, votos_jacobinos)

        votos_monarquistas = [models.NAO, models.NAO, models.NAO]
        self._new_votes(votacao, MONARQUISTAS, votos_monarquistas)

    #new_votation2 => get instance the new votation

    def _new_votation2(self):

        NUM = '2'
        DESCRICAO = 'Aumento da pensão dos nobres'
        prop = self._new_proposition(NUM, DESCRICAO)
        votacao = self._new_votation(
            NUM, DESCRICAO, BEGIN_FIRST_SEMESTER, prop)

        votos_girondinos = [models.NAO, models.NAO, models.NAO]
        self._new_votes(votacao, GIRONDINOS, votos_girondinos)

        votos_jacobinos = [models.NAO, models.NAO, models.NAO]
        self._new_votes(votacao, JACOBINOS, votos_jacobinos)

        votos_monarquistas = [models.SIM, models.SIM, models.SIM]
        self._new_votes(votacao, MONARQUISTAS, votos_monarquistas)

    #new_votation3 => get instance the new votation

    def _new_votation3(self):

        NUM = '3'
        DESCRICAO = 'Institui o Dia de Carlos Magno'
        prop = self._new_proposition(NUM, DESCRICAO)
        votacao = self._new_votation(
            NUM, DESCRICAO, BEGIN_FIRST_SEMESTER, prop)

        votos_girondinos = [models.NAO, models.NAO, models.SIM]
        self._new_votes(votacao, GIRONDINOS, votos_girondinos)

        votos_jacobinos = [models.NAO, models.NAO, models.NAO]
        self._new_votes(votacao, JACOBINOS, votos_jacobinos)

        votos_monarquistas = [models.SIM, models.SIM, models.SIM]
        self._new_votes(votacao, MONARQUISTAS, votos_monarquistas)

    #new_votation4 => get instance the new votation

    def _new_votation4(self):

        NUM = '4'
        DESCRICAO = 'Diminuição de impostos sobre a indústria'
        prop = self._new_proposition(NUM, DESCRICAO)
        votacao = self._new_votation(
            NUM, DESCRICAO, BEGIN_FIRST_SEMESTER, prop)

        votos_girondinos = [models.SIM, models.SIM, models.SIM]
        self._new_votes(votacao, GIRONDINOS, votos_girondinos)

        votos_jacobinos = [models.SIM, models.ABSTENCAO, models.NAO]
        self._new_votes(votacao, JACOBINOS, votos_jacobinos)

        votos_monarquistas = [models.SIM, models.NAO, models.AUSENTE]
        self._new_votes(votacao, MONARQUISTAS, votos_monarquistas)

    #new_votation5 => get instance the new votation

    def _new_votation5(self):

        NUM = '5'
        DESCRICAO = 'Guilhotinar o Conde Pierre'
        prop = self._new_proposition(NUM, DESCRICAO)
        votacao = self._new_votation(
            NUM, DESCRICAO, BEGIN_SECOND_SEMESTER, prop)

        votos_girondinos = [models.SIM, models.SIM, models.ABSTENCAO]
        self._new_votes(votacao, GIRONDINOS, votos_girondinos)

        votos_jacobinos = [models.SIM, models.SIM, models.SIM]
        self._new_votes(votacao, JACOBINOS, votos_jacobinos)

        votos_monarquistas = [models.NAO, models.NAO, models.NAO]
        self._new_votes(votacao, MONARQUISTAS, votos_monarquistas)

    #new_votation6 => get instance the new votation

    def _new_votation6(self):

        NUM = '6'
        DESCRICAO = 'Criação de novas escolas'
        prop = self._new_proposition(NUM, DESCRICAO)
        votacao = self._new_votation(
            NUM, DESCRICAO, BEGIN_SECOND_SEMESTER, prop)

        votos_girondinos = [models.SIM, models.SIM, models.SIM]
        self._new_votes(votacao, GIRONDINOS, votos_girondinos)

        votos_jacobinos = [models.SIM, models.SIM, models.SIM]
        self._new_votes(votacao, JACOBINOS, votos_jacobinos)

        votos_monarquistas = [models.AUSENTE, models.SIM, models.SIM]
        self._new_votes(votacao, MONARQUISTAS, votos_monarquistas)

    #new_votation7 => get instance the new votation

    def _new_votation7(self):

        NUM = '7'
        DESCRICAO = 'Aumento do efetivo militar'
        prop = self._new_proposition(NUM, DESCRICAO)
        votacao = self._new_votation(
            NUM, DESCRICAO, BEGIN_SECOND_SEMESTER, prop)

        votos_girondinos = [models.SIM, models.SIM, models.ABSTENCAO]
        self._new_votes(votacao, GIRONDINOS, votos_girondinos)

        votos_jacobinos = [models.SIM, models.SIM, models.SIM]
        self._new_votes(votacao, JACOBINOS, votos_jacobinos)

        votos_monarquistas = [models.SIM, models.AUSENTE, models.SIM]
        self._new_votes(votacao, MONARQUISTAS, votos_monarquistas)

    # Voting with different attributes for test
    def _new_votation8(self):

        NUM = '8'
        DESCRICAO = 'Guerra contra a Inglaterra'
        prop = models.Proposicao()
        prop.id_prop = NUM
        prop.sigla = 'PL'
        prop.numero = NUM
        prop.ementa = 'o uso proibido de armas químicas'
        prop.descricao = 'descricao da guerra'
        prop.casa_legislativa = self.casa
        prop.indexacao = 'bombas, efeitos, destruições'
        prop.save()
        votacao = self._new_votation(
            NUM, DESCRICAO, BEGIN_SECOND_SEMESTER, prop)

        votos_girondinos = [models.NAO, models.NAO, models.NAO]
        self._new_votes(votacao, GIRONDINOS, votos_girondinos)

        votos_jacobinos = [models.ABSTENCAO, models.NAO, models.NAO]
        self._new_votes(votacao, JACOBINOS, votos_jacobinos)

        votos_monarquistas = [models.SIM, models.AUSENTE, models.SIM]
        self._new_votes(votacao, MONARQUISTAS, votos_monarquistas)

    def importar(self):
        self.casa = self._new_legislative_house()
        self._new_party()
        self._new_legislature()
        self._new_votation1()
        self._new_votation2()
        self._new_votation3()
        self._new_votation4()
        self._new_votation5()
        self._new_votation6()
        self._new_votation7()
        self._new_votation8()
        self._new_proposition('9', 'Legalizacao da maconha')


def main():

    print 'IMPORTANDO DADOS DA CONVENÇÃO NACIONAL FRANCESA'
    importer = ImportadorConvencao()
    importer.importar()
