#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2012, Saulo Trento, Leonardo Leite
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Module cria_bd 

Classes:
GeradorBD -- Creates a sqlite3 database from propositions provided (list of objects of type Proposicao). 

Functions:
cria_bd_camara_deputados -- Creates the database in the chamber of deputies 'resultados/camara.db' from webservice requests to the chamber by the propositions listed 
                            in the file 'resultados/ids_que_existem.txt' (the latter can be created with ids_que_existem module)

cria_bc_cmsp -- Creates the database of the Câmara Munincipal de São Paulo from XMLs on resultados/cmsp[ano].xml
"""

from __future__ import unicode_literals
import cmsp
import proposicoes
import camaraws
import partidos
import sys
import re
import os
import model
import ids_que_existem
import sqlite3 as lite

class GeradorBD:
    """Creates a sqlite3 database from propositions provided (list of objects of type Proposicao)."""

    def __init__(self, proposicoes = [], db = "resultados/votos.db"):
        """ Arguments:
        proposicoes - list of objects of type Proposicao
        db - string with the location of the database to be generated (default = "resultados/votos.db")."""

        self.proposicoes = proposicoes
        self.db = db

    def arrumar_datas(self):
        con = lite.connect(self.db)
        with con:
            #cur = con.cursor()
            datas = con.execute("select idProp,idVot,data from VOTACOES;").fetchall()
            for v in datas:
                r = re.search('(\d*)/(\d*)/(\d*)',v[2])
                formato_sql = r.group(3).zfill(4) + '-' + r.group(2).zfill(2) + '-' + r.group(1).zfill(2)
                con.execute("update VOTACOES set data=? where idProp=?",(formato_sql,v[0]))
        con.close()
        return
            
    def _prepara_backup(self):
	
	# Delete previous backup:
        os.system('rm %s.backup' % self.db) 

	# Backup the previous database:
        os.system('mv %s %s.backup' % (self.db, self.db)) 

	# Delete the old database to a new:
        os.system('rm %s' % self.db) 

        print 'resultados/camara.db renomeado para resultados/camara.db.backup'
        print 'Backup anterior, se havia, foi apagado.'

    def gera_bd(self):

        self._prepara_backup()

        print 'Entre parenteses, (id da proposicao,numero de votacoes).'
        print 'Proposicoes sem votacoes aparecem como um ponto.'

	    # List of 'ints' that tells you how many votes each proposition listed above has:
        votations_number = []

        con = lite.connect(self.db) # abrir conexão com bd.
        with con:
            cur = con.cursor()

            # Create table if not exists TableName.
            # Test if table exist: SELECT name FROM sqlite_master WHERE type='table' AND name='table_name';
            cur.execute("CREATE TABLE if not exists  PROPOSICOES(idProp INT, tipo TEXT, num TEXT, ano TEXT, ementa TEXT, explicacao TEXT, situacao TEXT, num_votacoes INT)")
            cur.execute("CREATE TABLE if not exists PARLAMENTARES(id INT, nome TEXT, search_political_party TEXT, uf TEXT)")
            cur.execute("CREATE TABLE if not exists VOTACOES(idProp INT, idVot INT, resumo TEXT, data TEXT, hora TEXT, sim TEXT, nao TEXT, abstencao TEXT, obstrucao TEXT)")
            cur.execute("CREATE TABLE if not exists PARTIDOS(numero INT, nome TEXT)")
        con.close()

        for prop in self.proposicoes:
            votations_number.append(len(prop.votacoes))
            sys.stdout.write('(%s,%d),'%(prop.id, len(prop.votacoes)))
            sys.stdout.flush()

            # Add proposition in the table PROPOSICOES:
            con = lite.connect(self.db)
            con.execute("INSERT INTO PROPOSICOES VALUES(?,?,?,?,?,?,?,?)",(prop.id, prop.sigla, prop.numero, prop.ano, prop.ementa, prop.explicacao, prop.situacao, len(prop.votacoes)))
            con.commit()
            con.close()
            for v in prop.votacoes:
                print 'analisando votação %s' % v
                yes = []
                no = []
                abstention = []
                obstruction = []
                for d in v.deputados:
                    sys.stdout.write(".")
                    sys.stdout.flush()
                    idDep = model.Deputado.idDep(d.nome, d.partido, d.uf, self.db)
                    if d.voto == model.SIM: 
                        yes.append(idDep)
                    if d.voto == model.NAO:
                        no.append(idDep)
                    if d.voto == model.ABSTENCAO:
                        abstention.append(idDep)
                    if d.voto == model.OBSTRUCAO:
                        obstruction.append(idDep)
                print ' '
                pid = prop.id
                votid = prop.votacoes.index(v) + 1
                resum = v.resumo
                data = v.data
                hora = v.hora
                ssim = str(yes)
                snao = str(no)
                sabs = str(abstention)
                sobs = str(obstruction)
                con = lite.connect(self.db)
                con.execute("INSERT INTO VOTACOES VALUES(?,?,?,?,?,?,?,?,?)",(pid, votid, resum, data, hora, ssim, snao, sabs, sobs))
                con.commit()
                con.close()

        self.arrumar_datas()

IDS_QUE_EXISTEM = 'resultados/ids_que_existem.txt'
IDS_VOTADAS = 'resultados/votadas.txt'
def cria_bd_camara_deputados(arquivo_ids=IDS_VOTADAS):
    """Creates the Chamber od Deputies's database on 'resultados/camara.db'
        Arguments:
        arquivo_ids -- > File with the list of "id: tipo num/ano" (one entry per line, supporting comments with #).
                       > The function will use these ids to make calls to the web service and get the camera polls.
                       > The default value is the IDS_VOTADAS file.
                       > Another useful file is IDS_QUE_EXISTEM (which can be created with ids_que_existem module).
    """

    props = []
    lista_proposicoes = ids_que_existem.parse_txt(arquivo_ids)
    for iprop in lista_proposicoes:
        print 'AVALIANDO %s %s %s' % (iprop['tipo'],iprop['num'],iprop['ano'])

	# Proposition and get their votes from the web service:
        p = camaraws.get_votings(iprop['tipo'], iprop['num'],iprop['ano'])
        
	if p != None:
            props.append(p)

    print 'Agora sim gerando o banco'
    gerador = GeradorBD(props, 'resultados/camara.db')
    gerador.gera_bd()

def cria_bd_cmsp():
    """Creates the database of the Câmara Munincipal de São Paulo from XMLs on resultados/cmsp[ano].xml."""

    props = cmsp.from_xml(cmsp.XML2010)   
    props += cmsp.from_xml(cmsp.XML2011)
    props += cmsp.from_xml(cmsp.XML2012)

    gerador = GeradorBD(props, 'resultados/cmsp.db')
    gerador.gera_bd()

if __name__ == "__main__":
    cria_bd_cmsp()    

estamos em 1994? A Dilma pegou inflação de 916% ao ano? Pegou desemprego de 8,3% ao ano sem confiança do investidor externo para poder reverter o quadro? Pegou um país sem reservas nacionais? Implantou uma moeda nova e lutou para estabiliza-la? Criou uma política macroeconomica basicamente do zero? Não? Então pare de fingir que as situações são comparáveis. A senhora Rousseff pegou o país em ótimas condições internas e com cenário externo favorável a expansão comercial e política do Brasil. Fudeu com tudo.