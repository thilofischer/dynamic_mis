from abc import abstractmethod
from collections import defaultdict
import networkx as nx


def filtered_edge_insert(g: nx.Graph, edges):
    # check that node is already in graph: else networkx will create that node and we don't want that
    def both_nodes_exist(e):
        return g.has_node(e[0]) and g.has_node(e[1])

    edges = filter(both_nodes_exist, edges)
    g.add_edges_from(edges)
    return len(list(edges))


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


class TrivialMIS(Algorithm):

    def __init__(self, graph, candidate_filter=None):
        super(TrivialMIS, self).__init__(graph)
        self._candidate_filter = candidate_filter
        self._mis = TrivialMIS.compute(graph, candidate_filter)

    @staticmethod
    def compute_networkx(graph):
        return nx.maximal_independent_set(graph)

    @staticmethod
    def compute(graph, candidate_filter=None):
        mis = set()

        if candidate_filter is None:
            for v in graph.nodes:
                can_be_added = True
                for w in graph[v]:
                    if w in mis:
                        can_be_added = False
                if can_be_added:
                    mis.add(v)
        else:
            for v in graph.nodes:
                if candidate_filter(v):
                    can_be_added = True
                    for w in graph[v]:
                        if w in mis:
                            can_be_added = False
                    if can_be_added:
                        mis.add(v)

        return mis

    def insert_edge(self, u, v):
        if self._graph.has_edge(u, v):
            return

        self._graph.add_edge(u, v)
        self._mis = TrivialMIS.compute(self._graph, self._candidate_filter)

    def remove_edge(self, u, v):
        self._graph.remove_edge(u, v)
        self._mis = TrivialMIS.compute(self._graph, self._candidate_filter)

    def insert_node(self, v, edges=[]):
        self._graph.add_node(v)
        filtered_edge_insert(self._graph, edges)
        self._mis = TrivialMIS.compute(self._graph, self._candidate_filter)

    def remove_node(self, v):
        self._graph.remove_node(v)
        self._mis = TrivialMIS.compute(self._graph, self._candidate_filter)

    def is_in_mis(self, node):
        return node in self._mis

    def get_mis(self):
        return self._mis


class SimpleMIS(Algorithm):

    def __init__(self, graph):
        super(SimpleMIS, self).__init__(graph)
        self._count = defaultdict(lambda: 0)
        self._mis = TrivialMIS.compute(self._graph)

        for v in self._mis:
            for u in self._graph[v]:
                self._count[u] += 1

        # This assertion will fail if is_valid_mis is patched for a test case
        # assert self.is_valid_mis()
        # assert self._valid_count()

    def insert_node(self, v, edges=[]):
        self._graph.add_node(v)
        filtered_edge_insert(self._graph, edges)

        self._count[v] = 0
        for n in self._graph[v]:
            if n in self._mis:
                self._count[v] += 1

        if self._count[v] == 0:
            self._mis.add(v)
            for n in self._graph[v]:
                # assert n not in self._mis
                self._count[n] += 1

    def remove_node(self, v):
        if self.is_in_mis(v):
            self._mis.remove(v)
            for w in self._graph[v]:
                self._decrease_count(w)

        self._graph.remove_node(v)

    def insert_edge(self, u, v):
        assert u in self._graph and v in self._graph
        if self._graph.has_edge(u, v):
            return
        self._graph.add_edge(u, v)

        if u in self._mis and v in self._mis:
            # assert self._count[u] == 0
            self._count[u] = 1
            self._mis.remove(u)

            # First add one to v and then remove it.
            # This saves us an if statement inside a loop
            # self._count[v] = 1
            for n in self._graph[u]:
                if n != v:
                    self._decrease_count(n)

        elif (u in self._mis) != (v in self._mis):
            non_mis_node = v if u in self._mis else u
            self._count[non_mis_node] += 1
            # non_mis_node was not in mis -> we don't need to inform neighbors in this case

        # assertion slows it down significantly
        # assert self._valid_count()

    def remove_edge(self, u, v):
        self._graph.remove_edge(u, v)

        if self.is_in_mis(u) or self.is_in_mis(v):
            non_mis_node = u if self.is_in_mis(v) else v
            self._decrease_count(non_mis_node)

    def _decrease_count(self, v):
        # assert(self._count[v] > 0)
        self._count[v] -= 1
        # This and v not in self._mis is needed to optimize a loop in insert edge
        # if self._count[v] == 0 and v not in self._mis:
        if self._count[v] == 0:
            # assert all([w not in self._mis for w in self._graph[v]])
            self._mis.add(v)
            for w in self._graph[v]:
                # assert w not in self._mis
                self._count[w] += 1

    def _increase_count(self, v):
        self._count[v] += 1
        if v in self._mis:
            self._mis.remove(v)

    def _valid_count(self):
        for v in self._graph:
            c = self._count[v]
            s = 0
            for n in self._graph[v]:
                if n in self._mis:
                    s += 1
            if s != c:
                return False
        return True

    def is_in_mis(self, node):
        return node in self._mis

    def get_mis(self):
        return self._mis


class ImprovedIncrementalMIS(SimpleMIS):

    # Calling the super class makes it slower than the direct implementation
    # def insert_edge(self, u, v):
    #     lower_deg, higher_deg = (u, v) if self._graph.degree(u) < self._graph.degree(v) else (v, u)
    #     # super(ImprovedIncrementalMIS, self).insert_edge(lower_deg, higher_deg)
    #     SimpleMIS.insert_edge(self, lower_deg, higher_deg)

    def insert_edge(self, u, v):
        assert u in self._graph and v in self._graph
        if self._graph.has_edge(u, v):
            return
        self._graph.add_edge(u, v)

        if u in self._mis and v in self._mis:
            lower_deg, higher_deg = (u, v) if self._graph.degree[u] < self._graph.degree[v] else (v, u)

            # assert self._count[lower_deg] == 0
            self._count[lower_deg] = 1
            self._mis.remove(lower_deg)

            for n in self._graph[lower_deg]:
                if n != higher_deg:
                    self._decrease_count(n)
            # self._increase_count(lower_deg)  # increase_count automatically removes u from mis set
            # for n in self._graph[lower_deg]:
            #     if n != higher_deg:
            #         self._decrease_count(n)

        elif (u in self._mis) != (v in self._mis):
            non_mis_node = v if u in self._mis else u
            self._count[non_mis_node] += 1

        # assert self._valid_count()

    def insert_node(self, v, edges=[], count=None):
        raise NotImplementedError

    def remove_node(self, v):
        raise NotImplementedError

    def remove_edge(self, u, v):
        raise NotImplementedError


class ImprovedDynamicMIS(Algorithm):

    def __init__(self, graph):
        Algorithm.__init__(self, graph)
        self._light_count = defaultdict(lambda: 0)
        self._heavy_mis = set()
        self._heavy_nodes = set()
        self._light_mis = set()
        self._delta_c = 0
        self._m_c = 0
        self._edge_count = self._graph.number_of_edges()
        self.new_phase()

    def new_phase(self):
        if self._edge_count <= self._m_c / 2 or self._edge_count >= self._m_c * 2:
            self._m_c = self._edge_count
            self._delta_c = self._edge_count ** (2 / 3)

            self._heavy_nodes.clear()
            self._light_mis.clear()
            self._light_count = defaultdict(lambda: 0)
            for v in self._graph:
                if self._graph.degree[v] >= self._delta_c:
                    self._heavy_nodes.add(v)
                elif self._light_count[v] == 0:
                    self._light_mis.add(v)
                    for w in self._graph[v]:
                        self._light_count[w] += 1

            # These assertions slow down execution
            # assert self.is_valid_light_mis()
            # assert self.is_valid_light_count()
            self._compute_heavy_mis()
            return True

        return False

    def insert_node(self, v, edges):
        self._graph.add_node(v)
        c = filtered_edge_insert(self._graph, edges)
        self._edge_count += c

        if self._is_heavy(v):
            self._heavy_nodes.add(v)
        for u in self._graph[v]:
            if self._is_heavy(u) and u not in self._heavy_nodes:
                self._heavy_nodes.add(u)

        if self.new_phase():
            return

        for w in self._graph[v]:
            if self._became_heavy(w) and w in self._light_mis:
                self._remove_from_light_mis(w)
                self._decrease_light_count(self._graph[w], skip=v)
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

        self._edge_count -= len(neighbors)

        if v in self._heavy_nodes:
            self._heavy_nodes.remove(v)
        for u in neighbors:
            if u in self._heavy_nodes and self._is_light(u):
                self._heavy_nodes.remove(u)

        if self.new_phase():
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
        self._edge_count -= 1

        if self.new_phase():
            return

        if u in self._light_mis or v in self._light_mis:
            non_mis_node = u if v in self._light_mis else v
            self._decrease_light_count([non_mis_node])

        for node in [u, v]:
            if self._light_count[node] == 0 and node not in self._light_mis:
                self._insert_into_light_mis(node)

            if node in self._heavy_nodes and self._is_light(node):
                self._heavy_nodes.remove(node)

        self._compute_heavy_mis()

    def insert_edge(self, u, v):
        assert u in self._graph and v in self._graph

        if self._graph.has_edge(u, v):
            return

        self._graph.add_edge(u, v)
        self._edge_count += 1

        if self.new_phase():
            return

        for node, other in [(u, v), (v, u)]:
            if self._is_heavy(node) and node not in self._heavy_nodes:
                self._heavy_nodes.add(node)

            # Adding the edge could make a vertex heavy
            if node in self._light_mis and self._is_heavy(node):
                self._remove_from_light_mis(node)
                if other in self._light_mis:
                    self._light_count[node] += 1
                    assert self._light_count[node] == 1

                # neighbor already sees new edge
                # old_neighbors = set(self._graph[node])
                # old_neighbors.remove(other)
                self._decrease_light_count(self._graph[node], skip=other)

        # Still both can be in the light mis -> then remove u
        if u in self._light_mis and v in self._light_mis:
            self._remove_from_light_mis(u)
            self._light_count[u] += 1
            assert self._light_count[u] == 1
            # No need to decrease light count of v
            self._decrease_light_count(self._graph[u], skip=v)
        elif u in self._light_mis or v in self._light_mis:
            non_mis_node = u if v in self._light_mis else v
            self._light_count[non_mis_node] += 1

        self._compute_heavy_mis()

    def _became_heavy(self, v):
        # Node should be heavy but light with one neighbor less
        deg = self._graph.degree[v]
        return deg >= self._delta_c > deg - 1

    def _remove_from_light_mis(self, v):
        assert v in self._light_mis
        self._light_mis.remove(v)

    def _decrease_light_count(self, nodes, skip=None):
        for v in nodes:
            if v == skip:
                continue

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

    def _is_heavy(self, v):
        return self._graph.degree[v] >= self._delta_c

    def _is_light(self, v):
        return self._graph.degree[v] < self._delta_c
        # return not self._is_heavy(v)

    def get_mis(self):
        return set.union(self._light_mis, self._heavy_mis)

    def is_in_mis(self, node):
        return node in self._heavy_mis or node in self._light_mis

    def _candidate_for_heavy_mis(self, v):
        # return self._is_heavy(v) and self._light_count[v] == 0
        # In line is heavy to save a func call
        return self._graph.degree[v] >= self._delta_c and self._light_count[v] == 0

    def _compute_heavy_mis(self):
        self._heavy_mis = TrivialMIS.compute(self._graph.subgraph(self._heavy_nodes),
                                             candidate_filter=lambda n: self._light_count[n] == 0)

    def is_valid_mis(self):
        assert self.is_valid_light_count()
        assert self.is_valid_light_mis()
        return Algorithm.is_valid_mis(self)

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


class ImplicitMIS(Algorithm):

    def __init__(self, graph):
        super(ImplicitMIS, self).__init__(graph)
        self._m_c = self._graph.number_of_edges()
        self._heavy_threshold = self._m_c ** 0.5
        self._edge_count = self._m_c
        self._almost_heavy_count = dict()
        self._almost_heavy_nodes = None
        self._independent_set = set()

        self._count = defaultdict(lambda: 0)
        # In the beginning this will always return 0
        # for v in self._graph.nodes:
        #     if self.is_heavy(v):
        #         self._count[v] = self._calculate_count(v)

    def new_phase(self):
        if self._m_c/2.0 < self._edge_count < 2.0*self._m_c:
            return False

        # Zero edges is a special case
        if self._edge_count == self._m_c == 0:
            return False

        new_threshold = self._edge_count ** 0.5

        if self._edge_count <= self._m_c/2.0:
            # Lowering the boundary
            # Have we calculated all counts?
            for v in self.almost_heavy_nodes():
                if v not in self._almost_heavy_count:
                    self._almost_heavy_count[v] = self._calculate_count(v)
            # for v in self._almost_heavy_nodes():
            #     if v not in self._almost_heavy_count:
            #         self._almost_heavy_count[v] = self._calculate_count(v)
            assert all(v in self._almost_heavy_count for v in self.almost_heavy_nodes())
            self._count = {**self._count, **self._almost_heavy_count}
            # for v in self._graph:
            #     if self.is_heavy(v):
            #         assert v in self._count
        elif self._edge_count >= 2*self._m_c:
            # Raising the boundary
            # Remove count from the now light nodes
            # Resize while iterating
            # for v in self._count.keys():
            #     if self._graph.degree[v] < new_threshold:
            #         del self._count[v]

            # Removing them costs 0.1 s in Topology
            for v in self._graph.nodes:
                if v in self._count and self._graph.degree[v] < new_threshold:
                    del self._count[v]
        else:
            raise ValueError

        self._m_c = self._edge_count
        self._heavy_threshold = new_threshold
        self._almost_heavy_count.clear()
        self._almost_heavy_nodes = None
        # self._almost_heavy_count = dict()
        return True

    def insert_node(self, v, edges=[]):
        raise NotImplementedError

    def remove_node(self, v):
        raise NotImplementedError

    def insert_edge(self, u, v):
        if self._graph.has_edge(u, v):
            return

        self._graph.add_edge(u, v)
        self._edge_count += 1
        self.new_phase()
        self.update_almost_heavy()

        # Do this first so that newly heavy nodes have a count
        for node, other in [(u, v), (v, u)]:
            if self.is_heavy(node) and node not in self._count:
                self._count[node] = self._calculate_count(node)
                # _calculate_count already sees edge (node, other) -> result is 1 too high
                if other in self._independent_set:
                    self._count[node] -= 1

        if u in self._independent_set and v in self._independent_set:
            self._independent_set.remove(u)
            if self._graph.degree[node] > self._heavy_threshold:
                self._count[u] = 1
            for w in self._graph[u]:
                # Check for w != higher_deg here, because the new edge did not influence the count
                if self._graph.degree[node] > self._heavy_threshold and w != v:
                    # assert self._count[w] > 0
                    self._count[w] -= 1

        elif u in self._independent_set or v in self._independent_set:
            non_mis_node = v if u in self._independent_set else u
            if self._graph.degree[node] > self._heavy_threshold:
                self._count[non_mis_node] += 1

    def remove_edge(self, u, v):
        self._graph.remove_edge(u, v)
        self._edge_count -= 1
        self.new_phase()
        self.update_almost_heavy()

        for node, other in [(u, v), (v, u)]:
            if self.is_heavy(node) and other in self._independent_set:
                self._count[node] -= 1
            elif node in self._almost_heavy_count and other in self._independent_set:
                self._almost_heavy_count[node] -= 1
            elif self.is_light(node) and node in self._count:
                del self._count[node]

    def update_almost_heavy(self):
        if self._edge_count < self._m_c:
            # Calculate the count of one node that will become heavy in the next boundary reduction
            if self._almost_heavy_nodes is None:
                self._almost_heavy_nodes = self.almost_heavy_nodes()

            if len(self._almost_heavy_nodes) > 0:
                node = self._almost_heavy_nodes.pop()
                self._almost_heavy_count[node] = self._calculate_count(node)
        elif len(self._almost_heavy_count) > 0:
            # Clear calculations
            self._almost_heavy_count.clear()

    def is_heavy(self, node):
        return self._graph.degree[node] > self._heavy_threshold

    def is_light(self, node):
        return self._graph.degree[node] <= self._heavy_threshold

    def is_almost_heavy(self, node):
        return self._heavy_threshold >= self._graph.degree[node] >= (self._m_c / 2.0) ** 0.5

    def almost_heavy_nodes(self):
        f = filter(self.is_almost_heavy, self._graph.nodes)
        return set(f)

    def _calculate_count(self, node):
        # assert self.is_heavy(node)
        s = 0
        for w in self._graph[node]:
            if w in self._independent_set:
                s += 1
        return s

    def _insert_into_is(self, v):
        # assert v not in self._independent_set
        self._independent_set.add(v)
        for w in self._graph[v]:
            # assert w not in self._independent_set
            if self.is_heavy(w):
                self._count[w] += 1

    def is_in_mis(self, node):
        if node in self._independent_set:
            return True
        elif self.is_heavy(node) and self._count[node] == 0:
            # add and inform neighbours
            self._insert_into_is(node)
            return True
        elif self.is_light(node):
            for w in self._graph[node]:
                if w in self._independent_set:
                    return False

            # Is only reached if no neighbor is in is
            self._insert_into_is(node)
            return True
        return False

    def get_mis(self):
        for v in self._graph.nodes:
            self.is_in_mis(v)
        return self._independent_set
