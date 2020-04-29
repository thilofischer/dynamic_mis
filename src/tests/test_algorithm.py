import unittest
from unittest.mock import MagicMock, patch
import networkx as nx
from typing import Type
import numpy as np
from algorithm import *
from visualize import *


class TestIsValidMIS(unittest.TestCase):

    @patch.object(SimpleMIS, 'is_in_mis')
    def test_neighbors_in_mis(self, mock_is_in_mis):
        graph = nx.Graph()
        graph.add_nodes_from([1, 2])
        graph.add_edge(1, 2)

        mock_is_in_mis.return_value = True

        srm = SimpleMIS(graph)

        self.assertFalse(srm.is_valid_mis())

    @patch.object(SimpleMIS, 'is_in_mis')
    def test_empty_is(self, mock_is_in_mis):
        graph = nx.Graph()
        graph.add_nodes_from([1, 2])

        mock_is_in_mis.return_value = False
        srm = SimpleMIS(graph)

        self.assertFalse(srm.is_valid_mis())

    @patch.object(SimpleMIS, 'is_in_mis')
    def test_valid_mis(self, mock_is_in_mis):
        graph = nx.Graph()
        graph.add_nodes_from([1, 2])

        mock_is_in_mis.return_value = True
        srm = SimpleMIS(graph)

        self.assertTrue(srm.is_valid_mis())

    @patch.object(SimpleMIS, 'is_in_mis')
    def test_non_maximal(self, mock_is_in_mis):
        graph = nx.Graph()
        graph.add_nodes_from([1, 2])

        # Only node 1 is in MIS but 2 could be also
        mock_is_in_mis.side_effect = lambda v: v == 1
        srm = SimpleMIS(graph)

        self.assertFalse(srm.is_valid_mis())


class TestTrivialMIS(unittest.TestCase):

    def test_valid(self):
        g = nx.gnp_random_graph(20, 0.3, seed=1234)
        tmis = TrivialMIS(g)
        self.assertTrue(tmis.is_valid_mis())

    def test_remove_nodes(self):
        _test_remove_nodes(self, TrivialMIS)

    def test_remove_edges(self):
        _test_remove_edges(self, TrivialMIS)


class TestSimpleMIS(unittest.TestCase):

    def test_valid(self):
        g = nx.gnp_random_graph(20, 0.3, seed=1234)
        sm = SimpleMIS(g)
        self.assertTrue(sm.is_valid_mis())

    def test_remove_nodes(self):
        _test_remove_nodes(self, SimpleMIS)

    def test_remove_edges(self):
        _test_remove_edges(self, SimpleMIS)

class TestImprovedIncrementalMIS(unittest.TestCase):

    def test_valid(self):
        g = nx.gnp_random_graph(20, 0.3, seed=1234)
        sm = SimpleMIS(g)
        self.assertTrue(sm.is_valid_mis())


def _test_remove_nodes(test: unittest.TestCase, cls: Type[MISAlgorithm]):
    g = nx.gnp_random_graph(20, 0.3, seed=42)
    removal_order = np.random.RandomState(seed=42).permutation(g.nodes)
    algo = cls(g)

    test.assertTrue(algo.is_valid_mis())

    for n in removal_order:
        algo.remove_node(n)
        test.assertFalse(n in g.nodes)
        test.assertTrue(algo.is_valid_mis())


def _test_remove_edges(test: unittest.TestCase, cls: Type[MISAlgorithm]):
    g = nx.gnp_random_graph(5, 0.3, seed=42)
    removal_order = np.random.RandomState(seed=42).permutation(g.edges)
    algo = cls(g)

    history = []

    test.assertTrue(algo.is_valid_mis())

    for e in removal_order:
        algo.remove_edge(*e)
        history.append(algo.get_state())
        test.assertFalse(e in g.edges)
        test.assertTrue(algo.is_valid_mis())

    # animate(*zip(*history))
