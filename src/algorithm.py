#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import abstractmethod
from collections import defaultdict
from enum import Enum
import networkx as nx
import functools
import logger


class Algorithm:
    def __init__(self, graph: nx.Graph):
        self._graph = graph
        self.initialise()

    def graph(self):
        return self._graph

    @abstractmethod
    def initialise(self):
        pass

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
        self._mis = set()
        self._candidate_filter = candidate_filter
        super().__init__(graph)

    def initialise(self):
        # self._logger.adjusted(len(self._independent_set))
        self._mis.clear()

        if self._candidate_filter:
            candidates = set(filter(self._candidate_filter, self._graph.nodes))
        else:
            candidates = set(self._graph.nodes)

        while candidates:
            v = candidates.pop()
            self._mis.add(v)
            # self._logger.adjusted()

            for w in self._graph[v]:
                if w in candidates:
                    candidates.remove(w)

    def insert_edge(self, u, v):
        self._graph.add_edge(u, v)
        self.initialise()

    def remove_edge(self, u, v):
        self._graph.remove_edge(u, v)
        self.initialise()

    def insert_node(self, v, edges=[]):
        self._graph.add_node(v)
        self._graph.add_edges_from(edges)
        self.initialise()

    def remove_node(self, v):
        self._graph.remove_node(v)
        self.initialise()

    def is_in_mis(self, node):
        # self._logger.queried()
        return node in self._mis

    def get_mis(self):
        return self._mis


class SimpleMIS(MISAlgorithm):

    def __init__(self, graph):
        self._count = defaultdict(lambda: 0)
        self._mis = set()
        super(SimpleMIS, self).__init__(graph)

    def initialise(self):
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
                if self._decrease_count(w):
                    for x in self._graph[w]:
                        self._increase_count(x)
        self._graph.remove_node(v)

    def insert_edge(self, u, v):
        self._graph.add_edge(u, v)
        if self.is_in_mis(u) and self.is_in_mis(v):
            self._increase_count(u)  # increase_count automatically removes u from _mis set
            for n in self._graph[u]:
                if n != v:
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
        self._light_nodes = {v for v, deg in self._graph.degree if deg < self._delta_c}
        self._heavy_nodes = set(self._graph.nodes).difference(self._light_nodes)

        tmis = TrivialMIS(self._light_subgraph())
        self._light_mis = tmis.get_mis()
        for v in self._light_mis:
            self._calculate_light_count(v)

        self._calculate_heavy_mis()

    def insert_node(self, v, edges=[]):
        self._graph.add_node(v)
        self._graph.add_edges_from(edges)

        if len(edges) < self._delta_c:
            self._add_to_light_nodes(v)
        else:
            self._heavy_nodes.add(v)

        self._calculate_heavy_mis()

    def remove_node(self, v):
        neighbors = set(self._graph[v])
        self._graph.remove_node(v)

        if v in self._light_mis:
            for w in neighbors:
                if w in self._light_nodes:
                    self._decrease_light_count(w)
                else:
                    self._update_node_weight(w)

        self._calculate_heavy_mis()

    def insert_edge(self, u, v):
        self._graph.add_edge(u, v)

        # First check if both nodes remain light
        for n in [u, v]:
            # Node was light and isn't anymore
            if self._graph.degree(n) == self._delta_c:
                self._reset_light_count(n)
                self._update_node_weight(n)  # move from light to heavy set

                if n in self._light_mis:
                    self._light_mis.remove(n)
                    for w in self._graph[n]:
                        self._decrease_light_count(w)
                        self._maybe_add_to_light_mis(w)

        if u in self._light_mis and v in self._light_mis:
            self._remove_from_light_mis(u)
        elif u in self._light_mis != v in self._light_mis:
            non_mis_node = v if u in self._light_mis else v
            if non_mis_node in self._light_nodes:
                self._increase_light_count(non_mis_node)

        self._calculate_heavy_mis()

    def remove_edge(self, u, v):
        if u in self._light_nodes and v in self._light_nodes:
            if u in self._light_mis:
                self._decrease_light_count(v)
            elif v in self._light_mis:
                self._decrease_light_count(u)
        else:
            for n in [u, v]:
                # n becomes a light node:
                if self._graph.degree(n) == self._delta_c - 1:
                    self._add_to_light_nodes(n)

        self._calculate_heavy_mis()

    def _calculate_light_count(self, v):
        self._reset_light_count(v, 0)
        for w in self._graph[v]:
            if w in self._light_mis:
                self._increase_light_count(v)

        self._calculate_heavy_mis()

    def _decrease_light_count(self, v):
        assert(self._graph[v]['light_count'] > 0)
        self._graph.nodes[v]['light_count'] = self._graph.nodes[v]['light_count'] - 1

    def _increase_light_count(self, v):
        self._graph.nodes[v]['light_count'] = self._graph.nodes[v]['light_count'] + 1
        # if v in self._light_mis:
        #     self._light_mis.remove(v)

    def _reset_light_count(self, v, value=None):
        if value:
            self._graph.nodes[v]['light_count'] = value
        else:
            del self._graph.nodes[v]['light_count']

    # Depends on a correct self._light_mis
    def _calculate_heavy_mis(self):
        # allowed returns True if the heavy node can be put into the mis
        def allowed(light_mis: set, graph: nx.Graph, node):
            return light_mis.isdisjoint(graph[node])

        cf = functools.partial(allowed, self._light_mis)
        self._heavy_mis = TrivialMIS(self._heavy_subgraph(), candidate_filter=cf).get_mis()

    def _update_node_weight(self, v):
        if self._graph.degree(v) < self._delta_c:
            if v not in self._light_nodes:
                self._add_to_light_nodes(v)
                self._heavy_nodes.remove(v)
        else:
            if v not in self._heavy_nodes:
                self._heavy_nodes.add(v)
                self._light_nodes.remove(v)

    def _add_to_light_nodes(self, v):
        self._light_nodes.add(v)
        self._calculate_light_count(v)
        self._maybe_add_to_light_mis(v)  # maybe not a good spot to do here

    def _add_to_light_mis(self, v):
        assert(v in self._light_nodes and self._graph.nodes[v]['light_count'] == 0)

        self._light_mis.add(v)
        for w in self._graph[v]:
            if w in self._light_nodes:
                self._increase_light_count(w)

    def _maybe_add_to_light_mis(self, v):
        if self._graph.nodes[v]['light_count'] == 0:
            self._add_to_light_mis(v)

    def _remove_from_light_mis(self, v):
        assert v in self._light_mis
        self._light_mis.remove(v)
        for w in self._graph[v]:
            if w in self._light_nodes:
                self._decrease_light_count(w)
                self._maybe_add_to_light_mis(w)

    def _light_subgraph(self):
        return self._graph.subgraph(self._light_nodes)

    def _heavy_subgraph(self):
        heavy_nodes = [v for v, degr in self._graph.degree if degr >= self._delta_c]
        return self._graph.subgraph(heavy_nodes)

    def is_in_mis(self, node):
        return node in self._light_mis or node in self._heavy_mis

    def get_mis(self):
        return set.union(self._light_mis, self._heavy_mis)
