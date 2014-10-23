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

PARTIES = {}
DIC_TERMS = {}
WORDS_MORE_MORE = []
DISCARDED = ['de', 'do', 'da', 'dos', 'das', 'e', 'para', 'com', 'a', 'A']
FILTERED = [
    'lei', 'normas', 'obrigatoriedade', 'cria\u00e7\u00e3o', 'nacional',
    'prazo', 'fixa\u00e7\u00e3o', 'proibi\u00e7\u00e3o',
    'especial', 'pessoa', 'utiliza\u00e7\u00e3o', 'atividade', 'valor',
    'institui\u00e7\u00e3o', 'civil', 'estabelecimento', 'registro']
BASE_LIST_PARTIES = [
    'PCB', 'PSD', 'UDN', 'SEM PARTIDO', 'PP', 'PR', 'PTB', 'PRE', 'PRF', 'PST',
    'UPF', 'AL', 'FUG', 'PSN', 'PSP', 'PRP', 'PTN', 'PDC', 'PNI', 'PL', 'PPR',
    'ARENA', 'PTR', 'PSB', 'PRR', 'PSC', 'PRD', 'LASP', 'PRM', 'PRT', 'PPS',
    'PSR', 'PS', 'PDS', 'MTR', 'MDB', 'PMDB', 'PSDB', 'PFL', 'PT', 'PTdoB',
    'PDT', 'PJ', 'PCdoB', 'PC', 'PV', 'PRN', 'PPB', 'PSDC', 'PRONA', 'DEM',
    'PSOL', 'PMN', 'PSL', 'PRS', 'PRB', 'PE', 'PRC', 'PRL', 'UDB', 'PLC',
    'LEC', 'PD', 'ED', 'PRPa', 'PED', 'PNS', 'PPA', 'PNA', 'PSTU', 'PTC',
    'PAN', 'PHS', 'PRTB']

matrix = {}

def main(font=None):
    if not font:
        font = 'pl'
    propositions_list = convert_csv_to_json(font)
    propositions_list = multiple_null_remove(propositions_list)
    propositions_list = index_propositions(propositions_list)
    get_political_parties_by_acronym(propositions_list)
    propositions_list = propositions_index_parse(propositions_list)
    account_terms(propositions_list)
    get_more_words(DIC_TERMS)


    generate_political_parties_with_jsonMatrix()
    generate_more_terms_with_jsonMatrix()
    print(matrix['termos'])
    generate_political_parties_terms_links_with_jsonMatrix()
    with open('matrix.json', 'w') as arqMatrix:
        arqMatrix.write(json.dumps(matrix, indent=4))

    returnVariable = {'partidos': PARTIES, 'dic_termos':
               DIC_TERMS, 'lista_proposicoes': propositions_list}

    export_json(DIC_TERMS, 'dic_termos.json')

    return returnVariable


def convert_csv_to_json(input_file_name):
    sep = b";"
    file = open(input_file_name + '.csv', 'r')
    reader = csv.DictReader(file, delimiter=sep, fieldnames=HEADERS)
    out = json.loads(json.dumps([row for row in reader], indent=4))
    return out

def convert_null_to_none(proposition):
    for attribute in proposition.keys():
        if proposition[attribute] == "NULL":
            proposition[attribute] = None
    return proposition

def multiple_null_remove(proposition_list):
    new_list = []
    for proposition in proposition_list:
        new_list.append(convert_null_to_none(proposition))
    return new_list

def index_propositions(proposition_list):
    indexed = []

    for proposition in proposition_list:
        if proposition['txtIndexacao'] and proposition['txtSiglaPartido']:
            if proposition['txtSiglaPartido'].strip() in BASE_LIST_PARTIES:
                indexed.append(proposition)
    return indexed

def do_index_parse(indexing):
    indexing1 = [term.strip()

    for term in indexing.replace('\n', '').replace('.', '').replace('_', '').split(',')]
    indexing2 = []

    for term in indexing1:
        term = term.split(' ')

        for term2 in term:
            if not term2 == "":
                indexing2.append(term2.lower())
    return indexing2

def propositions_index_parse(propositions_list):
    new_proposition_list = []

    for proposition in propositions_list:
        proposition['txtIndexacao'] = do_index_parse(
            proposition['txtIndexacao'])
        new_proposition_list.append(proposition)

        if proposition['txtSiglaPartido']:
            sum_words_political_party(
                proposition['txtSiglaPartido'], proposition['txtIndexacao'])
    return new_proposition_list

def get_political_parties_by_acronym(propositions_list):

    for proposition in propositions_list:
        if proposition['txtSiglaPartido']:
            party = proposition['txtSiglaPartido'].strip()
            if party not in PARTIES:
                PARTIES[party] = {}

def account_terms(indexed_list):

    for proposition in indexed_list:

        increment_variable = 1

        for term in proposition['txtIndexacao']:
            if term not in DISCARDED:
                if term in DIC_TERMS:
                    DIC_TERMS[term] += increment_variable
                else:
                    DIC_TERMS[term] = increment_variable

def get_more_words(dic_words):
    words = sorted(dic_words, key=lambda k: -dic_words[k])
    export_json(words, "lista_50_mais")
    global WORDS_MORE_MORE
    WORDS_MORE_MORE = words[0:50]

    for term in FILTERED:
        WORDS_MORE_MORE.remove(term)

def arrange_words_political_party():
    for party in PARTIES:
        party_words = PARTIES[party]
        words = sorted(party_words, key=lambda k: -party_words[k])
        PARTIES[party] = {}

        for term in words:
            PARTIES[party][term] = party_words[term]

def sum_words_political_party(party, words_list):
    for word in words_list:
        if word not in PARTIES[party.strip()]:
            PARTIES[party.strip()][word] = 1
        else:
            PARTIES[party.strip()][word] += 1

def export_json(data, filename):
    with open(filename, 'w') as outFile:
        outFile.write(json.dumps(data, indent=4))

def generate_political_parties_with_jsonMatrix():
    i = 0
    parties_list = []

    for party in PARTIES:
        parties_list.append({'name': party, 'group': 1, 'id': i})
        i += 1
    global matrix
    matrix['partidos'] = parties_list

def generate_more_terms_with_jsonMatrix():
    i = 0
    term_list = []
    global matrix
    matrix['termos'] = []

    for term in WORDS_MORE_MORE:
        print(term, i)
        term_list.append({'name': term, 'group': 1, 'id': i})
        i += 1
    matrix['termos'] = term_list
    print(matrix['termos'])

def generate_political_parties_terms_links_with_jsonMatrix():
    global matrix
    matrix['links'] = []

    for p in range(len(matrix['partidos'])):
        partyName = matrix['partidos'][p]['name']

        for t in range(len(matrix['termos'])):
            termName = matrix['termos'][t]['name']

            if termName in PARTIES[partyName]:
                matrix['links'].append(
                    {'source': t, 'target': p, 'value': PARTIES[
                     partyName][termName]})