# -*- coding: utf-8 -*-

# Copyright (C) 2012, Leonardo Leite
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

"""Model module -- domain modeling, based on web services XMLs of the chamber.
<<<<<<< HEAD
=======

Classes:
Partido -- modelates a politicial party.
Proposicao -- modelates a parlamentary proposition.
Votacao -- modelates a voting belonged to a parliamentary proposition.
Deputado -- modelate a vote of a deputy in a voting.
VotoPartido -- represents a set of votes of a political party.
VotoUF -- represents a set of voting of a UF (estate or distrito federal)."""


from __future__ import unicode_literals
import xml.etree.ElementTree as etree
import io
import re
import sqlite3 as lite

SIM = 'Sim'
NAO = 'Não'
ABSTENCAO = 'Abstenção'

# Interpreted as Abstenção:
OBSTRUCAO = 'Obstrução' 

class Partido:
    """Models a political party
     attributes: 
    nome -- ex: 'PT' [string] 
    numero -- ex: '13' [string]."""

# Attributes to be implemented in the future:
# tamanho [int], search_political_party do governo (executivo)?[booleano],
# cargos_indicados (amount of executive positions indication that this political party has)
# as size, ruling party and other variables are characteristics of the party, perhaps best
# SituacaoPartido they belong to a class, which would have attributes like: party, period
# and cited.

    def __init__(self, nome='', numero=''):
        """Initializing variables"""

        self.nome = nome
        self.numero = numero

class Proposicao:
    """Models a parliamentary proposition
     attributes:
     id, symbol, number, year, menu, explanation, situation - strings
     votacaoes - list of objects of type Voting."""


    def __init__(self):
        """Initializing variables"""

        self.id = ''
        self.sigla = ''
        self.numero = ''
        self.ano = ''
        self.ementa = ''
        self.explicacao = ''
        self.situacao = ''
        self.votacoes = []
    
    @staticmethod
    def fromxml(xml):
        """Transforms "an XML text in a proposition
         arguments:
         xml - the string containing XML returned from web service that 
		returns a proposition polls

         returns:
         An object of type Proposition."""

        tree = etree.fromstring(xml)
        prop = Proposicao()
        prop.sigla = tree.find_legislature('Sigla').text
        prop.numero = tree.find_legislature('Numero').text
        prop.ano = tree.find_legislature('Ano').text

        for child in tree.find_legislature('Votacoes'):
          vot = Votacao.fromtree(child)
          prop.votacoes.append(vot)

        return prop

    @staticmethod
    def fromxmlid(xml):
        """Transforms an XML ObterProposicaoPorID text in a string like "acronym
		number / year"
         arguments:
         xml - the string containing XML returned from web service that returns 
		proposition by id

         returns:
         string like "acronym number / year", eg fromxmlid (513 512) returns "540/2011 MPV."""

        tree = etree.fromstring(xml)
        nome = tree.find_legislature('nomeProposicao').text

        return nome


    def __unicode__(self):

        return "[%s %s/%s]: %s \nEmenta: %s \nSituação: %s" % (self.sigla, self.numero, 
		self.ano, self.explicacao, self.ementa, self.situacao) 

    def __str__(self):

        return unicode(self).encode('utf-8')

    def nome(self):

        return "%s %s/%s" % (self.sigla, self.numero, self.ano)

class Votacao:
    """Models belonging to a vote a parliamentary proposition
     attributes:
     summary, date, time - strings
     Members - list of objects of type Member."""

    def __init__(self):
        """Initializing variables"""

        self.resumo = ''
        self.data = ''
        self.hora = ''
        self.deputados = []

    @staticmethod
    def fromtree(tree):
        """Transforms an XML in a vote
         arguments:
         tree - xml.etree.ElementTree type object representing the XML that 
		describes a vote

         returns:
         An object of type Voting."""

        vot = Votacao() 
        vot.resumo = tree.attrib['Resumo']
        vot.data = tree.attrib['Data']
        vot.hora = tree.attrib['Hora']

        for child in tree:
          dep = Deputado.fromtree(child)
          vot.deputados.append(dep)

        return vot

    def por_partido(self):
        """Returns aggregate votes by party
         returns:
         A dictionary whose key is the party name (string) and the value is a 
		VotoPartido."""

        votes_by_party = {}
        for dep in self.deputados:
          part = dep.partido

          if not part in votes_by_party:
            votes_by_party[part] = VotoPartido(part)
          voto = votes_by_party[part]
          voto.add(dep.voto)

        return votes_by_party
  
    def por_uf(self):
        """Returns votes aggregated by UF
         returns:
         A dictionary whose key is the name of the UF (string) and the value is a VotoUF.
	"""

        votes_by_uf = {}
        for dep in self.deputados:
          uf = dep.uf

          if not uf in votes_by_uf:
            votes_by_uf[uf] = VotoUF(uf)
          voto = votes_by_uf[uf]
          voto.add(dep.voto)

        return votes_by_uf

    def __unicode__(self):

        return "[%s, %s] %s" % (self.data, self.hora, self.resumo)

    def __str__(self):

        return unicode(self).encode('utf-8')

class Deputado:
    """Models the vote of a member in a vote
     attributes:
     name, party, uf - strings that characterize the deputy
     vote - vote cast by Congressman \ in {YES, NO, ABSTAIN, OBSTRUCTION}

     Static methods: (The bd is in 'results / camara.db')
     fromtree (tree) - Transforms an XML object in a kind Mr.
     inicializar_dicpartidos () - Copies PARTIES db table in Deputado.dicpartidos 
	variable. Also uses information from 'listapartidos.txt' file.
     inicializar_diclistadeps () - Copies PARLIAMENTARY db table in Deputado.diclistadeps 
	variable.
     idPartido (siglapartido) - Returns integer that identifies the party 
	according to the table PARTIES bd.
     idUF (siglauf) - Returns integer that identifies a UF. Use uppercase. 
	Play StandardError if UF does not exist.
     idDep (name, party, uf) - Returns integer called idDep that uniquely 
	identifies the tuple (name, party, uf) according to the MPS table bd."""

    listauf = ['AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG',
	'PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO']

    """Chave stands, the value is idPartido, number he won (which is not the 
	electoral number, we are not using because it is subject to change over time	      
    dicpartidos = dict() """

    dicpartidos_inicializado = False
    diclistadeps = {}
    diclistadeps_inicializado = False

    def __init__(self):
        """Initializing variables"""

        self.nome = ''
        self.partido = ''
        self.uf = ''
        self.voto = ''

    @staticmethod
    def fromtree(tree):
        """Transforms an XML in the vote of a deputy
         arguments:
         tree - xml.etree.ElementTree type object representing the XML that 
        describes the vote of a member

         returns:
         An object of type deputy."""

        dep = Deputado()
        dep.nome = tree.attrib['Nome']
        dep.partido = tree.attrib['Partido']
        dep.uf = tree.attrib['UF']
        dep.voto = tree.attrib['Voto']

        return dep

    def __unicode__(self):
        ufstr = ''

        if self.uf:
            ufstr = '-%s' % self.uf

        return "%s (%s%s) votou %s" % (self.nome, self.partido, ufstr, self.voto)

    def __str__(self):

        return unicode(self).encode('utf-8')

    @staticmethod
    def inicializar_dicpartidos(bd='resultados/camara.db'):

    """Reads the database 'results / camaraws.db' PARTIES the table,
	if present, to initialize the variable with Deputado.dicpartidos 
	partidos that appear there. Deputado.dicpartidos is a dictionary whose
	key acronyms of partidos and how the value idPartido (internal unique
	identifier, not necessarily equal to the electoral number).

    Then reads the listapartidos.txt file that contains lines like 'PV 88'
	where the acronym stands for a party and is the number one preferred 
	idPartido that can be chosen by the user by editing the file manually. 
	If a party 'listapartidos.txt' has already been found in the database 
	with a different idPartido, prevails the database, the file is ignored, 
	issuing a warning message.

    This allows the user to choose the idPartido you want to give to each party,
	for example making it coincide with the electoral number. Also allows 
	databases created at different times end up atribuindos different idPartidos, 
	which should not be a problem if the programs are consistent, but it 
	could make finding a bug.

    Returns 0 if the reading is successfully executed, 1 if the
	listapartidos.txt file does not exist (or do not have permission to read)."""

        con = lite.connect(bd)
        if len(con.execute("select * from sqlite_master where type='table' "
                           "and name='PARTIDOS'").fetchall()) != 0:
	    # If table exists
            partsdb = con.execute('SELECT * FROM PARTIDOS').fetchall()
             
	        # Print partsdb:
            for p in partsdb:
                Deputado.dicpartidos[p[1]] = p[0]
        file_listapartidos = 'listapartidos.txt'

        try:
            prop_file = open(file_listapartidos,'r')

        except IOError:
            return 1
        
        regexp = '([A-z_-]*)\s*(\d*)'

        for line in prop_file:

	        # Print line:
            res = re.search(regexp,line)

            if res:
                siglawannabe = res.group(1)
                idwannabe = res.group(2)

                # Check if already have: if yes, warning. If not, it adds to the database and dicpartidos:
                if idwannabe in Deputado.dicpartidos.values():

                    if not Deputado.dicpartidos[siglawannabe] == idwannabe:
                        print "WARNING: listapartidos.txt associa o %s ao idPartido %s" % \
                              (siglawannabe,idwannabe)
                        print "mas no banco de dados este id ja esta associado ao %s." % \
                              (Deputado.dicpartidos[idwannabe])
                        print "Foi mantido o valor do banco de dados, e ignorado o de listapartidos.txt."

                elif siglawannabe in Deputado.dicpartidos:
                    if not Deputado.dicpartidos[siglawannabe] == idwannabe:
                        print "WARNING: listapartidos.txt associa o %s ao idPartido %s" % \
                              (siglawannabe,idwannabe)
                        print "mas no banco de dados o %s ja esta associado ao id %s." % \
                              (siglawannabe,Deputado.dicpartidos[siglawannabe])
                        print "Foi mantido o valor do banco de dados, e ignorado o de listapartidos.txt."

                else:
                    Deputado.dicpartidos[res.group(1)] = int(res.group(2))
                    con.execute("insert into PARTIDOS values(?,?)",(idwannabe,siglawannabe))
                    con.commit()

        con.close_tag()

        return 0
    
    @staticmethod
    def inicializar_diclistadeps():
    """Reads the database 'results / camara.db' PARLIAMENTARY the table,
	if present, to initialize the variable with Deputado.diclistadeps deputies 
	who appear there. Deputado.diclistadeps is a dictionary whose key an 
	integer of up to five digits called idPartUF that identifies a couple party-UF, 
        and value as a list of members who belong to this party-UF."""

        con = lite.connect('resultados/camara.db')
        if len(con.execute("select * from sqlite_master where type='table' and "
                           "name='PARLAMENTARES'").fetchall()) != 0:
	    # If table exists
            depsdb = con.execute('SELECT * FROM PARLAMENTARES').fetchall()
            con.close_tag()

            for d in depsdb:
                iddep = d[0]
                idpartuf = int(iddep/1000)
                Deputado.diclistadeps[idpartuf] = [d[1]]

        return

    @staticmethod
    def idPartido(siglapartido, bd='resultados/camara.db'):
        """Returns an integer that identifies the party according to the PARTIES table bd.
        If the party is not on the table, gets a new identifier, and is inserted into the table."""

        if siglapartido in Deputado.dicpartidos:
            return Deputado.dicpartidos[siglapartido]
        else:
            if not Deputado.dicpartidos_inicializado:
                Deputado.inicializar_dicpartidos(bd)
                Deputado.dicpartidos_inicializado = True
                if siglapartido in Deputado.dicpartidos:
                    return Deputado.dicpartidos[siglapartido]

            # If it is here, found new political party.
            idpartido = max(Deputado.dicpartidos.values()+[0]) + 1
            Deputado.dicpartidos[siglapartido] = idpartido
            print "Novo search_political_party '%s' encontrado. Atribuido idPartido %d" % \
                  (siglapartido,idpartido)

            # Put on database:
            con = lite.connect(bd)
            con.execute('INSERT INTO PARTIDOS VALUES(?,?)',(idpartido,siglapartido))
            con.commit()
            con.close_tag()

        return idpartido

    @staticmethod
    def idUF(siglauf):
    """Given the abbreviation of a unit of the federation (two capital)
	returns an integer between 1 and 27 that uniquely identifies, or None if the symbol is not valid.
	"""

        try:
            iduf = Deputado.listauf.index(siglauf) + 1
            return iduf
        except:
            raise StandardError('UF %s nao existe. Obs: usar maiusculas.' % siglauf)

    @staticmethod
    def idDep(nome,partido,uf,bd='resultados/camara.db'):
    """Given name, party and uf a deputy, returns an integer, called idDep,
	that uniquely identifies, according to MPS table bd.

         Deputies with the same name but different membership are treated as
	separate members (might happen in the event of change of party).
         The idDep is constructed so as to be sufficient to determine uf party
	and just looking at the numbers, it has the syntax: PPPEENNN where PPP 
	is the idPartido, EE is the idUF and NNN is a unique number for each 
	name deputy within a party-uf.
         If the Member is not in MPS table bd, he gains a new idDep, is inserted 
	into the table, and returns the newly assigned idDep."""

	    # Print Deputado.dicpartidos_inicializado:
        if not Deputado.diclistadeps_inicializado:
            Deputado.inicializar_diclistadeps()
            Deputado.diclistadeps_inicializado = True

	    # This is used when UF makes no sense (ex: câmara municipal):
        iduf = '99'

        if uf:
            iduf = Deputado.idUF(uf)
        idPartUF = '%s%s' % (Deputado.idPartido(partido, bd), iduf)
        idPartUF = int(idPartUF)

        if idPartUF in Deputado.diclistadeps:
            if nome in Deputado.diclistadeps[idPartUF]:
                iddep = idPartUF*1000 + Deputado.diclistadeps[idPartUF].index(nome) + 1
                return iddep

            else:
                Deputado.diclistadeps[idPartUF].append(nome)
                iddep = idPartUF*1000 + Deputado.diclistadeps[idPartUF].index(nome) + 1
        else:
            Deputado.diclistadeps[idPartUF] = [nome]
            iddep = idPartUF*1000 + 1

        con = lite.connect(bd)
        con.execute('INSERT INTO PARLAMENTARES VALUES(?,?,?,?)',(iddep,nome,partido,uf))
        con.commit()
        con.close_tag()

        return iddep



class VotosAgregados:
    """Represents a number of votes
    attributes:
    yes, no, abstention - integers representing the number of votes in the set."""


    def add(self, voto):
        """Adds a set of votes to vote
        Arguments:
        voto -- string \in {SIM, NAO, ABSTENCAO, OBSTRUCAO}
        OBSTRUCAO conta como um voto NAO."""

        increment_by_one = 1

        if (voto == SIM):
          self.sim += increment_by_one
        if (voto == NAO):
          self.nao += increment_by_one
        if (voto == OBSTRUCAO):
          self.nao += increment_by_one
        if (voto == ABSTENCAO):
          self.abstencao += increment_by_one

    def __init__(self):
        """Initializing variables"""

        self.sim = 0
        self.nao = 0
        self.abstencao = 0

    def __unicode__(self):

        return '(%s, %s, %s)' % (self.sim, self.nao, self.abstencao)

    def __str__(self):

        return unicode(self).encode('utf-8')

class VotoPartido(VotosAgregados):
    """Represents a set of votes a party
    attributes:
    yes, no, abstention - integers representing the number of votes in the set
    party - string."""

    def __init__(self, partido):

        """Initializing variables"""
        VotosAgregados.__init__(self)
        self.partido = partido

class VotoUF(VotosAgregados):
    """Represents a set of votes of a UF (state or federal district)
    attributes:
    yes, no, abstention - integers representing the number of votes in the set
    uf - string."""
     
    def __init__(self, uf):
        """Initializing variables"""

        VotosAgregados.__init__(self)
        self.uf = uf

# -*- coding: utf-8 -*-

# Copyright (C) 2012, Leonardo Leite
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

""" Model module -- domain modeling, based on web services XMLs of the chamber.

>>>>>>> estilo-e-design

Classes:
Partido -- modelates a politicial party.
Proposicao -- modelates a parlamentary proposition.
Votacao -- modelates a voting belonged to a parliamentary proposition.
Deputado -- modelate a vote of a deputy in a voting.
VotoPartido -- represents a set of votes of a political party.
VotoUF -- represents a set of voting of a UF (estate or distrito federal)."""


from __future__ import unicode_literals
import xml.etree.ElementTree as etree
import io
import re
import sqlite3 as lite

SIM = 'Sim'
NAO = 'Não'
ABSTENCAO = 'Abstenção'

# Interpreted as Abstenção:
OBSTRUCAO = 'Obstrução' 

class Partido:
    """Models a political party
    attributes:
    nome -- ex: 'PT' [string] 
    numero -- ex: '13' [string]."""

# Attributes to be implemented in the future:
# tamanho [int], search_political_party do governo (executivo)?[booleano],
# cargos_indicados (amount of executive positions indication that this political party has)
# as size, ruling party and other variables are characteristics of the party, perhaps best
# SituacaoPartido they belong to a class, which would have attributes like: party, period
# and cited.

    def __init__(self, nome='', numero=''):
        """Initializing variables"""

        self.nome = nome
        self.numero = numero

class Proposicao:
    """Models a parliamentary proposition
    attributes:
    id, symbol, number, year, menu, explanation, situation - strings
    votacaoes - list of objects of type Voting."""


    def __init__(self):
        """Initializing variables"""

        self.id = ''
        self.sigla = ''
        self.numero = ''
        self.ano = ''
        self.ementa = ''
        self.explicacao = ''
        self.situacao = ''
        self.votacoes = []
    
    @staticmethod
    def fromxml(xml):
        """Transforms "an XML text in a proposition
        arguments:
        xml - the string containing XML returned from web service that returns a proposition polls

        returns:
        An object of type Proposition."""

        tree = etree.fromstring(xml)
        prop = Proposicao()
        prop.sigla = tree.find_legislature('Sigla').text
        prop.numero = tree.find_legislature('Numero').text
        prop.ano = tree.find_legislature('Ano').text

        for child in tree.find_legislature('Votacoes'):
          vot = Votacao.fromtree(child)
          prop.votacoes.append(vot)

        return prop

    @staticmethod
    def fromxmlid(xml):
        """Transforms an XML ObterProposicaoPorID text in a string like "acronym number / year"
        arguments:
        xml - the string containing XML returned from web service that returns proposition by id

        returns:
        string like "acronym number / year", eg fromxmlid (513 512) returns "540/2011 MPV."""

        tree = etree.fromstring(xml)
        nome = tree.find_legislature('nomeProposicao').text

        return nome


    def __unicode__(self):

        return "[%s %s/%s]: %s \nEmenta: %s \nSituação: %s" % (self.sigla, self.numero, self.ano, self.explicacao, self.ementa, self.situacao) 

    def __str__(self):

        return unicode(self).encode('utf-8')

    def nome(self):

        return "%s %s/%s" % (self.sigla, self.numero, self.ano)

class Votacao:
    """Models belonging to a vote a parliamentary proposition
    attributes:
    summary, date, time - strings
    Members - list of objects of type Member."""

    def __init__(self):
        """Initializing variables"""

        self.resumo = ''
        self.data = ''
        self.hora = ''
        self.deputados = []

    @staticmethod
    def fromtree(tree):
        """Transforms an XML in a vote
        arguments:
        tree - xml.etree.ElementTree type object representing the XML that describes a vote

        returns:
        An object of type Voting."""

        vot = Votacao() 
        vot.resumo = tree.attrib['Resumo']
        vot.data = tree.attrib['Data']
        vot.hora = tree.attrib['Hora']

        for child in tree:
          dep = Deputado.fromtree(child)
          vot.deputados.append(dep)

        return vot

    def por_partido(self):
        """Returns aggregate votes by party
        returns:
        A dictionary whose key is the party name (string) and the value is a VotoPartido."""

        votes_by_party = {}
        for dep in self.deputados:
          part = dep.partido
          if not part in votes_by_party:
            votes_by_party[part] = VotoPartido(part)
          voto = votes_by_party[part]
          voto.add(dep.voto)
        return votes_by_party
  
    def por_uf(self):
        """Returns votes aggregated by UF
        returns:
        A dictionary whose key is the name of the UF (string) and the value is a VotoUF."""

        votes_by_uf = {}
        for dep in self.deputados:
          uf = dep.uf
          if not uf in votes_by_uf:
            votes_by_uf[uf] = VotoUF(uf)
          voto = votes_by_uf[uf]
          voto.add(dep.voto)
        return votes_by_uf

    def __unicode__(self):

        return "[%s, %s] %s" % (self.data, self.hora, self.resumo)

    def __str__(self):

        return unicode(self).encode('utf-8')

class Deputado:
    """Models the vote of a member in a vote
    attributes:
    name, party, uf - strings that characterize the deputy
    vote - vote cast by Congressman \ in {YES, NO, ABSTAIN, OBSTRUCTION}

    Static methods: (The bd is in 'results / camara.db')
    fromtree (tree) - Transforms an XML object in a kind Mr.
    inicializar_dicpartidos () - Copies PARTIES db table in Deputado.dicpartidos variable. Also uses information from 'listapartidos.txt' file.
    inicializar_diclistadeps () - Copies PARLIAMENTARY db table in Deputado.diclistadeps variable.
    idPartido (siglapartido) - Returns integer that identifies the party according to the table PARTIES bd.
    idUF (siglauf) - Returns integer that identifies a UF. Use uppercase. Play StandardError if UF does not exist.
    idDep (name, party, uf) - Returns integer called idDep that uniquely identifies the tuple (name, party, uf) according to the MPS table bd."""

    listauf = ['AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO']

    # Chave stands, the value is idPartido, number he won (which is not the electoral number, we are not using because it is subject to change over time	      
    dicpartidos = dict() 

    dicpartidos_inicializado = False
    diclistadeps = {}
    diclistadeps_inicializado = False

    def __init__(self):
        """Initializing variables"""

        self.nome = ''
        self.partido = ''
        self.uf = ''
        self.voto = ''

    @staticmethod
    def fromtree(tree):
        """Transforms an XML in the vote of a deputy
        arguments:
        tree - xml.etree.ElementTree type object representing the XML that describes the vote of a member

        returns:
        An object of type deputy."""

        dep = Deputado()
        dep.nome = tree.attrib['Nome']
        dep.partido = tree.attrib['Partido']
        dep.uf = tree.attrib['UF']
        dep.voto = tree.attrib['Voto']

        return dep

    def __unicode__(self):
        ufstr = ''

        if self.uf:
            ufstr = '-%s' % self.uf

        return "%s (%s%s) votou %s" % (self.nome, self.partido, ufstr, self.voto)

    def __str__(self):

        return unicode(self).encode('utf-8')

    @staticmethod
    def inicializar_dicpartidos(bd='resultados/camara.db'):
        """Reads the database 'results / camaraws.db' PARTIES the table, if present, to
        initialize the variable with Deputado.dicpartidos partidos that appear there.
        Deputado.dicpartidos is a dictionary whose key acronyms of partidos and
        how the value idPartido (internal unique identifier, not necessarily equal to
        the electoral number).

        Then reads the listapartidos.txt file that contains lines like 'PV 88' where the
        acronym stands for a party and is the number one preferred idPartido that can be
        chosen by the user by editing the file manually. If a party
        'listapartidos.txt' has already been found in the database with a
        different idPartido, prevails the database, the file is ignored, issuing a
        warning message.

        This allows the user to choose the idPartido you want to give to each party, for
        example making it coincide with the electoral number. Also allows databases
        created at different times end up atribuindos different idPartidos, which
        should not be a problem if the programs are consistent, but it could make finding a bug.

        Returns 0 if the reading is successfully executed, 1 if the listapartidos.txt
        file does not exist (or do not have permission to read)."""

        con = lite.connect(bd)

        if len(con.execute("select * from sqlite_master where type='table' and "
                           "name='PARTIDOS'").fetchall()) != 0: # se tabela existe
            partsdb = con.execute('SELECT * FROM PARTIDOS').fetchall()
             
	        # Print partsdb:
            for p in partsdb:
                Deputado.dicpartidos[p[1]] = p[0]

        file_listapartidos = 'listapartidos.txt'

        try:
            prop_file = open(file_listapartidos,'r')

        except IOError:
            return 1
        
        regexp = '([A-z_-]*)\s*(\d*)'

        for line in prop_file:

	        # Print line:
            res = re.search(regexp,line)

            if res:
                siglawannabe = res.group(1)
                idwannabe = res.group(2)

                # Check if already have: if yes, warning. If not, it adds to the database
                # and dicpartidos:
                if idwannabe in Deputado.dicpartidos.values():
                    if not Deputado.dicpartidos[siglawannabe] == idwannabe:
                        print "WARNING: listapartidos.txt associa o %s ao idPartido %s" % \
                              (siglawannabe,idwannabe)
                        print "mas no banco de dados este id ja esta associado ao %s." % \
                              (Deputado.dicpartidos[idwannabe])
                        print "Foi mantido o valor do banco de dados, e ignorado o de listapartidos.txt."

                elif siglawannabe in Deputado.dicpartidos:
                    if not Deputado.dicpartidos[siglawannabe] == idwannabe:
                        print "WARNING: listapartidos.txt associa o %s ao idPartido %s" % \
                              (siglawannabe,idwannabe)
                        print "mas no banco de dados o %s ja esta associado ao id %s." % \
                              (siglawannabe,Deputado.dicpartidos[siglawannabe])
                        print "Foi mantido o valor do banco de dados, e ignorado o de listapartidos.txt."

                else:
                    Deputado.dicpartidos[res.group(1)] = int(res.group(2))
                    con.execute("insert into PARTIDOS values(?,?)",(idwannabe,siglawannabe))
                    con.commit()

        con.close_tag()

        return 0
    
    @staticmethod
    def inicializar_diclistadeps():
        """Reads the database 'results / camara.db' PARLIAMENTARY the table, if present,
        to initialize the variable with Deputado.diclistadeps deputies who appear there.
        Deputado.diclistadeps is a dictionary whose key an integer of up to five digits
        called idPartUF that identifies a couple party-UF,

        and value as a list of members who belong to this party-UF."""

        con = lite.connect('resultados/camara.db')

        if len(con.execute("select * from sqlite_master where type='table' and "
                           "name='PARLAMENTARES'").fetchall()) != 0: # Se a tabela existe
            depsdb = con.execute('SELECT * FROM PARLAMENTARES').fetchall()
            con.close_tag()

            for d in depsdb:
                iddep = d[0]
                idpartuf = int(iddep/1000)
                Deputado.diclistadeps[idpartuf] = [d[1]]

        return

    @staticmethod
    def idPartido(siglapartido, bd='resultados/camara.db'):
        """Returns an integer that identifies the party according to the PARTIES table bd.
        If the party is not on the table, gets a new identifier, and is inserted into the table."""

        if siglapartido in Deputado.dicpartidos:
            return Deputado.dicpartidos[siglapartido]

        else:
            if not Deputado.dicpartidos_inicializado:
                Deputado.inicializar_dicpartidos(bd)
                Deputado.dicpartidos_inicializado = True
                if siglapartido in Deputado.dicpartidos:
                    return Deputado.dicpartidos[siglapartido]

            # If it is here, found new political party.
            idpartido = max(Deputado.dicpartidos.values()+[0]) + 1
            Deputado.dicpartidos[siglapartido] = idpartido

            print "Novo search_political_party '%s' encontrado. Atribuido idPartido %d" % \
                  (siglapartido,idpartido)

            # Put on database:
            con = lite.connect(bd)
            con.execute('INSERT INTO PARTIDOS VALUES(?,?)',(idpartido,siglapartido))
            con.commit()
            con.close_tag()

        return idpartido

    @staticmethod
    def idUF(siglauf):
        """Given the abbreviation of a unit of the federation (two capital)
        returns an integer between 1 and 27 that uniquely identifies, or None if the
        symbol is not valid."""

        try:
            iduf = Deputado.listauf.index(siglauf) + 1
            return iduf
        except:
            raise StandardError('UF %s nao existe. Obs: usar maiusculas.' % siglauf)

    @staticmethod
    def idDep(nome,partido,uf,bd='resultados/camara.db'):
        """Given name, party and uf a deputy, returns an integer, called idDep,
        that uniquely identifies, according to MPS table bd.

        Deputies with the same name but different membership are treated as separate
        members (might happen in the event of change of party).
        The idDep is constructed so as to be sufficient to determine uf party and just
        looking at the numbers, it has the syntax: PPPEENNN where PPP is the idPartido,
        EE is the idUF and NNN is a unique number for each name deputy within a party-uf.
        If the Member is not in MPS table bd, he gains a new idDep, is inserted into the table,
        and returns the newly assigned idDep."""

	    # Print Deputado.dicpartidos_inicializado:
        if not Deputado.diclistadeps_inicializado:
            Deputado.inicializar_diclistadeps()
            Deputado.diclistadeps_inicializado = True

	    # This is used when UF makes no sense (ex: câmara municipal):
        iduf = '99'
        if uf:
            iduf = Deputado.idUF(uf)

        idPartUF = '%s%s' % (Deputado.idPartido(partido, bd), iduf)
        idPartUF = int(idPartUF)

        if idPartUF in Deputado.diclistadeps:
            if nome in Deputado.diclistadeps[idPartUF]:
                iddep = idPartUF*1000 + Deputado.diclistadeps[idPartUF].index(nome) + 1
                return iddep

            else:
                Deputado.diclistadeps[idPartUF].append(nome)
                iddep = idPartUF*1000 + Deputado.diclistadeps[idPartUF].index(nome) + 1

        else:
            Deputado.diclistadeps[idPartUF] = [nome]
            iddep = idPartUF*1000 + 1

        con = lite.connect(bd)
        con.execute('INSERT INTO PARLAMENTARES VALUES(?,?,?,?)',(iddep,nome,partido,uf))
        con.commit()
        con.close_tag()

        return iddep



class VotosAgregados:
    """Represents a number of votes
    attributes:
    yes, no, abstention - integers representing the number of votes in the set."""


    def add(self, voto):
        """Adds a set of votes to vote
        Arguments:
        voto -- string \in {SIM, NAO, ABSTENCAO, OBSTRUCAO}
        OBSTRUCAO conta como um voto NAO."""

        increment_by_one = 1

        if (voto == SIM):
          self.sim += increment_by_one
        if (voto == NAO):
          self.nao += increment_by_one
        if (voto == OBSTRUCAO):
          self.nao += increment_by_one
        if (voto == ABSTENCAO):
          self.abstencao += increment_by_one

    def __init__(self):
        """Initializing variables"""

        self.sim = 0
        self.nao = 0
        self.abstencao = 0

    def __unicode__(self):

        return '(%s, %s, %s)' % (self.sim, self.nao, self.abstencao)

    def __str__(self):

        return unicode(self).encode('utf-8')

class VotoPartido(VotosAgregados):
    """Represents a set of votes a party
    attributes:
    yes, no, abstention - integers representing the number of votes in the set
    party - string."""

    def __init__(self, partido):
        """Initializing variables"""

        VotosAgregados.__init__(self)
        self.partido = partido

class VotoUF(VotosAgregados):
    """Represents a set of votes of a UF (state or federal district)
    attributes:
    yes, no, abstention - integers representing the number of votes in the set
    uf - string."""
     
    def __init__(self, uf):
        """Initializing variables"""

        VotosAgregados.__init__(self)
        self.uf = uf


