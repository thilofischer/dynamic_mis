import networkx as nx

node_color_in = "orangered"
node_color_out = "blue"


def image(algo):
    g = algo.graph()
    nodes = g.nodes

    def color(v):
        return node_color_in if algo.is_in_mis(v) else node_color_out

    colors = [color(v) for v in nodes]

    nx.draw_networkx(g, node_color=colors)


