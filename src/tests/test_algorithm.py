import unittest
from unittest.mock import MagicMock, patch
import networkx as nx
from algorithm import *


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


# Test remove node functionality
def _helper_explicit_remove_node(test, cls):
    g = nx.gnp_random_graph(20, 0.3, seed=1234)
    inst = cls(g)

    test.assertTrue(inst.is_valid_mis())

    size_before = len(inst.get_mis())
    v = list(inst.get_mis())[0]
    inst.remove_node(v)

    test.assertTrue(inst.is_valid_mis())
    # test.assertEqual(size_before - 1, len(inst.get_mis()))


class TestTrivialMIS(unittest.TestCase):

    def test_valid(self):
        g = nx.gnp_random_graph(20, 0.3, seed=1234)
        tmis = TrivialMIS(g)
        self.assertTrue(tmis.is_valid_mis())

    def test_remove_node(self):
        _helper_explicit_remove_node(self, TrivialMIS)


class TestSimpleMIS(unittest.TestCase):

    def test_valid(self):
        g = nx.gnp_random_graph(20, 0.3, seed=1234)
        sm = SimpleMIS(g)
        self.assertTrue(sm.is_valid_mis())

    def test_remove_node(self):
        _helper_explicit_remove_node(self, SimpleMIS)

class TestImprovedIncrementalMIS(unittest.TestCase):

    def test_valid(self):
        g = nx.gnp_random_graph(20, 0.3, seed=1234)
        sm = SimpleMIS(g)
        self.assertTrue(sm.is_valid_mis())

    def test_remove_node(self):
        _helper_explicit_remove_node(self, SimpleMIS)
