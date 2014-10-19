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
    """Tests the generation of an array of polls."""

    # Tested polls (s,n,a):
    # (9,0,0) 
    # (0,8,1) 
    # (7,1,1) 
    # (3,3,3) 
    party = 'arena'
    votings = []

    deputy_vote_yes = Deputado()
    deputy_vote_yes.partido = party
    deputy_vote_yes.voto = model.SIM
    deputy_vote_no = Deputado()
    deputy_vote_no.partido = party
    deputy_vote_no.voto = model.NAO
    depute_vote_abstention = Deputado()
    depute_vote_abstention.partido = party
    depute_vote_abstention.voto = model.ABSTENCAO

    # First grade:
    vote = Votacao()
    for i in range(0,9):
      vote.deputados.append(deputy_vote_yes)
    votings.append(vote)

    # Second grade::
    vote = Votacao()
    for i in range(0,8):
      vote.deputados.append(deputy_vote_no)
    vote.deputados.append(depute_vote_abstention)
    votings.append(vote)

    # Third grade:
    vote = Votacao()
    for i in range(0,7):
      vote.deputados.append(deputy_vote_yes)
    vote.deputados.append(deputy_vote_no)
    vote.deputados.append(depute_vote_abstention)
    votings.append(vote)

    # Fourth voting:
    vote = Votacao()
    for i in range(0,3):
      vote.deputados.append(deputy_vote_yes)
    for i in range(0,3):
      vote.deputados.append(deputy_vote_no)
    for i in range(0,3):
      vote.deputados.append(depute_vote_abstention)
    votings.append(vote)

    proposition = Proposicao()
    proposition.votacoes = votings
    propositions = [proposition]
  
    # Tested by invoking the function:
    vector = partidos.votings_vector(party, propositions)

    # If testing is right:
    expected = [1, -0.88889, 0.66667, 0]
    self.assertEqual(len(expected), len(vector))
    for e, v in zip(expected, vector):
      self.assertAlmostEqual(e, v, 5)

  def test_norma(self):
    """ Tests the function that returns the norm of the vector."""
    
    # Input:

    vector_test1 = [1, 0.8, 0.2, 0.5]
    vector_test2 = [1, 0.7, 0.1, 0.6]
    vector_test3 = [0, 0.2, 0.8, 0.2]
    
    self.assertAlmostEqual(1.389244399 , algebra.calculate_vector_size(vector_test1), 5)
    self.assertAlmostEqual(1.36381817 , algebra.calculate_vector_size(vector_test2), 5)
    self.assertAlmostEqual(0.848528137 , algebra.calculate_vector_size(vector_test3), 5)

  def test_normalizacao(self):

    # Input:
    vector_test1 = [1, 0.8, 0.2, 0.5]
    vector_test2 = [1, 0.7, 0.1, 0.6]
    vector_teste3 = [0, 0.2, 0.8, 0.2]

    # Expected results:
    nv1 = [0.719815751, 0.575852601, 0.14396315, 0.359907875]
    nv2 = [0.733235575, 0.513264902, 0.073323557, 0.439941345]
    nv3 = [0, 0.235702261, 0.942809042, 0.235702261]

    for e, v in zip(nv1, algebra.normalize_vector(vector_test1)):
      self.assertAlmostEqual(e, v, 5)
    for e, v in zip(nv2, algebra.normalize_vector(vector_test2)):
      self.assertAlmostEqual(e, v, 5)
    for e, v in zip(nv3, algebra.normalize_vector(vector_teste3)):
      self.assertAlmostEqual(e, v, 5)

  def test_prod_escalar(self):

    # Input:
    nv1 = [0.719815751, 0.575852601, 0.14396315, 0.359907875]
    nv2 = [0.733235575, 0.513264902, 0.073323557, 0.439941345]
    nv3 = [0, 0.235702261, 0.942809042, 0.235702261]
  
    self.assertAlmostEqual(0.99225369 , algebra.calculate_scalar_product(nv1,nv2), 5)
    self.assertAlmostEqual(0.356290619 , algebra.calculate_scalar_product(nv1,nv3), 5)
    self.assertAlmostEqual(0.29380298 , algebra.calculate_scalar_product(nv2,nv3), 5)

  def test_semelhanca_vetores(self):
    """ Testing the similarity between feature vectors."""

    # Input:
    vector_test1 = [1, 0.8, 0.2, 0.5]
    vector_test2 = [1, 0.7, 0.1, 0.6]
    vector_test3 = [0, 0.2, 0.8, 0.2]

    # Results obtained:
    similarity_vector_1_and_2 = partidos.vectors_similarity(vector_test1,vector_test2)
    similarity_vector_1_and_3 = partidos.vectors_similarity(vector_test1,vector_test3)
    similarity_vector_2_and_3 = partidos.vectors_similarity(vector_test2,vector_test3)

    # Expected results:
    expected_result_1_2 = 0.99225369
    expected_result_1_3 = 0.356290619
    expected_result_2_3 = 0.29380298

    # Comparing:
    self.assertAlmostEqual(expected_result_1_2, similarity_vector_1_and_2, 5)
    self.assertAlmostEqual(expected_result_1_3, similarity_vector_1_and_3, 5)
    self.assertAlmostEqual(expected_result_2_3, similarity_vector_2_and_3, 5)

    # The resemblance is commutative:
    similarity_vector_2_and_1 = partidos.vectors_similarity(vector_test2,vector_test1)
    similarity_vector_3_and_1 = partidos.vectors_similarity(vector_test3,vector_test1)
    similarity_vector_3_and_2 = partidos.vectors_similarity(vector_test3,vector_test2)
    self.assertAlmostEqual(similarity_vector_1_and_2, similarity_vector_2_and_1, 5)
    self.assertAlmostEqual(similarity_vector_1_and_3, similarity_vector_3_and_1, 5)
    self.assertAlmostEqual(similarity_vector_2_and_3, similarity_vector_3_and_2, 5)

  def test_semelhanca_partidos(self):
    """ Tests the function of similarity for political partidos."""

    party1 = 'girondinos'
    party2 = 'jacobinos'
    votings = []

    # Votations of the test:
    # v1: p1(3,0,0) p2(0,3,0)
    # v2: p1(0,2,1) p2(2,0,1)
    # v3: p1(3,0,0) p2(0,2,1)
    dep1Sim = Deputado()
    dep1Sim.partido = party1
    dep1Sim.voto = model.SIM 
    dep1Nao = Deputado()
    dep1Nao.partido = party1
    dep1Nao.voto = model.NAO
    dep1Abs = Deputado()
    dep1Abs.partido = party1
    dep1Abs.voto = model.ABSTENCAO 
    dep2Sim = Deputado()
    dep2Sim.partido = party2
    dep2Sim.voto = model.SIM 
    dep2Nao = Deputado()
    dep2Nao.partido = party2
    dep2Nao.voto = model.NAO
    dep2Abs = Deputado()
    dep2Abs.partido = party2
    dep2Abs.voto = model.ABSTENCAO 

    # First grade:
    vot = Votacao()
    vot.deputados.append(dep1Sim)
    vot.deputados.append(dep1Sim)
    vot.deputados.append(dep1Sim)
    vot.deputados.append(dep2Nao)
    vot.deputados.append(dep2Nao)
    vot.deputados.append(dep2Nao)
    votings.append(vot)

    # Second grade:
    vot = Votacao()
    vot.deputados.append(dep1Nao)
    vot.deputados.append(dep1Nao)
    vot.deputados.append(dep1Abs)
    vot.deputados.append(dep2Sim)
    vot.deputados.append(dep2Sim)
    vot.deputados.append(dep2Abs)
    votings.append(vot)

    # Third grade:
    vot = Votacao()
    vot.deputados.append(dep1Sim)
    vot.deputados.append(dep1Sim)
    vot.deputados.append(dep1Sim)
    vot.deputados.append(dep2Nao)
    vot.deputados.append(dep2Nao)
    vot.deputados.append(dep2Abs)
    votings.append(vot)

    proposition = Proposicao()
    proposition.votacoes = votings

    propositions = [proposition]

    # Tested by invoking the function:
    s = partidos.similarity(party1, party2, propositions)

    # If testing is right;
    # Calculating on hand:
    expected = 0.008766487 
    self.assertAlmostEqual(expected, s, 5)

if __name__ == '__main__':
  unittest.main()

