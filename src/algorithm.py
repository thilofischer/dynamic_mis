#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import abstractmethod
from collections import defaultdict
from enum import Enum
import networkx as nx
import logger


class Algorithm:
    def __init__(self, graph):
        self._graph = graph
        self.initialise()

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


class TrivialMIS(MISAlgorithm):

    def __init__(self, graph):
        self._mis = set()
        super().__init__(graph)

    def initialise(self):
        # self._logger.adjusted(len(self._independent_set))
        self._mis.clear()

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


class SimpleRelaxedMIS(MISAlgorithm):

    def __init__(self, graph):
        self._count = defaultdict(lambda: 0)
        super(SimpleRelaxedMIS, self).__init__(graph)

    def initialise(self):
        tmis = TrivialMIS(self._graph)

        for u, v in self._graph.edges:
            if tmis.is_in_mis(u):
                self._increase_count(v)
            elif tmis.is_in_mis(v):
                self._increase_count(u)

    def insert_node(self, v, edges=[]):
        #reset count to protect against re-insertion bugs
        self._count[v] = 0
        self._graph.add_node(v)
        self._graph.add_edges_from(edges)
        for n in self._graph[v]:
            if self.is_in_mis(n):
                self._increase_count(v)

        if self.is_in_mis(v):
            for n, _ in self._graph[v]:
                self._increase_count(n)

    def remove_node(self, v):
        if self.is_in_mis(v):
            for w in self._graph[v]:
                self._decrease_count(w)
        self._graph.remove_node(v)

    def insert_edge(self, u, v):
        self._graph.add_edge(u, v)
        if self.is_in_mis(u) and self.is_in_mis(v):
            self._increase_count(u)
            for n, _ in self._graph[u]:
                self._decrease_count(n)

        elif self.is_in_mis(u) != self.is_in_mis(v):
            non_mis_node = v if self.is_in_mis(u) else u
            self._increase_count(non_mis_node)

    def remove_edge(self, u, v):
        if self.is_in_mis(u) or self.is_in_mis(v):
            mis_node = u if self.is_in_mis(u) else v

            for n, _ in self._graph[mis_node]:
                self._decrease_count(n)
        self._graph.remove_edge(u, v)

    def _decrease_count(self, v):
        self._count[v] = self._count[v] - 1

    def _increase_count(self, v):
        self._count[v] = self._count[v] + 1

    def is_in_mis(self, node):
        return self._count[node] == 0

    def get_mis(self):
        mis = set()
        for v in self._graph.nodes:
            if self.is_in_mis(v):
                mis.add(v)
        return mis


class SimpleExplicitMIS(SimpleRelaxedMIS):
    
    def __init__(self, graph):
        self._mis = set()
        super(SimpleExplicitMIS, self).__init__(graph)

    def initialise(self):
        tmis = TrivialMIS(self._graph)

        for u, v in self._graph.edges:
            if tmis.is_in_mis(u):
                if u not in self._mis:
                    self._mis.add(u)
                self._increase_count(v)
            elif tmis.is_in_mis(v):
                if v not in self._mis:
                    self._mis.add(v)
                self._increase_count(u)

    def _decrease_count(self, v):
        super(SimpleExplicitMIS, self)._decrease_count(v)
        if self._count[v] == 0:
            self._mis.add(v)

    def _increase_count(self, v):
        super(SimpleExplicitMIS, self)._increase_count(v)
        # if self._count[v] == 1 and v in self._mis #counter == 0 and not in mis in initial state
        if v in self._mis:
            self._mis.remove(v)

    def is_in_mis(self, v):
        return v in self._mis

    def get_mis(self):
        return self._mis
