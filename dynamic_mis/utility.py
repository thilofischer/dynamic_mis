import networkx as nx


def benchmark_edge_insertion(algo_cls, dataset_file, nodes, benchmark_name=""):
    from timeit import default_timer as timer

    graph = nx.Graph()
    graph.add_nodes_from(nodes)

    print('Starting Benchmark ' + benchmark_name)

    start = timer()

    algo = algo_cls(graph)
    for line in open(dataset_file):
        e = edge_from_line(line)
        algo.insert_edge(*e)
        # assert algo.is_valid_mis()

    end = timer()
    t = end - start

    # valid = algo.is_valid_mis()
    valid = True
    msg = "[ OK ]" if valid else "[FAIL]"
    print("Result is: " + msg)
    print("Completed Benchmark {} in t={}".format(benchmark_name, t))
    return t, valid


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


def image(algo):
    g = algo.graph()
    nodes = g.nodes

    def color(v):
        return node_color_in if algo.is_in_mis(v) else node_color_out

    colors = [color(v) for v in nodes]

    nx.draw_networkx(g, node_color=colors)


def filtered_edge_insert(g: nx.Graph, edges):
    # check that node is already in graph: else networkx will create that node and we don't want that
    def both_nodes_exist(e):
        return g.has_node(e[0]) and g.has_node(e[1])

    edges = filter(both_nodes_exist, edges)
    g.add_edges_from(edges)

