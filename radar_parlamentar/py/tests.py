#!/usr/bin/python
# -*- coding: utf-8 -*-

from model import Deputado
from model import Votacao
from model import Proposicao
import model
import partidos
import algebra
import unittest

class CamaraWS_Test(unittest.TestCase):

  def test_vetor_votacoes(self): 
    '''tests the generation of an array of polls'''

    # Tested polls (s,n,a):
    # (9,0,0) 
    # (0,8,1) 
    # (7,1,1) 
    # (3,3,3) 

    partido = 'arena'
    votacoes = []

    depSim = Deputado()
    depSim.partido = partido
    depSim.voto = model.SIM 
    depNao = Deputado()
    depNao.partido = partido
    depNao.voto = model.NAO
    depAbs = Deputado()
    depAbs.partido = partido
    depAbs.voto = model.ABSTENCAO 

    # First grade:

    vot = Votacao()
    for i in range(0,9):
      vot.deputados.append(depSim)
    votacoes.append(vot)

    # Second grade::

    vot = Votacao()
    for i in range(0,8):
      vot.deputados.append(depNao)
    vot.deputados.append(depAbs)
    votacoes.append(vot)

    # Third grade:

    vot = Votacao()
    for i in range(0,7):
      vot.deputados.append(depSim)
    vot.deputados.append(depNao)
    vot.deputados.append(depAbs)
    votacoes.append(vot)

    # Fourth voting:

    vot = Votacao()
    for i in range(0,3):
      vot.deputados.append(depSim)
    for i in range(0,3):
      vot.deputados.append(depNao)
    for i in range(0,3):
      vot.deputados.append(depAbs)
    votacoes.append(vot)

    proposicao = Proposicao()
    proposicao.votacoes = votacoes
    proposicoes = [proposicao]
  
    # Tested by invoking the function:

    vetor = partidos.vetor_votacoes(partido, proposicoes)

    # If testing is right:

    expected = [1, -0.88889, 0.66667, 0]
    self.assertEqual(len(expected), len(vetor))
    for e, v in zip(expected, vetor):
      self.assertAlmostEqual(e, v, 5)

  def test_norma(self):
    '''tests the function that returns the norm of the vector'''
    
    # Input:

    v1 = [1, 0.8, 0.2, 0.5]
    v2 = [1, 0.7, 0.1, 0.6]
    v3 = [0, 0.2, 0.8, 0.2]
    
    self.assertAlmostEqual(1.389244399 , algebra.norma(v1), 5)
    self.assertAlmostEqual(1.36381817 , algebra.norma(v2), 5)
    self.assertAlmostEqual(0.848528137 , algebra.norma(v3), 5)

  def test_normalizacao(self):

    # Input:

    v1 = [1, 0.8, 0.2, 0.5]
    v2 = [1, 0.7, 0.1, 0.6]
    v3 = [0, 0.2, 0.8, 0.2]

    # Expected results:

    nv1 = [0.719815751, 0.575852601, 0.14396315, 0.359907875]
    nv2 = [0.733235575, 0.513264902, 0.073323557, 0.439941345]
    nv3 = [0, 0.235702261, 0.942809042, 0.235702261]

    for e, v in zip(nv1, algebra.normaliza(v1)):
      self.assertAlmostEqual(e, v, 5)
    for e, v in zip(nv2, algebra.normaliza(v2)):
      self.assertAlmostEqual(e, v, 5)
    for e, v in zip(nv3, algebra.normaliza(v3)):
      self.assertAlmostEqual(e, v, 5)

  def test_prod_escalar(self):

    # Input:

    nv1 = [0.719815751, 0.575852601, 0.14396315, 0.359907875]
    nv2 = [0.733235575, 0.513264902, 0.073323557, 0.439941345]
    nv3 = [0, 0.235702261, 0.942809042, 0.235702261]
  
    self.assertAlmostEqual(0.99225369 , algebra.prod_escalar(nv1,nv2), 5)
    self.assertAlmostEqual(0.356290619 , algebra.prod_escalar(nv1,nv3), 5)
    self.assertAlmostEqual(0.29380298 , algebra.prod_escalar(nv2,nv3), 5)

  def test_semelhanca_vetores(self):
    '''testa a função de semelhança entre vetores'''

    # Input:

    v1 = [1, 0.8, 0.2, 0.5]
    v2 = [1, 0.7, 0.1, 0.6]
    v3 = [0, 0.2, 0.8, 0.2]

    # Results obtained:

    s12 = partidos.semelhanca_vetores(v1,v2)
    s13 = partidos.semelhanca_vetores(v1,v3)
    s23 = partidos.semelhanca_vetores(v2,v3)

    # Expected results:

    e12 = 0.99225369
    e13 = 0.356290619
    e23 = 0.29380298

    # Comparing:

    self.assertAlmostEqual(e12, s12, 5)
    self.assertAlmostEqual(e13, s13, 5)
    self.assertAlmostEqual(e23, s23, 5)

    # The resemblance is commutative:

    s21 = partidos.semelhanca_vetores(v2,v1)
    s31 = partidos.semelhanca_vetores(v3,v1)
    s32 = partidos.semelhanca_vetores(v3,v2)
    self.assertAlmostEqual(s12, s21, 5)
    self.assertAlmostEqual(s13, s31, 5)
    self.assertAlmostEqual(s23, s32, 5)

  def test_semelhanca_partidos(self):
    '''Tests the function of similarity for parties'''

    partido1 = 'girondinos'
    partido2 = 'jacobinos'
    votacoes = []

    # Votations of the test:
    # v1: p1(3,0,0) p2(0,3,0)
    # v2: p1(0,2,1) p2(2,0,1)
    # v3: p1(3,0,0) p2(0,2,1)

    dep1Sim = Deputado()
    dep1Sim.partido = partido1
    dep1Sim.voto = model.SIM 
    dep1Nao = Deputado()
    dep1Nao.partido = partido1
    dep1Nao.voto = model.NAO
    dep1Abs = Deputado()
    dep1Abs.partido = partido1
    dep1Abs.voto = model.ABSTENCAO 
    dep2Sim = Deputado()
    dep2Sim.partido = partido2
    dep2Sim.voto = model.SIM 
    dep2Nao = Deputado()
    dep2Nao.partido = partido2
    dep2Nao.voto = model.NAO
    dep2Abs = Deputado()
    dep2Abs.partido = partido2
    dep2Abs.voto = model.ABSTENCAO 

    # First grade:

    vot = Votacao()
    vot.deputados.append(dep1Sim)
    vot.deputados.append(dep1Sim)
    vot.deputados.append(dep1Sim)
    vot.deputados.append(dep2Nao)
    vot.deputados.append(dep2Nao)
    vot.deputados.append(dep2Nao)
    votacoes.append(vot)

    # Second grade:

    vot = Votacao()
    vot.deputados.append(dep1Nao)
    vot.deputados.append(dep1Nao)
    vot.deputados.append(dep1Abs)
    vot.deputados.append(dep2Sim)
    vot.deputados.append(dep2Sim)
    vot.deputados.append(dep2Abs)
    votacoes.append(vot)

    # Third grade:

    vot = Votacao()
    vot.deputados.append(dep1Sim)
    vot.deputados.append(dep1Sim)
    vot.deputados.append(dep1Sim)
    vot.deputados.append(dep2Nao)
    vot.deputados.append(dep2Nao)
    vot.deputados.append(dep2Abs)
    votacoes.append(vot)

    proposicao = Proposicao()
    proposicao.votacoes = votacoes

    proposicoes = [proposicao]

    # Tested by invoking the function:

    s = partidos.semelhanca(partido1, partido2, proposicoes)

    # If testing is right;
    # Calculating on hand:

    expected = 0.008766487 
    self.assertAlmostEqual(expected, s, 5)

if __name__ == '__main__':
  unittest.main()

