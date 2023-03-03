from pyformlang.regular_expression import *
from pyformlang.finite_automaton import *


def build_DFA_from_regexp(regexp) -> DeterministicFiniteAutomaton:
    regexp = Regex(regexp)
    return regexp.to_epsilon_nfa().minimize()


def build_DFA_from_python_regexp(regexp) -> DeterministicFiniteAutomaton:
    regexp = PythonRegex(regexp)
    return regexp.to_epsilon_nfa().minimize()


def build_NDFA_from_graph(graph, start=None, final=None) -> EpsilonNFA:
    ndfa = EpsilonNFA.from_networkx(graph)

    if start is not None:
        for s in start:
            ndfa.add_start_state(s)
    else:
        for s in ndfa.states:
            ndfa.add_start_state(s)
    if final is not None:
        for s in final:
            ndfa.add_final_state(s)
    else:
        for s in ndfa.states:
            ndfa.add_final_state(s)

    return ndfa
