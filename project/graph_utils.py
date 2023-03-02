from collections import namedtuple
import cfpq_data
import networkx
import pydot

GraphDescription = namedtuple(
    "GraphDescription", ["NumberOfNodes", "NumbreOfEdges", "Labels"]
)


def get_graph(name):
    return cfpq_data.graph_from_csv(cfpq_data.download(name))


def describe_graph(graph):
    labels = set(label for _, _, label in graph.edges(data="label"))
    return GraphDescription(graph.number_of_nodes(), graph.number_of_edges(), labels)


def describe_graph_by_name(name):
    graph = get_graph(name)
    return describe_graph(graph)


def save_labeled_two_cycle_graph(path, n, m, labels=("a", "b")):
    graph = cfpq_data.labeled_two_cycles_graph(n, m, labels=labels)
    networkx.drawing.nx_pydot.write_dot(graph, path)
    return graph
