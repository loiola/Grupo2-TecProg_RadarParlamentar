# !/usr/bin/python
# coding=utf8

# Copyright (C) 2012, Leonardo Leite, Guilherme Januário, Diego Rabatone
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

"""CMSP Module (Câmara Municipal de São Paulo)"""

from __future__ import unicode_literals
from django.utils.dateparse import parse_datetime
from modelagem import models
import re
import sys
import os
import xml.etree.ElementTree as etree

# Date on which the XML files were updated
ULTIMA_ATUALIZACAO = parse_datetime('2012-12-31 0:0:0')

MODULE_DIR = os.path.abspath(os.path.dirname(__file__))

# Files with the data provided by CMSP
XML2010 = os.path.join(MODULE_DIR, 'dados/cmsp/cmsp2010.xml')
XML2011 = os.path.join(MODULE_DIR, 'dados/cmsp/cmsp2011.xml')
XML2012 = os.path.join(MODULE_DIR, 'dados/cmsp/cmsp2012.xml')
XML2013 = os.path.join(MODULE_DIR, 'dados/cmsp/cmsp2013.xml')
XML2014 = os.path.join(MODULE_DIR, 'dados/cmsp/cmsp2014.xml')

# Types of propositions found in the PBMC XMLs. Be list helps identify the votes 
# that are propositions. Examples of votes that are not propositions: Postponement 
# of prolongation Expedient; Other items postponement of the Tariff.
TIPOS_PROPOSICOES = ['PL', 'PLO', 'PDL']

# Regex that captures a proposition name (ex: PL 12/2010)
PROP_REGEX = '([a-zA-Z]{1,3}) ([0-9]{1,4}) ?/([0-9]{4})'

INICIO_PERIODO = parse_datetime('2010-01-01 0:0:0')
FIM_PERIODO = parse_datetime('2012-12-31 0:0:0')


class GeradorCasaLegislativa(object):

    def gerar_cmsp(self):
        try:
            cmsp = models.CasaLegislativa.objects.get(nome_curto='cmsp')
        except models.CasaLegislativa.DoesNotExist:
            cmsp = self.salvar_cmsp()
        return cmsp

    def salvar_cmsp(self):
        cmsp = models.CasaLegislativa()
        cmsp.nome = 'Câmara Municipal de São Paulo'
        cmsp.nome_curto = 'cmsp'
        cmsp.esfera = models.MUNICIPAL
        cmsp.local = 'São Paulo - SP'
        cmsp.atualizacao = ULTIMA_ATUALIZACAO
        cmsp.save()
        return cmsp


class XmlCMSP:

    def __init__(self, cmsp, verbose=False):
        self.parlamentares = {}
        self.cmsp = cmsp
        self.verbose = verbose

    def converte_data(self, data_str):
        """Converts string "d/m/y" to datetime object;
        returns None if data_str is invalid"""

        DATA_REGEX = '(\d\d?)/(\d\d?)/(\d{4})'
        res = re.match(DATA_REGEX, data_str)
        if res:
            new_str = '%s-%s-%s 0:0:0' % (
                res.group(3), res.group(2), res.group(1))
            return parse_datetime(new_str)
        else:
            return None

    def prop_nome(self, texto):
        """Search "type num/ano" in the text"""

        res = re.search(PROP_REGEX, texto)
        if res:
            nome = res.group(1).upper()
            if self.votacao_valida(nome, texto):
                return res.group(0).upper()
        return None

    def votacao_valida(self, nome_prop, texto):
        return nome_prop in TIPOS_PROPOSICOES and not 'Inversão' in texto

    def tipo_num_anoDePropNome(self, prop_nome):
        """Extract year from "tipo num/ano" """
        res = re.search(PROP_REGEX, prop_nome)
        if res:
            return res.group(1), res.group(2), res.group(3)
        else:
            return None, None, None

    def voto_cmsp_to_model(self, voto):
        """Interprets as voting is up in XML and responds suitability modeling 
        in models.py"""

        if voto == 'Não':
            return models.NAO
        elif voto == 'Sim':
            return models.SIM
        elif voto == 'Não votou':
            return models.AUSENTE
        elif voto == 'Abstenção':
            return models.ABSTENCAO
        else:
            print 'tipo de voto (%s) nao mapeado!' % voto
            return models.ABSTENCAO

    def partido(self, ver_tree):
        nome_partido = ver_tree.get('Partido').strip()
        partido = models.Partido.from_name(nome_partido)
        if partido is None:
            print 'Nao achou o partido %s' % nome_partido
            partido = models.Partido.get_no_party()
        return partido

    def votante(self, ver_tree):
        id_parlamentar = ver_tree.get('IDParlamentar')
        if id_parlamentar in self.parlamentares:
            votante = self.parlamentares[id_parlamentar]
        else:
            votante = models.Parlamentar()
            votante.save()
            votante.id_parlamentar = id_parlamentar
            votante.nome = ver_tree.get('NomeParlamentar')
            votante.save()
            if self.verbose:
                print 'Vereador %s salvo' % votante
            self.parlamentares[id_parlamentar] = votante
            # TODO gender
        return votante

    def legislatura(self, ver_tree):
        """Creates and returns a legistura for the given party"""

        partido = self.partido(ver_tree)
        votante = self.votante(ver_tree)

        # TODO also filter by start and end
        legs = models.Legislatura.objects.filter(
            parlamentar=votante, partido=partido, casa_legislativa=self.cmsp)
       
       # TODO this period should be further refined to support guys who switch partidos
        if legs:
            leg = legs[0]
        else:
            leg = models.Legislatura()
            leg.parlamentar = votante
            leg.partido = partido
            leg.casa_legislativa = self.cmsp
            leg.inicio = INICIO_PERIODO
            leg.fim = FIM_PERIODO
            leg.save()

        return leg

    def votos_from_tree(self, vot_tree, votacao):
        """Extract list of votes the vote of XML and saved in the database
        Arguments:
           vot_tree -- tree of votes
           votacao -- object of Votacao type"""

        for ver_tree in vot_tree.getchildren():
            if ver_tree.tag == 'Vereador':
                leg = self.legislatura(ver_tree)
                voto = models.Voto()
                voto.legislatura = leg
                voto.votacao = votacao
                voto.opcao = self.voto_cmsp_to_model(ver_tree.get('Voto'))
                if voto.opcao is not None:
                    voto.save()

    def votacao_from_tree(self, proposicoes, votacoes, vot_tree):

        # If the votation is nominal, vot_tree gets the subject and the menu
        votacao_TipoVotacao = vot_tree.get('TipoVotacao')
        if vot_tree.tag == 'Votacao' and votacao_TipoVotacao == 'Nominal':
            resumo = '%s -- %s' % (
                vot_tree.get('Materia'), vot_tree.get('Ementa'))

            # Prop_nome is as internally identifies the proposals
            # We want to know which proposition the analyzed voting is associated
            # Will return if prop_nome vote for Proposition
            prop_nome = self.prop_nome(resumo)

            # If the voting was associable to a proposition, so..
            if (prop_nome):
                id_vot = vot_tree.get('VotacaoID')
                votacoes_em_banco = models.Votacao.objects.filter(
                    id_vot=id_vot)
                if votacoes_em_banco:
                    vot = votacoes_em_banco[0]
                else:
                    if prop_nome in proposicoes:
                        prop = proposicoes[prop_nome]

                    # The propositon was not in dictionary yet, so we have to create and
                    # register it on dictionary
                    else:
                        prop = models.Proposicao()
                        prop.sigla, prop.numero, prop.ano = self.tipo_num_anoDePropNome(
                            prop_nome)
                        prop.casa_legislativa = self.cmsp
                        proposicoes[prop_nome] = prop

                    if self.verbose:
                        print 'Proposicao %s salva' % prop
                    prop.save()
                    vot = models.Votacao()

                    # To create de primary key and assign the votes
                    vot.save()
                    vot.id_vot = id_vot
                    vot.descricao = resumo
                    vot.data = self.converte_data(vot_tree.get('DataDaSessao'))
                    vot.resultado = vot_tree.get('Resultado')
                    self.votos_from_tree(vot_tree, vot)
                    vot.proposicao = prop
                    if self.verbose:
                        print 'Votacao %s salva' % vot
                    else:
                        self.progresso()
                    vot.save()

                votacoes.append(vot)

    def progresso(self):
        """Indica progresso na tela"""
        sys.stdout.write('x')
        sys.stdout.flush()


class ImportadorCMSP:
    """Save the CMSP XML archives datas in database"""

    def __init__(self, cmsp, verbose=False):
        """verbose (booleano) -- activate/desactivate prints on screen"""

        self.verbose = verbose
        self.xml_cmsp = XmlCMSP(cmsp, verbose)

    def importar_de(self, xml_file):
        """Save in Django database and returns the voting list"""

        if self.verbose:
            print "importando de: " + str(xml_file)

        tree = ImportadorCMSP.abrir_xml(xml_file)
        proposicoes = {}
            # The ley is a string (ex: 'pl 127/2004'); value ix object from
            # Proposiction type
        votacoes = []
        self.analisar_xml(proposicoes, votacoes, tree)
        return votacoes

    def analisar_xml(self, proposicoes, votacoes, tree):
        for vot_tree in tree.getchildren():
            self.xml_cmsp.votacao_from_tree(proposicoes, votacoes, vot_tree)

    @staticmethod
    def abrir_xml(xml_file):
    # f = open(xml_file, 'r')
    # xml = f.read()
    # f.close()
    # return etree.fromstring(xml)
        return etree.parse(xml_file).getroot()



def main():
    """Imports all data from XML by importer"""
    
    print 'IMPORTANDO DADOS DA CAMARA MUNICIPAL DE SAO PAULO (CMSP)'
    gerador_casa = GeradorCasaLegislativa()
    cmsp = gerador_casa.gerar_cmsp()
    importer = ImportadorCMSP(cmsp)
    for xml in [XML2010, XML2011, XML2012, XML2013, XML2014]:
        importer.importar_de(xml)
    print 'Importacao dos dados da Camara Municipal de Sao Paulo (CMSP) terminada'
