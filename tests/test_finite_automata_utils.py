import pytest
import pydot
import project.finite_automata_utils as fa_utils
from pyformlang.regular_expression import *
import project.graph_utils as g_utils
import networkx as nx


def setup_module(module):
    ...


def teardown_module(module):
    ...


def test_build_DFA_from_python_regexp():
    dfa = fa_utils.build_DFA_from_python_regexp("Help .*")
    assert dfa.accepts("Help me")
    assert dfa.accepts("Help yourself")
    assert dfa.accepts("Help ")

    assert not dfa.accepts("Help")
    assert not dfa.accepts("Lol")
    assert not dfa.accepts("Help3")

    assert dfa.accepts(["H", "e", "l", "p", " "])


def test_build_from_graph():
    ndfa = fa_utils.build_NDFA_from_graph(g_utils.get_graph("bzip"))

    assert len(ndfa.states) == len(g_utils.get_graph("bzip").nodes)
    assert len(ndfa.start_states) == len(ndfa.states)
    assert len(ndfa.final_states) == len(ndfa.states)

    ndfa = fa_utils.build_NDFA_from_graph(
        g_utils.get_graph("bzip"), start=[1, 77, 294], final=[10]
    )

    assert len(ndfa.states) == len(g_utils.get_graph("bzip").nodes)
    assert ndfa.start_states == set([1, 77, 294])
    assert ndfa.final_states == set([10])


def test_intersect_fa():
    fa1 = fa_utils.build_DFA_from_python_regexp("Hello.*")
    fa2 = fa_utils.build_DFA_from_python_regexp(".* world!")
    fai = fa_utils.intersect_FA(fa1, fa2)

    assert fa1.accepts("Hello")
    assert fa2.accepts(" world!")

    assert fa1.accepts("Hello world!")
    assert fa2.accepts("Hello world!")

    assert fai.accepts("Hello world!")
    assert fai.accepts("Hello, beautiful world!")
    assert not fai.accepts("Hello")
    assert not fai.accepts(" world!")

    assert fa1.get_intersection(fa2).is_equivalent_to(fai)


def test_query_graph_with_python_regexp():
    start = [1, 2, 3]
    final = [4, 5, 6]

    graph = nx.from_edgelist(
        [
            (1, 4, {"label": "a"}),
            (2, 5, {"label": "b"}),
            (3, 6, {"label": "c"}),
        ]
    )

    regexp = "a|b"

    assert Regex(regexp).accepts("a")
    assert Regex(regexp).accepts("b")
    assert not Regex(regexp).accepts("c")

    result = fa_utils.query_graph_with_regexp(graph, start, final, regexp)

    assert {(1, 4), (2, 5)} == set(result)
