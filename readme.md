
# Dynamic Maximal Independent Sets

<!-- TABLE OF CONTENTS -->
## Table of Contents

* [Introduction](#introdcution)
* [Requirements](#requirements)
* [Usage](#usage)


<!-- Introduction -->
## Introduction

An independent set on a graph is a set of nodes where no two nodes in the set are neighbors.
A maximal independent set (MIS) is an independent set where no node can be added without having two neighbors in the set.

This problem is interesting when we are considering a graph that can be dynamically updated.
Possible updates are removal/insertion of an edge/vertex.

Instead of recomputing the MIS from scratch, it is desirable to re-use information from the old solution. Ideally, this
leads to faster solutions after an update.

This project contains several different algorithms that compute a MIS on a dynamically changeable graph.

* **TrivialMIS**

    The intuitive approach to building a MIS. It completely recomputes the MIS after every update
    
* **SimpleMIS**

    Each vertex keeps a count of how many neighbors are in the MIS. Nodes are added/removed from the MIS based
    on this counter.
    
* **ImprovedIncrementalMIS**
    
    A small change to SimpleMIS, that only implements edge insertions. In the case that both nodes of the edge
    are in the MIS, the node with lower degree will be removed.
    
* **ImprovedDynamicMIS**

    A fully dynamic algorithm, that classifies nodes as either heavy or light based on their degree and performs
    different operations accordingly to achieve lower amortized costs.
    
* **ImplicitMIS**

    In a relaxed model we need not maintain an explicit version of the MIS. Instead this algorithms only saves an 
    independent set. If a node not in this set is part of the MIS is decided lazily.

<!-- Requirements -->
## Requirements

The code was tested using Python 3.8.2.

The requirements are listed in *requirements.txt*.

The code uses the networkx library as the backend for graph operations.

Furthermore numpy.random is used to generate reproducible random numbers.

To visualise and animate the graphs, matplotlib is used.



<!-- USAGE EXAMPLES -->
## Usage

The code can be imported as follows:

```
import dynamic_mis as dm
```

The implemented algorithms all share a common interface.
To create a new instance of an algorithm on a graph call

```
graph = *your networkx graph*
algo = dm.TrivialMIS(graph)
```

where graph is a *networkx* graph.

Information about the maximal independet set is exposed via
two member functions:

```
algo.is_in_mis(node) # Boolean
mis = algo.get_mis() # set object
```

To perform updates to the graph one of these four functions can be used:

```python
algo.insert_edge(u, v)
algo.remove_edge(u, v)

algo.insert_node(v, edges) # The edges parameter is optional
algo.remove_node(v)
```

Note that the complexity of these function calls depends on the specific algorithm.

