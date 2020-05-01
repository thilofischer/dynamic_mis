#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import abstractmethod
from collections import defaultdict
import networkx as nx
import functools


class Algorithm:
    def __init__(self, graph: nx.Graph):
        self._graph = graph

    def graph(self):
        return self._graph

    @abstractmethod
    def insert_edge(self, u, v):
        pass

    @abstractmethod
    def remove_edge(self, u, v):
        pass

    @abstractmethod
    def insert_node(self, v, edges):
        pass

    @abstractmethod
    def remove_node(self, v):
        pass


class MISAlgorithm(Algorithm):

    @abstractmethod
    def is_in_mis(self, node):
        pass

    @abstractmethod
    def get_mis(self):
        pass

    def is_valid_mis(self):
        for u, v in self._graph.edges:
            if self.is_in_mis(u) and self.is_in_mis(v):
                return False

        for v in self._graph.nodes:
            neighbor_in_mis = False
            for w in self._graph[v]:
                neighbor_in_mis |= self.is_in_mis(w)
            if not neighbor_in_mis and not self.is_in_mis(v):
                return False

        return True

    def get_state(self):
        return set(self._graph.nodes), self.get_mis(), set(self._graph.edges)


class TrivialMIS(MISAlgorithm):

    def __init__(self, graph, candidate_filter=None):
        super(TrivialMIS, self).__init__(graph)
        self._mis = set()
        self._candidate_filter = candidate_filter
        self._compute()

    def _compute(self):
        # self._logger.adjusted(len(self._independent_set))
        self._mis.clear()

        if self._candidate_filter:
            candidates = set(filter(self._candidate_filter, self._graph.nodes))
        else:
            candidates = set(self._graph.nodes)

        while candidates:
            v = candidates.pop()
            self._mis.add(v)
            for w in self._graph[v]:
                if w in candidates:
                    candidates.remove(w)

    def insert_edge(self, u, v):
        self._graph.add_edge(u, v)
        self._compute()

    def remove_edge(self, u, v):
        self._graph.remove_edge(u, v)
        self._compute()

    def insert_node(self, v, edges=[]):
        self._graph.add_node(v)
        # FIXME: filter edges so nodes don't get created as a byproduct
        self._graph.add_edges_from(edges)
        self._compute()

    def remove_node(self, v):
        self._graph.remove_node(v)
        self._compute()

    def is_in_mis(self, node):
        # self._logger.queried()
        return node in self._mis

    def get_mis(self):
        return self._mis


class SimpleMIS(MISAlgorithm):

    def __init__(self, graph):
        super(SimpleMIS, self).__init__(graph)
        self._count = defaultdict(lambda: 0)
        tmis = TrivialMIS(self._graph)
        self._mis = tmis.get_mis()

        for u, v in self._graph.edges:
            if tmis.is_in_mis(u):
                self._increase_count(v)
            elif tmis.is_in_mis(v):
                self._increase_count(u)

    def insert_node(self, v, edges=[]):
        # reset count to protect against re-insertion bugs
        self._count[v] = 0
        self._graph.add_node(v)

        # check that node is already in graph: else networkx will create that node and we don't want that
        def both_nodes_exist(e):
            return self._graph.has_node(e[0]) and self._graph.has_node(e[1])

        edges = filter(both_nodes_exist, edges)
        self._graph.add_edges_from(edges)

        for n in self._graph[v]:
            if self.is_in_mis(n):
                self._increase_count(v)

        if self._count[v] == 0:
            self._mis.add(v)
            for n in self._graph[v]:
                assert(not self.is_in_mis(n))
                self._increase_count(n)

    def remove_node(self, v):
        if self.is_in_mis(v):
            self._mis.remove(v)
            for w in self._graph[v]:
                # FIXME: same loop
                if self._decrease_count(w):
                    for x in self._graph[w]:
                        self._increase_count(x)

        self._graph.remove_node(v)

    def insert_edge(self, u, v):
        assert u in self._graph and v in self._graph
        self._graph.add_edge(u, v)
        if self.is_in_mis(u) and self.is_in_mis(v):
            self._increase_count(u)  # increase_count automatically removes u from _mis set
            for n in self._graph[u]:
                if n != v:
                    # FIXME: same loop
                    if self._decrease_count(n):
                        for x in self._graph[n]:
                            self._increase_count(x)

        elif self.is_in_mis(u) != self.is_in_mis(v):
            non_mis_node = v if self.is_in_mis(u) else u
            self._increase_count(non_mis_node)

    def remove_edge(self, u, v):
        if self.is_in_mis(u) or self.is_in_mis(v):
            mis_node, non_mis_node = (v, u) if self.is_in_mis(v) else (u, v)
            if self._decrease_count(non_mis_node):
                for w in self._graph[non_mis_node]:
                    # FIXME: is this if needed here? otherwise the loop can be generalized
                    if w != mis_node:
                        self._increase_count(w)

        self._graph.remove_edge(u, v)

    def _decrease_count(self, v):
        assert(self._count[v] > 0)
        self._count[v] = self._count[v] - 1
        if self._count[v] == 0:
            self._mis.add(v)
            return True
        else:
            return False

    def _increase_count(self, v):
        self._count[v] = self._count[v] + 1
        if v in self._mis:
            self._mis.remove(v)
            return True
        else:
            return False

    def is_in_mis(self, node):
        return node in self._mis

    def get_mis(self):
        return self._mis


class ImprovedIncrementalMIS(SimpleMIS):

    def insert_edge(self, u, v):
        lower_deg, higher_deg = (u, v) if self._graph.degree(u) < self._graph.degree(v) else (v, u)
        super(ImprovedIncrementalMIS, self).insert_edge(lower_deg, higher_deg)

    def remove_node(self, v):
        raise NotImplementedError

    def remove_edge(self, u, v):
        raise NotImplementedError


class ImprovedDynamicMIS(MISAlgorithm):

    def __init__(self, graph: nx.Graph, delta_c: int):
        super(ImprovedDynamicMIS, self).__init__(graph)
        self._delta_c = delta_c
        light_nodes = {v for (v, deg) in graph.degree if deg < self._delta_c}

        self._light_subgraph = nx.Graph(graph.subgraph(light_nodes))
        self._light_algo = SimpleMIS(self._light_subgraph)

        self._heavy_mis = set()
        self._compute_heavy_mis()

    def insert_edge(self, u, v):
        made_heavy = False
        for n in [u, v]:
            if self._graph.degree[n] == self._delta_c - 1:
                self._light_algo.remove_node(n)
                made_heavy |= True

        if not made_heavy and u in self._light_subgraph and v in self._light_subgraph:
            self._light_algo.insert_edge(u, v)

        self._graph.add_edge(u, v)
        self._compute_heavy_mis()

    def remove_edge(self, u, v):
        if u in self._light_subgraph and v in self._light_subgraph:
            self._light_algo.remove_edge(u, v)

        self._graph.remove_edge(u, v)
        self._check_became_light([u, v])
        self._compute_heavy_mis()

    def remove_node(self, v):
        if v in self._light_subgraph:
            self._light_algo.remove_node(v)

        neighbors = set(self._graph[v])
        self._graph.remove_node(v)
        self._check_became_light(neighbors)
        self._compute_heavy_mis()

    def insert_node(self, v, edges=[]):
        self._graph.add_node(v)

        # check that both nodes are already in graph: else networkx will create that node and we don't want that
        # needs to be done first so the len(edges) value is correct to classify the node as light/heavy
        def both_nodes_exist(e):
            return self._graph.has_node(e[0]) and self._graph.has_node(e[1])
        edges = list(filter(both_nodes_exist, edges))
        self._graph.add_edges_from(edges)

        if len(edges) < self._delta_c:
            self._light_algo.insert_node(v, edges)
            self._check_became_heavy(set(self._light_subgraph[v]))

        self._compute_heavy_mis()

    def _check_became_light(self, nodes):
        for n in nodes:
            # Node just became light
            if self._graph.degree(n) == self._delta_c - 1:
                self._light_algo.insert_node(n, self._graph.edges(n))

    def _check_became_heavy(self, nodes):
        for n in nodes:
            # Node just became heavy
            if self._light_subgraph.degree(n) == self._delta_c:
                self._light_algo.remove_node(n)

    def _compute_heavy_mis(self):
        # allowed returns True if the heavy node can be put into the mis
        def allowed(light_mis: set, graph: nx.Graph, node):
            return light_mis.isdisjoint(graph[node])

        cf = functools.partial(allowed, self._light_algo.get_mis(), self._graph)
        self._heavy_mis = TrivialMIS(self._graph, candidate_filter=cf).get_mis()

    def _valid_node_partition(self):
        for v in self._graph.nodes:
            if self._graph.degree[v] < self._delta_c:
                if v not in self._light_subgraph:
                    return False
        return True

    def is_valid_mis(self):
        valid_partition = self._valid_node_partition()
        return valid_partition and super(ImprovedDynamicMIS, self).is_valid_mis()

    def is_in_mis(self, node):
        return node in self._heavy_mis or self._light_algo.is_in_mis(node)

    def get_mis(self):
        return set.union(self._heavy_mis, self._light_algo.get_mis())
