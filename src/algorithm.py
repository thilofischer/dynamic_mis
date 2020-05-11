#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import abstractmethod
from collections import defaultdict
import networkx as nx
from utility import filtered_edge_insert


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
        filtered_edge_insert(self._graph, edges)
        self._compute()

    def remove_node(self, v):
        self._graph.remove_node(v)
        self._compute()

    def is_in_mis(self, node):
        return node in self._mis

    def get_mis(self):
        return self._mis


class SimpleMIS(MISAlgorithm):

    def __init__(self, graph, count=None):
        super(SimpleMIS, self).__init__(graph)

        if count is None:
            self._count = defaultdict(lambda: 0)
        else:
            self._count = count

        tmis = TrivialMIS(self._graph)
        self._mis = tmis.get_mis()

        for u, v in self._graph.edges:
            if tmis.is_in_mis(u):
                self._increase_count(v)
            elif tmis.is_in_mis(v):
                self._increase_count(u)

    def insert_node(self, v, edges=[], count=None):
        self._graph.add_node(v)

        filtered_edge_insert(self._graph, edges)

        if count is None:
            self._count[v] = 0
            for n in self._graph[v]:
                if self.is_in_mis(n):
                    self._increase_count(v)
        else:
            self._count[v] = count

        if self._count[v] == 0:
            self._mis.add(v)
            for n in self._graph[v]:
                assert(not self.is_in_mis(n))
                self._increase_count(n)

    def remove_node(self, v):
        if self.is_in_mis(v):
            self._mis.remove(v)
            for w in self._graph[v]:
                self._decrease_count(w)

        self._graph.remove_node(v)

    def insert_edge(self, u, v):
        assert u in self._graph and v in self._graph
        self._graph.add_edge(u, v)
        if self.is_in_mis(u) and self.is_in_mis(v):
            self._increase_count(u)  # increase_count automatically removes u from _mis set
            for n in self._graph[u]:
                if n != v:
                    self._decrease_count(n)

        elif self.is_in_mis(u) != self.is_in_mis(v):
            non_mis_node = v if self.is_in_mis(u) else u
            self._increase_count(non_mis_node)

    def remove_edge(self, u, v):
        self._graph.remove_edge(u, v)

        if self.is_in_mis(u) or self.is_in_mis(v):
            non_mis_node = u if self.is_in_mis(v) else v
            self._decrease_count(non_mis_node)

    def _decrease_count(self, v):
        assert(self._count[v] > 0)
        self._count[v] = self._count[v] - 1
        if self._count[v] == 0:
            self._mis.add(v)
            for w in self._graph[v]:
                self._increase_count(w)

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

    def __init__(self, graph):
        super(ImprovedDynamicMIS, self).__init__(graph)
        self._light_count = dict()
        self._heavy_mis = set()
        self._light_mis = set()
        self._delta_c = 0
        self._m_c = 0
        self.new_phase()

    def new_phase(self):
        self._m_c = len(self._graph.edges)
        self._delta_c = self._m_c ** (2/3)

        # Initialise light node mis via Trivial Algo
        self._light_mis = TrivialMIS(self._graph, candidate_filter=self._is_light).get_mis()

        self._light_count = dict()
        for v in self._graph.nodes:
            self._light_count[v] = 0

        for u, v in self._graph.edges:
            if u in self._light_mis or v in self._light_mis:
                non_mis_node = u if v in self._light_mis else v
                self._light_count[non_mis_node] += 1

        assert self.is_valid_light_mis()
        assert self.is_valid_light_count()

        self._compute_heavy_mis()

    def check_new_phase(self):
        m = len(self._graph.edges)
        if m <= self._m_c / 2 or m >= self._m_c * 2:
            self.new_phase()
            return True
        return False

    def insert_node(self, v, edges):
        self._graph.add_node(v)
        filtered_edge_insert(self._graph, edges)
        self._light_count[v] = 0

        if self.check_new_phase():
            return

        for w in self._graph[v]:
            if self._became_heavy(w) and w in self._light_mis:
                self._remove_from_light_mis(w)
                old_neighbors = set(self._graph[w])
                old_neighbors.remove(v)
                self._decrease_light_count(old_neighbors)
            # this does not work because decrease light count might already have incremented for a new light mis node
            # elif w in self._light_mis:
            #     self._light_count[v] += 1

        # Instead do the same loop here again where the light mis does not change during iteration
        self._light_count[v] = 0
        for w in self._graph[v]:
            if w in self._light_mis:
                self._light_count[v] += 1

        if self._is_light(v) and self._light_count[v] == 0:
            self._insert_into_light_mis(v)

        self._compute_heavy_mis()

    def remove_node(self, v):
        neighbors = set(self._graph[v])
        self._graph.remove_node(v)
        del self._light_count[v]

        if self.check_new_phase():
            return

        if v in self._light_mis:
            self._remove_from_light_mis(v)
            self._decrease_light_count(neighbors)

        for w in neighbors:
            if self._light_count[w] == 0 and w not in self._light_mis:
                self._insert_into_light_mis(w)

        self._compute_heavy_mis()

    def remove_edge(self, u, v):
        self._graph.remove_edge(u, v)

        if self.check_new_phase():
            return

        if u in self._light_mis or v in self._light_mis:
            non_mis_node = u if v in self._light_mis else v
            self._decrease_light_count([non_mis_node])

        for node in [u, v]:
            if self._light_count[node] == 0 and node not in self._light_mis:
                self._insert_into_light_mis(node)

        self._compute_heavy_mis()

    def insert_edge(self, u, v):

        self._graph.add_edge(u, v)

        if self.check_new_phase():
            return

        # Adding the edge could make a vertex heavy
        for node, other in [(u, v), (v, u)]:
            # if self._became_heavy(node) and node in self._light_mis:
            if self._is_heavy(node) and node in self._light_mis:
                self._remove_from_light_mis(node)
                if other in self._light_mis:
                    self._light_count[node] += 1
                    assert self._light_count[node] == 1

                # neighbor already sees new edge
                old_neighbors = set(self._graph[node])
                old_neighbors.remove(other)
                self._decrease_light_count(old_neighbors)

        # Still both can be in the light mis -> then remove u
        if u in self._light_mis and v in self._light_mis:
            # Do not decrease count of v
            u_neighbors = set(self._graph[u])
            u_neighbors.remove(v)
            self._remove_from_light_mis(u)
            self._light_count[u] += 1
            assert self._light_count[u] == 1
            # No need to decrease light count of v
            self._decrease_light_count(u_neighbors)
        elif u in self._light_mis or v in self._light_mis:
            non_mis_node = u if v in self._light_mis else v
            self._light_count[non_mis_node] += 1

        self._compute_heavy_mis()

    def _became_heavy(self, v):
        # Node should be heavy but light with one neighbor less
        deg = self._graph.degree[v]
        return deg >= self._delta_c > deg - 1

    def _became_light(self, v):
        # Node should be light but heavy with one neighbor more
        deg = self._graph.degree[v]
        return deg + 1 >= self._delta_c > deg

    def _remove_from_light_mis(self, v):
        assert v in self._light_mis
        self._light_mis.remove(v)

    def _decrease_light_count(self, nodes):
        for v in nodes:
            assert self._light_count[v] > 0
            self._light_count[v] -= 1
            if self._light_count[v] == 0 and self._is_light(v):
                self._insert_into_light_mis(v)

    def _insert_into_light_mis(self, v):
        assert self._is_light(v)
        assert v not in self._light_mis

        self._light_mis.add(v)
        for w in self._graph[v]:
            assert w not in self._light_mis
            self._light_count[w] += 1

    def _candidate_for_heavy_mis(self, v):
        return self._is_heavy(v) and self._light_count[v] == 0

    def _is_heavy(self, v):
        return self._graph.degree[v] >= self._delta_c

    def _is_light(self, v):
        return not self._is_heavy(v)

    def get_mis(self):
        return set.union(self._light_mis, self._heavy_mis)

    def is_in_mis(self, node):
        return node in self._heavy_mis or node in self._light_mis

    def _compute_heavy_mis(self):
        self._heavy_mis = TrivialMIS(self._graph, candidate_filter=self._candidate_for_heavy_mis).get_mis()

    def is_valid_mis(self):
        assert self.is_valid_light_count()
        return super(ImprovedDynamicMIS, self).is_valid_mis()

    def is_valid_light_mis(self):
        assert self.is_valid_light_count()
        for v in self._graph.nodes:
            if self._is_light(v) and self._light_count[v] == 0:
                if v not in self._light_mis:
                    return False
        return True

    def is_valid_light_count(self):

        for v in self._graph.nodes:
            sum = 0
            for n in self._graph[v]:
                if n in self._light_mis:
                    sum += 1

            if sum != self._light_count[v]:
                return False
        return True

