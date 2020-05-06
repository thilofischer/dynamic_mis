import matplotlib.pyplot as plt
import matplotlib.animation as animation
from algorithm import *
import numpy.random as npr

node_color_in = 'orangered'
node_color_out = 'royalblue'


class History:
    def __init__(self):
        self._nodes = []
        self._edges = []
        self._mis = []

    def append(self, algo: MISAlgorithm):
        g = algo.graph()
        self._nodes.append(set(g.nodes))
        self._edges.append(set(g.edges))
        self._mis.append(set(algo.get_mis()))

    def animate(self):
        all_nodes = set.union(*self._nodes)
        all_edges = set.union(*self._edges)

        # Calculate the layout w.r.t. the graph with most possible nodes and edges
        maximal_graph = nx.Graph()
        maximal_graph.add_nodes_from(all_nodes)
        maximal_graph.add_edges_from(all_edges)
        layout = nx.spring_layout(maximal_graph)

        # fig, ax = plt.subplots(figsize=(1, 1))
        fig, ax = plt.subplots()

        def update(num):
            ax.clear()
            plt.ylim(top=1.1, bottom=-1.1)
            plt.xlim(left=-1.1, right=1.1)

            non_mis = nx.draw_networkx_nodes(maximal_graph, pos=layout, nodelist=self._nodes[num] - self._mis[num],
                                             node_color=node_color_out, ax=ax)
            # non_mis.set_edgecolor("dimgray")

            mis_nodes = nx.draw_networkx_nodes(max, pos=layout, nodelist=self._mis[num], node_color=node_color_in,
                                               ax=ax)
            mis_nodes.set_edgecolor("orange")
            nx.draw_networkx_edges(maximal_graph, pos=layout, edgelist=self._edges[num], ax=ax)

            ax.set_title("Frame {}".format(num + 1), fontweight="bold")
            return fig

        plt.ylim(0, 1)
        plt.xlim(0, 1)
        ani = animation.FuncAnimation(fig, update, frames=len(self._nodes), interval=1500, repeat=True)
        plt.show(block=True)
        return ani


class Update:
    NODE_INSERT = 0
    NODE_REMOVE = 1
    EDGE_INSERT = 2
    EDGE_REMOVE = 3

    def __init__(self, action, value):
        self._action = action
        self._value = value

    def perform_on(self, algo: MISAlgorithm, history=None):
        if self._action == Update.NODE_INSERT:
            algo.insert_node(*self._value)
        elif self._action == Update.NODE_REMOVE:
            algo.remove_node(self._value)
        elif self._action == self.EDGE_INSERT:
            algo.insert_edge(*self._value)
        elif self._action == self.EDGE_REMOVE:
            algo.remove_edge(*self._value)
        else:
            raise ValueError

        if history is not None:
            history.append(algo)

    def __str__(self):
        return str(self._action) + " " + str(self._value)


def image(algo: MISAlgorithm):
    g = algo.graph()
    nodes = g.nodes

    def color(v):
        return node_color_in if algo.is_in_mis(v) else node_color_out

    colors = [color(v) for v in nodes]

    nx.draw_networkx(g, node_color=colors)


def _sample_animation():
    rnd = npr.RandomState(seed=78)
    hist = History()

    source = nx.gnp_random_graph(20, 0.3, seed=1234)
    initial_nodes = rnd.choice(source.nodes, size=5)
    initial = nx.Graph(source.subgraph(initial_nodes))

    algo = SimpleMIS(initial)
    hist.append(algo)

    for _ in range(3):
        update = random_update(rnd, source, algo.graph())
        print(update)
        update.perform_on(algo, history=hist)

    ani = hist.animate()
    ani.save('sample_animation.gif', writer='imagemagick')


def random_update(rnd: npr.RandomState, source: nx.Graph, target: nx.Graph, update_types):

    action = random_action(rnd, source, target, update_types)

    if action is None:
        return None

    if action == Update.NODE_INSERT:
        node = random_node(rnd, source)
        edges = source.edges(node)
        value = (node, edges)
    elif action == Update.NODE_REMOVE:
        value = random_node(rnd, target)
    elif action == Update.EDGE_INSERT:
        value = random_edge(rnd, source)
    elif action == Update.EDGE_REMOVE:
        value = random_edge(rnd, target)
    else:
        raise ValueError

    assert value is not None
    return Update(action, value)


def random_action(rnd, source: nx.Graph, target: nx.Graph, update_types):
    valid_actions = []

    if len(source.nodes) > 0 and Update.NODE_INSERT in update_types:
        valid_actions.append(Update.NODE_INSERT)

    if len(target.nodes) > 0 and Update.NODE_REMOVE in update_types:
        valid_actions.append(Update.NODE_REMOVE)

    if len(source.edges) > 0 and Update.EDGE_INSERT in update_types:
        valid_actions.append(Update.EDGE_INSERT)

    if len(target.edges) > 0 and Update.EDGE_REMOVE in update_types:
        valid_actions.append(Update.EDGE_REMOVE)

    if len(valid_actions) == 0:
        return None
    else:
        return rnd.choice(valid_actions)


def random_node(rnd: npr.RandomState, graph: nx.Graph):
    nodes = list(graph.nodes)
    if len(nodes) > 0:
        return rnd.choice(nodes)
    else:
        raise ValueError('Graph does not contain any nodes')


def random_edge(rnd: npr.RandomState, graph: nx.Graph):
    edges = list(graph.edges)
    if len(edges) > 0:
        i = rnd.choice(len(edges))
        return edges[i]
    else:
        raise ValueError('Graph does not contain any edges')


if __name__ == '__main__':
    _sample_animation()
