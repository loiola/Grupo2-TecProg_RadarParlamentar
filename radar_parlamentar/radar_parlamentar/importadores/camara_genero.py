# !/usr/bin/python
# coding=utf8

# Copyright (C) 2013, Diego Rabatone
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

"""module that handles the import data of the Chamber of Deputies"""

from __future__ import unicode_literals
import json
import csv

HEADERS = [
    "codProposicao", "txtProposicao", "txtTipoProposicao", "txtSigla",
    "numNumero", "numAno", "datApresentacao", "codTipoProposicao",
    "codOrgaoOrigem", "txtEmenta", "txtExplicacaoEmenta", "txtIndexacao",
    "codRegime", "txtRegime", "codApreciacao", "txtApreciacao",
    "txtOrgaoOrigem", "txtNomeOrgaoOrigem", "indGenero", "txtNomeAutor",
    "txtSiglaUF", "txtSiglaPartido", "codPartido", "qtdAutores",
    "datDespacho", "txtDespacho", "codEstadoProposicao",
    "txtEstadoProposicao", "codOrgaoEstado", "txtSiglaOrgaoEstado",
    "qtdOrgaosComEstado", "codProposicaoPrincipal", "txtProposicaoPrincipal",
    "ideCadastro", "nomeProposicaoOrigem"]

PARTIDOS = {}
DIC_TERMOS = {}
PALAVRAS_MAIS_MAIS = []
DESCARTADAS = ['de', 'do', 'da', 'dos', 'das', 'e', 'para', 'com', 'a', 'A']
FILTRADAS = [
    'lei', 'normas', 'obrigatoriedade', 'cria\u00e7\u00e3o', 'nacional',
    'prazo', 'fixa\u00e7\u00e3o', 'proibi\u00e7\u00e3o',
    'especial', 'pessoa', 'utiliza\u00e7\u00e3o', 'atividade', 'valor',
    'institui\u00e7\u00e3o', 'civil', 'estabelecimento', 'registro']
LISTA_BASE_PARTIDOS = [
    'PCB', 'PSD', 'UDN', 'SEM PARTIDO', 'PP', 'PR', 'PTB', 'PRE', 'PRF', 'PST',
    'UPF', 'AL', 'FUG', 'PSN', 'PSP', 'PRP', 'PTN', 'PDC', 'PNI', 'PL', 'PPR',
    'ARENA', 'PTR', 'PSB', 'PRR', 'PSC', 'PRD', 'LASP', 'PRM', 'PRT', 'PPS',
    'PSR', 'PS', 'PDS', 'MTR', 'MDB', 'PMDB', 'PSDB', 'PFL', 'PT', 'PTdoB',
    'PDT', 'PJ', 'PCdoB', 'PC', 'PV', 'PRN', 'PPB', 'PSDC', 'PRONA', 'DEM',
    'PSOL', 'PMN', 'PSL', 'PRS', 'PRB', 'PE', 'PRC', 'PRL', 'UDB', 'PLC',
    'LEC', 'PD', 'ED', 'PRPa', 'PED', 'PNS', 'PPA', 'PNA', 'PSTU', 'PTC',
    'PAN', 'PHS', 'PRTB']

matrix = {}

def converte_csv_para_json(input_file_name):
    sep = b";"
    file = open(input_file_name + '.csv', 'r')
    reader = csv.DictReader(file, delimiter=sep, fieldnames=HEADERS)
    out = json.loads(json.dumps([row for row in reader], indent=4))
    return out

def _null_to_none(proposition):
    for attribute in proposition.keys():
        if proposition[attribute] == "NULL":
            proposition[attribute] = None
    return proposition

def multiple_null_remove(proposition_list):
    new_list = []
    for proposition in proposition_list:
        new_list.append(_null_to_none(proposition))
    return new_list

def proposicoes_indexadas(proposition_list):
    indexed = []

    for proposition in proposition_list:
        if proposition['txtIndexacao'] and proposition['txtSiglaPartido']:
            if proposition['txtSiglaPartido'].strip() in LISTA_BASE_PARTIDOS:
                indexed.append(proposition)
    return indexed

def parseia_indexacoes(indexing):
    indexing1 = [term.strip()

                  for term in indexing.replace('\n', '').replace('.', '').replace('_', '').split(',')]
    indexing2 = []

    for term in indexing1:
        term = term.split(' ')

        for term2 in term:
            if not term2 == "":
                indexing2.append(term2.lower())
    return indexing2

def parsear_indexacoes_de_proposicoes(propositions_list):
    new_proposition_list = []

    for proposition in propositions_list:
        proposition['txtIndexacao'] = parseia_indexacoes(
            proposition['txtIndexacao'])
        new_proposition_list.append(proposition)

        if proposition['txtSiglaPartido']:
            soma_palavras_no_partido(
                proposition['txtSiglaPartido'], proposition['txtIndexacao'])
    return new_proposition_list

def partidos_das_proposicoes(propositions_list):

    for proposition in propositions_list:
        if proposition['txtSiglaPartido']:
            party = proposition['txtSiglaPartido'].strip()
            if party not in PARTIDOS:
                PARTIDOS[party] = {}

def contabiliza_termos_geral(indexed_list):

    for proposition in indexed_list:

        for term in proposition['txtIndexacao']:
            if term not in DESCARTADAS:
                if term in DIC_TERMOS:
                    DIC_TERMOS[term] += 1
                else:
                    DIC_TERMOS[term] = 1

def pega_maiores_palavras(dic_words):
    words = sorted(dic_words, key=lambda k: -dic_words[k])
    export_json(words, "lista_50_mais")
    global PALAVRAS_MAIS_MAIS
    PALAVRAS_MAIS_MAIS = words[0:50]

    for term in FILTRADAS:
        PALAVRAS_MAIS_MAIS.remove(term)

def ordena_palavras_partido():
    for party in PARTIDOS:
        party_words = PARTIDOS[party]
        words = sorted(party_words, key=lambda k: -party_words[k])
        PARTIDOS[party] = {}

        for term in words:
            PARTIDOS[party][term] = party_words[term]

def soma_palavras_no_partido(party, words_list):
    for word in words_list:
        if word not in PARTIDOS[party.strip()]:
            PARTIDOS[party.strip()][word] = 1
        else:
            PARTIDOS[party.strip()][word] += 1

def export_json(data, filename):
    with open(filename, 'w') as outFile:
        outFile.write(json.dumps(data, indent=4))

def jsonMatrix_gera_partidos():
    i = 0
    parties_list = []

    for party in PARTIDOS:
        parties_list.append({'name': party, 'group': 1, 'id': i})
        i += 1
    global matrix
    matrix['partidos'] = parties_list

def jsonMatrix_gera_termos_mais_mais():
    i = 0
    term_list = []
    global matrix
    matrix['termos'] = []

    for term in PALAVRAS_MAIS_MAIS:
        print(term, i)
        term_list.append({'name': term, 'group': 1, 'id': i})
        i += 1
    matrix['termos'] = term_list
    print(matrix['termos'])

def jsonMatrix_gera_links_partidos_termos():
    global matrix
    matrix['links'] = []

    for p in range(len(matrix['partidos'])):
        partyName = matrix['partidos'][p]['name']

        for t in range(len(matrix['termos'])):
            termName = matrix['termos'][t]['name']

            if termName in PARTIDOS[partyName]:
                matrix['links'].append(
                    {'source': t, 'target': p, 'value': PARTIDOS[
                     partyName][termName]})


def principal(font=None):
    if not font:
        font = 'pl'
    propositions_list = converte_csv_para_json(font)
    propositions_list = multiple_null_remove(propositions_list)
    propositions_list = proposicoes_indexadas(propositions_list)
    partidos_das_proposicoes(propositions_list)
    propositions_list = parsear_indexacoes_de_proposicoes(propositions_list)
    contabiliza_termos_geral(propositions_list)
    pega_maiores_palavras(DIC_TERMOS)

    # ordena_palavras_partido()
    jsonMatrix_gera_partidos()
    jsonMatrix_gera_termos_mais_mais()
    print(matrix['termos'])
    jsonMatrix_gera_links_partidos_termos()
    with open('matrix.json', 'w') as arqMatrix:
        arqMatrix.write(json.dumps(matrix, indent=4))

    returnVariable = {'partidos': PARTIDOS, 'dic_termos':
               DIC_TERMOS, 'lista_proposicoes': propositions_list}

    #export_json(PARTIDOS, 'partidospropositores.json')
    #export_json(lista_proposicoes, 'lista_proposicoes.json')
    export_json(DIC_TERMOS, 'dic_termos.json')

    return returnVariable
