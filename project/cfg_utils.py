from collections import defaultdict
from copy import deepcopy
from pyformlang.cfg import *
from scipy.sparse import *
import networkx as nx


def read_cfg_from_file(path: str) -> CFG:
    """
    Returns CFG built from the text file
    :param path: path to the file with CFG description
    :return: CFG built by description in file
    """
    with open(path) as file:
        return CFG.from_text(file.read())


def to_wcnf(cfg: CFG) -> CFG:
    """
    Returns CFG in Weak Normal Chomsky Form that is equivalent to the original
    :param cfg: original CFG
    :return: CFG equivalent to the original but in Weak Normal Chomsky Form
    """
    cfg = cfg.eliminate_unit_productions()
    cfg = cfg.remove_useless_symbols()

    prods = cfg._get_productions_with_only_single_terminals()
    prods = cfg._decompose_productions(prods)
    return CFG(start_symbol=cfg.start_symbol, productions=prods)


def matrix_alg(graph: nx.DiGraph, cfg: CFG):
    """
    Matrix algorithm for all nodes reachability
    """

    cfg = to_wcnf(cfg)

    edges = defaultdict(set)

    for v, u, l in graph.edges.data("label"):
        edges[l].add((v, u))

    matrix_size = graph.number_of_nodes()

    m0 = defaultdict(lambda: csr_matrix((matrix_size, matrix_size), dtype=bool))

    for p in cfg.productions:
        if len(p.body) == 0:
            for i in range(matrix_size):
                m0[p.head][i, i] = True
        if len(p.body) != 1:
            continue
        for i, j in edges[p.body[0].value]:
            m0[p.head][i, j] = True

    prev = None

    def check_bool_dec(m1: dict, m2: dict):
        if m2.keys() != m1.keys():
            return False
        for k in m1.keys():
            if (m1[k] != m2[k]).sum() != 0:
                return False
        return True

    while True:
        if prev is not None and check_bool_dec(prev, m0):
            break
        prev = deepcopy(m0)
        for p in cfg.productions:
            if len(p.body) != 2:
                continue
            m0[p.head] += m0[p.body[0]] @ m0[p.body[1]]

    return prev


def query_matrix(
    graph: nx.DiGraph, cfg: CFG, start: set = None, final: set = None, nonterminal=None
):
    """
    Solves reachability problem for graph and CFG for provided start, final nodes and nonterminal symbol
    """
    if start is None:
        start = set(graph.nodes)

    if final is None:
        final = set(graph.nodes)

    if nonterminal is None:
        nonterminal = cfg.start_symbol

    result = set()
    for n, matr in matrix_alg(graph, cfg).items():
        for v, u in zip(*matr.nonzero()):
            if n == nonterminal and v in start and u in final:
                result.add((v, u))

    return result
