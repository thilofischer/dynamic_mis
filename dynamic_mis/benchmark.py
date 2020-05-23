from dynamic_mis.algorithm import *
from dynamic_mis.utility import *


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
    from timeit import default_timer as timer

    graph = nx.Graph()
    graph.add_nodes_from(nodes)

    print('Starting Benchmark ' + benchmark_name)

    start = timer()

    algo = algo_cls(graph)
    # for line in open(dataset_file):
    #     e = edge_from_line(line)
    for e in edges:
        algo.insert_edge(*e)
        # assert algo.is_valid_mis()

    end = timer()
    t = end - start

    valid = algo.is_valid_mis()
    msg = "[ OK ]" if valid else "[FAIL]"
    print("Result is: " + msg)
    print("Completed Benchmark {} in t={:.3f}".format(benchmark_name, t))
    return t, valid


# In the final graph all nodes are considered light
def wildbirds(data_dir):
    file = data_dir + 'aves-wildbird-network.edges'
    nodes = nodes_from_file(file)
    edges = [edge_from_line(line) for line in open(file)]
    benchmark_edge_insertion(TrivialMIS, nodes, edges, 'Wildbirds Trivial')
    benchmark_edge_insertion(SimpleMIS, nodes, edges, 'Wildbirds Simple')
    benchmark_edge_insertion(ImprovedIncrementalMIS, nodes, edges, 'Wildbirds Improved Incremental')
    benchmark_edge_insertion(ImprovedDynamicMIS, nodes, edges, 'Wildbirds Improved Dynamic')
    benchmark_edge_insertion(ImplicitMIS, nodes, edges, 'Wildbirds Implicit')


def topology(data_dir):
    file = data_dir + 'topology/out.topology'
    nodes = nodes_from_file(file)
    edges = [edge_from_line(line) for line in open(file)]

    # Takes a long time
    # benchmark_edge_insertion(TrivialMIS, nodes, edges, 'Topology Trivial')
    # benchmark_edge_insertion(SimpleMIS, nodes, edges, 'Topology Simple')
    # benchmark_edge_insertion(ImprovedIncrementalMIS, nodes, edges, 'Topology Improved Incremental')
    benchmark_edge_insertion(ImprovedDynamicMIS, nodes, edges, 'Topology Improved Dynamic')
    # benchmark_edge_insertion(ImplicitMIS, nodes, edges, 'Topology Implicit')


def facebook(data_dir):
    file = data_dir + 'facebook-wosn-links/out.facebook-wosn-links'
    nodes = nodes_from_file(file)
    edges = [edge_from_line(line) for line in open(file)]

    # benchmark_edge_insertion(TrivialMIS, nodes, edges 'Facebook Trival')
    benchmark_edge_insertion(SimpleMIS, nodes, edges, 'Facebook Simple')
    benchmark_edge_insertion(ImprovedIncrementalMIS, nodes, edges, 'Facebook Improved Incremental')
    # benchmark_edge_insertion(ImprovedDynamicMIS, nodes, edges, 'Facebook Improved Dynamic')
    benchmark_edge_insertion(ImplicitMIS, nodes, edges, 'Facebook Implicit')


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        data_dir = '../data/'

    wildbirds(data_dir)
    # topology(data_dir)
    # facebook(data_dir)


