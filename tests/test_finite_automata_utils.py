import pytest
import pydot
import project.finite_automata_utils as fa_utils
from pyformlang.regular_expression import *
import project.graph_utils as g_utils


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
