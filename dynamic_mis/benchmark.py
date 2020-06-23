from dynamic_mis.algorithm import *
from dynamic_mis.utility import *
import numpy.random as npr
import timeit


def edge_from_line(line):
    items = line.split()
    return items[0], items[1]


def nodes_from_file(dataset_file):
    nodes = set()
    for line in open(dataset_file):
        e = edge_from_line(line)
        if e[0] not in nodes:
            nodes.add(e[0])
        if e[1] not in nodes:
            nodes.add(e[1])

    return nodes


def benchmark_edge_insertion(algo_cls, nodes, edges, benchmark_name=""):
    graph = nx.Graph()
    graph.add_nodes_from(nodes)

    def execute():
        algo = algo_cls(graph)
        for e in edges:
            algo.insert_edge(*e)

    print('Starting Insertion Benchmark ' + benchmark_name)
    t = timeit.timeit(execute, number=1)
    print("Completed Benchmark {} in t={:.3f}".format(benchmark_name, t))
    return t


def average_insertion_runs(algo_cls, nodes, edges, benchmark_name="", runs=5):
    total = 0
    for _ in range(runs):
        total += benchmark_edge_insertion(algo_cls, nodes, edges, benchmark_name)
    total /= runs
    print("Average Benchmark {} in t={:.3f}\n".format(benchmark_name, total))
    return total


def benchmark_edge_deletion(algo_cls, graph, removals, benchmark_name=""):

    def execute():
        algo = algo_cls(graph)
        for e in removals:
            algo.remove_edge(*e)

    print('Starting Insertion Benchmark ' + benchmark_name)
    t = timeit.timeit(execute, number=1)
    print("Completed Benchmark {} in t={:.3f}".format(benchmark_name, t))
    return t


def average_deletion_runs(algo_cls, graph, removals, benchmark_name="", runs=5):
    total = 0
    for _ in range(runs):
        g = graph.copy()
        total += benchmark_edge_deletion(algo_cls, g, removals, benchmark_name)
    total /= runs
    print("Average Benchmark {} in t={:.3f}\n".format(benchmark_name, total))
    return total


def benchmark_initialization(algo_cls, graph, benchmark_name=""):
    def execute():
        algo = algo_cls(graph)

    print('Starting Insertion Benchmark ' + benchmark_name)
    t = timeit.timeit(lambda: algo_cls(graph), number=5) / 5
    print("Completed Benchmark {} in t={:.3f}".format(benchmark_name, t))
    return t


def graph_from_file(file):
    g = nx.Graph()
    edges = []
    for line in open(file):
        edges.append(edge_from_line(line))

    g.add_edges_from(edges)
    return g, edges


def brightkite(data_dir, seed=2, iterations=10000):
    file = data_dir + 'loc-brightkite_edges/out.loc-brightkite_edges'
    graph, edges = graph_from_file(file)

    rnd = npr.RandomState(seed)
    idx = rnd.choice(len(edges), size=iterations, replace=False)
    removals = [edges[i] for i in idx]

    benchmark_initialization(TrivialMIS, graph, "Brightkite Trivial Init")
    benchmark_initialization(SimpleMIS, graph, "Brightkite Simple Init")
    benchmark_initialization(ImprovedDynamicMIS, graph, "Brightkite Dynamic Init")
    benchmark_initialization(ImplicitMIS, graph, "Brightkite Implicit Init")

    average_deletion_runs(TrivialMIS, graph, removals, "Brightkite Trivial")
    average_deletion_runs(SimpleMIS, graph, removals, "Brightkite Simple")
    average_deletion_runs(ImprovedDynamicMIS, graph, removals, "Brightkite Improved Dynamic")
    average_deletion_runs(ImplicitMIS, graph, removals, "Brightkite Implicit")


# In the final graph all nodes are considered light
def wildbirds(data_dir):
    file = data_dir + 'aves-wildbird-network.edges'
    nodes = nodes_from_file(file)
    edges = [edge_from_line(line) for line in open(file)]
    time_initialization_empty(file)
    # average_insertion_runs(TrivialMIS, nodes, edges, 'Wildbirds Trivial')
    average_insertion_runs(SimpleMIS, nodes, edges, 'Wildbirds Simple')
    average_insertion_runs(ImprovedIncrementalMIS, nodes, edges, 'Wildbirds Improved Incremental')
    average_insertion_runs(ImprovedDynamicMIS, nodes, edges, 'Wildbirds Improved Dynamic')
    average_insertion_runs(ImplicitMIS, nodes, edges, 'Wildbirds Implicit')


def topology(data_dir):
    file = data_dir + 'topology/out.topology'
    nodes = nodes_from_file(file)
    edges = [edge_from_line(line) for line in open(file)]

    time_initialization_empty(file)
    # Takes a long time
    # average_insertion_runs(TrivialMIS, nodes, edges, 'Topology Trivial')
    average_insertion_runs(SimpleMIS, nodes, edges, 'Topology Simple')
    average_insertion_runs(ImprovedIncrementalMIS, nodes, edges, 'Topology Improved Incremental')
    average_insertion_runs(ImprovedDynamicMIS, nodes, edges, 'Topology Improved Dynamic')
    average_insertion_runs(ImplicitMIS, nodes, edges, 'Topology Implicit')


def facebook(data_dir):
    file = data_dir + 'facebook-wosn-links/out.facebook-wosn-links'
    nodes = nodes_from_file(file)
    edges = [edge_from_line(line) for line in open(file)]

    time_initialization_empty(file)
    # average_insertion_runs(TrivialMIS, nodes, edges 'Facebook Trival')
    average_insertion_runs(SimpleMIS, nodes, edges, 'Facebook Simple')
    average_insertion_runs(ImprovedIncrementalMIS, nodes, edges, 'Facebook Improved Incremental')
    # average_insertion_runs(ImprovedDynamicMIS, nodes, edges, 'Facebook Improved Dynamic')
    average_insertion_runs(ImplicitMIS, nodes, edges, 'Facebook Implicit')


def youtube(data_dir):
    file = data_dir + 'youtube-u-growth/out.youtube-u-growth'
    nodes = nodes_from_file(file)
    edges = [edge_from_line(line) for line in open(file)]

    time_initialization_empty(file)
    # average_insertion_runs(TrivialMIS, nodes, edges 'Youtube Trival')
    average_insertion_runs(SimpleMIS, nodes, edges, 'Youtube Simple')
    average_insertion_runs(ImprovedIncrementalMIS, nodes, edges, 'Youtube Improved Incremental')
    # average_insertion_runs(ImprovedDynamicMIS, nodes, edges, 'Youtube Improved Dynamic')
    average_insertion_runs(ImplicitMIS, nodes, edges, 'Youtube Implicit')


def time_initialization_empty(file):
    nodes = nodes_from_file(file)
    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    t = timeit.timeit(lambda: TrivialMIS.compute(graph), number=1)
    print("Completed Empty Trivial in t={:.3f}".format(t))


def time_initialization_full(file):
    nodes = nodes_from_file(file)
    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    edges = [edge_from_line(line) for line in open(file)]
    graph.add_edges_from(edges)
    t = timeit.timeit(lambda: TrivialMIS.compute(graph), number=1)
    print("Completed Full Trivial in t={:.3f}".format(t))


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        data_dir = '../data/'

    # Insertions
    # wildbirds(data_dir)
    # topology(data_dir)
    # facebook(data_dir)
    # youtube(data_dir)

    # Deletions
    brightkite(data_dir, iterations=1000)
    # brightkite(data_dir, iterations=10000)
    # brightkite(data_dir, iterations=100000)

