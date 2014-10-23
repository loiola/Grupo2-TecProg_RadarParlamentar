# coding=utf8

# Copyright (C) 2012, Arthur Del Esposte, Leonardo Leite, Aline Santos,
# Gabriel Augusto, Thallys Martins, Thatiany Lima, Winstein Martins.
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

from __future__ import unicode_literals
from modelagem import models
import re


class Temas():

    def __init__(self):
        self.dictionary = {}

    @staticmethod
    def get_default_themes():
        """Get topics and insert topics synonymous"""

        themes = Temas()
        synonyms = {}
        
        synonyms['educação'] = [
            'escola', 'professor', 'aluno', 'EAD', 'universidade', 'cotas']
        synonyms['segurança'] = [
            'policial', 'polícia', 'bandido', 'PM', 'violência', 'presídios']
        synonyms['economia'] = [
            'impostos', 'dívida', 'tributos', 'financeira']
        synonyms['saúde'] = [
            'medicina', 'médicos', 'SUS', 'hospital', 'enfermeiro',
            'remédios', 'receita']
        synonyms['transporte'] = ['trânsito', 'pedágio',
                                   'congestionamento', 'ônibus',
                                   'metrô', 'avião']
        synonyms['violência'] = ['desarmamento', 'bullying']
        synonyms['esporte'] = [
            'futebol', 'inclusão', 'torcida', 'estádio', 'copa', 'jogo']
        synonyms['drogas'] = ['álcool', 'entorpecentes', 'maconha', 'cigarro']
        synonyms['turismo'] = ['hotel', 'turista']
        synonyms['meio ambiente'] = [
            'poluição', 'mineração', 'desmatamento', 'energia', 'usina']
        synonyms['assistência social'] = ['bolsa', 'família', 'cidadania']
        synonyms['tecnologia'] = [
            'inovação', 'internet', 'rede', 'dados', 'hacker']
        synonyms['política'] = [
            'eleição', 'search_political_party', 'mandato', 'eleitor', 'voto', 'reforma',
            'prefeito', 'deputado', 'vereador', 'senador', 'presidente',
            'sistema eleitoral']
        synonyms['família'] = [
            'maternidade', 'mãe', 'pai', 'paternidade', 'adoção']
        synonyms['constituição'] = ['PEC', 'constituinte']
        synonyms['burocrática'] = [
            'pauta', 'quorum', 'urgência', 'adiamento', 'sessão']

        for i in synonyms:
            for j in synonyms[i]:
                themes.insert_synonyms(i, j)
        return themes

    def insert_synonyms(self, theme, sinonimo):
        """Verify if has topics or synonymous. If topics or synonymous, add. If not,
        show valueError"""

        if theme is None or sinonimo is None:
            raise ValueError('Impossivel adicionar sinonimo\n')
        if theme.encode('utf-8') in self.dictionary:

        # if self.dicionario.has_key(tema.encode('utf-8')):
            self.dictionary[theme.encode('utf-8')].add(sinonimo.encode('utf-8'))
        else:
            self.dictionary[theme.encode('utf-8')] = set()
            self.dictionary[theme.encode('utf-8')].add(sinonimo.encode('utf-8'))

    def expand_keywords(self, keywords):
        expanded = []
        for word in keywords:
            expanded.extend(self.recover_synonyms(word))
        return expanded

    def recover_synonyms(self, word):
        word = word.encode('utf-8')
        words = []
        for theme, synonyms in self.dictionary.items():
            if word in theme or self.word_in_synonyms(word, synonyms):
                words.append(theme)
                words.extend(synonyms)
        if not words:
            words.append(word)
        return words

    def word_in_synonyms(self, palavra, synonyms):
        for synonym in synonyms:
            if palavra in synonym:
                return True
        return False


class FiltroVotacao():
    """Filters polls by fields:
        * votacao.descricao
        * proposicao.ementa
        * proposicao.descricao
        * proposicao.indexacao"""

    def __init__(self, legislative_house, period_legislative_house,
                 keywords):
        """Arguments:
            legislative_house: object of type CasaLegislativa;
            Only voting from this house will be filtered.
            period_legislative_house: object of type PeriodoCasaLegislativa;
            Only voting from this period will be filtered.
            keywords: strings list for be used in voting filtering."""

        self.legislative_house = legislative_house
        self.period_legislative_house = period_legislative_house
        self.keywords = keywords
        self.themes = Temas.get_default_themes()
        self.votings = []

    def filter_votings(self):
        self.votings = models.Votacao.by_legislative_house(
            self.legislative_house,
            self.period_legislative_house.ini,
            self.period_legislative_house.fim)
        if self.keywords:
            self.keywords = self.themes.expand_keywords(
                self.keywords)
            self.votings = self.filter_votings_by_keywords()
        return self.votings

    def filter_votings_by_keywords(self):
        votings_with_keywords = []
        for votacao in self.votings:
            if self.verify_keywords_in_voting(votacao):
                votings_with_keywords.append(votacao)
        return votings_with_keywords

    def verify_keywords_in_voting(self, votacao):
        for keyword in self.keywords:
            if(self.verify_if_word_exist_in_voting(votacao, keyword)):
                return True
        return False

    def verify_if_word_exist_in_voting(self, votacao, palavra_chave):

        # Search a substring within a string.
        proposition = votacao.proposicao
        if((re.search(palavra_chave.upper(),
            proposition.descricao.upper()) is not None) or
           (re.search(palavra_chave.upper(),
            proposition.ementa.upper()) is not None) or
           (re.search(palavra_chave.upper(),
            proposition.indexacao.upper()) is not None) or
           (re.search(palavra_chave.upper(),
                      votacao.descricao.upper()) is not None)):
            return True
        else:
            return False
