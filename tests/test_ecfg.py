import pytest
import pydot
from project.ecfg import ECFG
import project.graph_utils as utils
from pyformlang.regular_expression import Regex
from pyformlang.cfg import CFG


def setup_module(module):
    ...


def teardown_module(module):
    ...


def test_ecfg():
    e = ECFG.read_from_text("S -> S|a S|epsilon")
    assert "S" == e.start
    assert (
        Regex("S|a S|epsilon")
        .to_epsilon_nfa()
        .is_equivalent_to(e.transitions["S"].to_epsilon_nfa())
    )

    e = ECFG.read_from_text("St -> S|a A\nS->A\nA ->S|eps")

    assert "St" == e.start
    assert 3 == len(e.transitions.values())

    e = ECFG.from_CFG(CFG.from_text("S->S | a S | $"))

    assert "S" == e.start
    assert (
        Regex("S|a S|epsilon")
        .to_epsilon_nfa()
        .is_equivalent_to(e.transitions["S"].to_epsilon_nfa())
    )
