from dynamic_mis.algorithm import *
from dynamic_mis.utility import *


# In the final graph all nodes are considered light
def wildbirds():
    file = '../data/aves-wildbird-network.edges'
    nodes = nodes_from_file(file)
    benchmark_edge_insertion(TrivialMIS, file, nodes, 'Wildbirds Trivial')
    benchmark_edge_insertion(SimpleMIS, file, nodes, 'Wildbirds Simple')
    benchmark_edge_insertion(ImprovedIncrementalMIS, file, nodes, 'Wildbirds Improved Incremental')
    benchmark_edge_insertion(ImprovedDynamicMIS, file, nodes, 'Wildbirds Improved Dynamic')
    benchmark_edge_insertion(ImplicitMIS, file, nodes, 'Wildbirds Implicit')


def topology():
    file = '../data/topology/out.topology'
    nodes = nodes_from_file(file)

    # Takes a long time
    # benchmark_edge_insertion(TrivialMIS, file, nodes, 'Topology Trivial')
    benchmark_edge_insertion(SimpleMIS, file, nodes, 'Topology Simple')
    benchmark_edge_insertion(ImprovedIncrementalMIS, file, nodes, 'Topology Improved Incremental')
    # benchmark_edge_insertion(ImprovedDynamicMIS, file, nodes, 'Topology Improved Dynamic')
    benchmark_edge_insertion(ImplicitMIS, file, nodes, 'Topology Implicit')


if __name__ == '__main__':
    wildbirds()
    # wildbirds_improved_dynamic()
    # topology()
