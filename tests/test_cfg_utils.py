import os
import tempfile

from pyformlang.cfg import Variable, Terminal, Epsilon, CFG

import project.cfg_utils as c_utils
import networkx as nx


def setup_module(module):
    ...


def teardown_module(module):
    ...


def test_read_cfg_from_file():
    try:
        with tempfile.NamedTemporaryFile(mode="tw+", delete=False) as file:
            file.write("\n".join(["S->A|B|C", "A->a", "B->b", "C->C"]))
            name = file.name
        cfg = c_utils.read_cfg_from_file(name)
        assert cfg.contains("a")
        assert cfg.contains("b")
        assert not cfg.contains("c")
    finally:
        os.remove(name)


def test_wnf():
    try:
        with tempfile.NamedTemporaryFile(mode="tw+", delete=False) as file:
            file.write("\n".join(["S->A B|B S|C", "A->a", "B->b b b", "C->C c"]))
            name = file.name
        cfg = c_utils.read_cfg_from_file(name)
        cfg = c_utils.to_wcnf(cfg)

        assert Variable("A") in cfg.variables
        assert Variable("B") in cfg.variables
        assert Variable("S") in cfg.variables
        assert Variable("C") not in cfg.variables

        assert Terminal("a") in cfg.terminals
        assert Terminal("b") in cfg.terminals
        assert Terminal("c") not in cfg.terminals

        for p in cfg.productions:
            assert (
                len(p.body) == 2
                and isinstance(p.body[0], Variable)
                and isinstance(p.body[1], Variable)
            ) or (
                len(p.body) == 1
                and (isinstance(p.body[0], Terminal) or isinstance(p.body[0], Epsilon))
            )

    finally:
        os.remove(name)


def test_hellings():
    cfg = CFG.from_text("S->A B\n S -> A S1\n S1->S B\n A->a\n B->b")
    graph = nx.MultiDiGraph()
    graph.add_edge(0, 1, label="a")
    graph.add_edge(1, 2, label="a")
    graph.add_edge(2, 0, label="a")
    graph.add_edge(2, 3, label="b")
    graph.add_edge(3, 2, label="b")

    result = c_utils.query_hellings(graph, cfg)
    assert result == {(0, 2), (0, 3), (1, 2), (1, 3), (2, 2), (2, 3)}
