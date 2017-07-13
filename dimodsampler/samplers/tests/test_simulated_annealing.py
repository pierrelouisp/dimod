import unittest

import itertools
import random

from dimodsampler import SimulatedAnnealingSampler, ising_energy
from dimodsampler.samplers.simulated_annealing import ising_simulated_annealing, greedy_coloring
from dimodsampler.samplers.tests.generic_sampler_tests import TestSolverAPI


class TestSASampler(unittest.TestCase, TestSolverAPI):
    def setUp(self):
        self.sampler = SimulatedAnnealingSampler()

    def test_basic(self):

        sampler = self.sampler

        h = {0: -.5, 1: 0, 2: 1, 3: -.5}
        J = {(0, 2): -1, (1, 2): -1, (0, 3): .5, (1, 3): -1}

        response0 = sampler.sample_ising(h, J, n_samples=10, multiprocessing=False)
        response1 = sampler.sample_ising(h, J, n_samples=10, multiprocessing=True)

        # make sure we actully got back 100 samples
        self.assertEqual(len(response0), 10)
        self.assertEqual(len(response1), 10)

        response2 = sampler.sample_structured_ising(h, J, n_samples=10, multiprocessing=False)
        response3 = sampler.sample_structured_ising(h, J, n_samples=10, multiprocessing=True)
        self.assertEqual(len(response2), 10)
        self.assertEqual(len(response3), 10)

        Q = {(0, 0): 0, (1, 1): 0, (0, 1): -1}

        response4 = sampler.sample_qubo(Q, n_samples=10, multiprocessing=False)
        response5 = sampler.sample_qubo(Q, n_samples=10, multiprocessing=True)
        self.assertEqual(len(response4), 10)
        self.assertEqual(len(response5), 10)

        response6 = sampler.sample_structured_qubo(Q, n_samples=10, multiprocessing=False)
        response7 = sampler.sample_structured_qubo(Q, n_samples=10, multiprocessing=True)
        self.assertEqual(len(response6), 10)
        self.assertEqual(len(response7), 10)


class TestSimulatedAnnealingAlgorithm(unittest.TestCase):
    def test_ising_simulated_annealing_basic(self):
        # AND gate
        h = {0: -.5, 1: 0, 2: 1, 3: -.5}
        J = {(0, 2): -1, (1, 2): -1, (0, 3): .5, (1, 3): -1}

        sample, energy = ising_simulated_annealing(h, J)

        self.assertIsInstance(sample, dict)
        self.assertIsInstance(energy, float)

        # make sure all of the nodes are present in sample
        for v in range(4):
            self.assertIn(v, sample)

    def test_ising_simulated_annealing_empty_J(self):
        h = {0: -1, 1: 1, 2: -.5}
        J = {}
        sample, energy = ising_simulated_annealing(h, J)

        self.assertIsInstance(sample, dict)
        self.assertIsInstance(energy, float)

        # make sure all of the nodes are present in sample
        for v in range(3):
            self.assertIn(v, sample)

    def test_ising_simulated_annealing_sample_quality(self):
        # because simulated annealing has randomness, we cannot
        # really test that it finds the solution. So instead we
        # note that it should return better than average solutions
        # so if we test the returned energy against the energy of
        # 100 random samples, it should do better than the average
        nV = 100  # number of variables in h,J
        nS = 100  # number of samples

        h = {v: random.uniform(-2, 2) for v in range(nV)}
        J = {}
        for u, v in itertools.combinations(h, 2):
            if random.random() < .05:
                J[(u, v)] = random.uniform(-1, 1)

        random_energies = [ising_energy(h, J, {v: random.choice((-1, 1)) for v in h})
                           for __ in range(nS)]

        average_energy = sum(random_energies) / float(nS)

        sample, energy = ising_simulated_annealing(h, J)

        self.assertLess(energy, average_energy)

    def test_greedy_coloring(self):
        # set up an adjacency matrix

        N = 100  # number of nodes

        adj = {node: set() for node in range(N)}

        # add randomly approximately 5% of the edges
        for u, v in itertools.combinations(range(N), 2):
            if random.random() < .05:
                adj[u].add(v)
                adj[v].add(u)

        # add one disconnected node
        adj[N] = set()

        # run
        coloring, colors = greedy_coloring(adj)

        # check output types
        self.assertIsInstance(coloring, dict)
        self.assertIsInstance(colors, dict)

        # we want to check that coloring and colors agree
        for v, c in coloring.items():
            self.assertIn(v, colors[c])
        for c, nodes in colors.items():
            for v in nodes:
                self.assertEqual(c, coloring[v])

        # next we want to make sure that no two neighbors share the same color
        for v in adj:
            for u in adj[v]:
                self.assertNotEqual(coloring[u], coloring[v])
