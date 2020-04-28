import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from typing import List
import algorithm

node_color_in = "#ff9800"
node_color_out = "#82aaff"


def mis(algo: algorithm.MISAlgorithm):
    g = algo.graph()
    nodes = g.nodes

    def color(v):
        return node_color_in if algo.is_in_mis(v) else node_color_out
    colors = [color(v) for v in nodes]

    nx.draw_networkx(g, node_color=colors)


def animate(node_history: List[set], mis_history: List[set], edge_history: List[set]):
    all_nodes = set.union(*node_history)
    all_edges = set.union(*edge_history)

    maximal_graph = nx.Graph()
    maximal_graph.add_nodes_from(all_nodes)
    maximal_graph.add_edges_from(all_edges)

    layout = nx.spring_layout(maximal_graph)

    fig, ax = plt.subplots(figsize=(6, 4))

    def update(num):
        ax.clear()

        not_in_graph = nx.draw_networkx_nodes(maximal_graph, pos=layout, nodelist=all_nodes - node_history[num], node_color="gray",  ax=ax)

        nx.draw_networkx_edges(maximal_graph, pos=layout, edgelist=edge_history[num], ax=ax, edge_color="gray")

        non_mis = nx.draw_networkx_nodes(maximal_graph, pos=layout, nodelist=node_history[num] - mis_history[num], node_color=node_color_out,  ax=ax)
        non_mis.set_edgecolor("black")

        query_nodes = nx.draw_networkx_nodes(max, pos=layout, nodelist=mis_history[num], node_color=node_color_in, ax=ax)
        query_nodes.set_edgecolor("red")

        # Scale plot ax
        ax.set_title("Frame {}".format(num+1), fontweight="bold")
        # ax.set_xticks([])
        # ax.set_yticks([])
        return fig

    ani = animation.FuncAnimation(fig, update, frames=len(node_history), interval=1000, repeat=True)
    plt.show()
    return ani


node_history = [{1,2}, {1,2,3}]
mis_history = [{1}, {1,3}]
edge_history = [{(1,2)}, {(1,2)}]

