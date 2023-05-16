from pyformlang.cfg import *
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


def hellings(graph: nx.DiGraph, cfg: CFG):
    # cfg = cfg.to_normal_form()
    cfg = to_wcnf(cfg)
    r = set()
    for p in cfg.productions:
        N = p.head
        if len(p.body) == 0:
            r |= {(N, v, v) for v in graph.nodes.data("label")}
        elif len(p.body) == 1:
            if isinstance(p.body[0], Terminal):
                r |= {
                    (N, v, u)
                    for v, u, s in graph.edges.data("label")
                    if s == p.body[0].value
                }
    r = list(r)
    m = list(r)

    while len(m) != 0:
        N, v, u = m.pop(0)
        for N_, v_, u_ in r:
            if u_ == v:
                for p in cfg.productions:
                    if len(p.body) != 2:
                        continue
                    if p.body[0] != N_ or p.body[1] != N:
                        continue
                    if (p.head, v_, u) in r:
                        continue

                    m.append((p.head, v_, u))
                    r.append((p.head, v_, u))
            if u == v_:
                for p in cfg.productions:
                    if len(p.body) != 2:
                        continue
                    if p.body[0] != N or p.body[1] != N_:
                        continue
                    if (p.head, v, u_) in r:
                        continue

                    m.append((p.head, v, u_))
                    r.append((p.head, v, u_))

    return r


def query_hellings(
    graph: nx.DiGraph, cfg: CFG, start: set = None, final: set = None, nonterminal=None
):
    if start is None:
        start = set(graph.nodes)

    if final is None:
        final = set(graph.nodes)

    if nonterminal is None:
        nonterminal = cfg.start_symbol

    result = set()
    for n, v, u in hellings(graph, cfg):
        if n == nonterminal and v in start and u in final:
            result.add((v, u))

    return result
