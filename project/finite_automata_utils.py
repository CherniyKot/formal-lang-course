from pyformlang.regular_expression import *
from pyformlang.finite_automaton import *
from scipy.sparse import *
import networkx as nx


def build_DFA_from_regexp(regexp) -> DeterministicFiniteAutomaton:
    regexp = Regex(regexp)
    return regexp.to_epsilon_nfa().minimize()


def build_DFA_from_python_regexp(regexp) -> DeterministicFiniteAutomaton:
    regexp = PythonRegex(regexp)
    return regexp.to_epsilon_nfa().minimize()


def build_NDFA_from_graph(graph, start=None, final=None) -> EpsilonNFA:
    ndfa = EpsilonNFA.from_networkx(graph)

    for s, f, label in graph.edges(data="label"):
        ndfa.add_transition(s, label, f)

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


def convert_FA_to_matrix_form(fa: EpsilonNFA) -> dict[any, dok_matrix]:
    result = dict()

    states = list(fa.states)
    matrix_size = len(states)

    for s, symb, f in fa:
        matrix = result.setdefault(
            symb, dok_matrix((matrix_size, matrix_size), dtype=bool)
        )
        matrix[states.index(s), states.index(f)] = True

    return result


def intersect_FA(fa1: EpsilonNFA, fa2: EpsilonNFA) -> EpsilonNFA:
    m1 = convert_FA_to_matrix_form(fa1)
    m2 = convert_FA_to_matrix_form(fa2)
    states1 = list(fa1.states)
    states2 = list(fa2.states)

    result = EpsilonNFA()

    for symb in m1.keys() & m2.keys():
        mi = kron(m1[symb], m2[symb])
        for s, f in zip(*mi.nonzero()):
            result.add_transition(s, symb, f)

    for state1 in fa1.start_states:
        for state2 in fa2.start_states:
            result.add_start_state(
                states1.index(state1) * len(states2) + states2.index(state2)
            )

    for state1 in fa1.final_states:
        for state2 in fa2.final_states:
            result.add_final_state(
                states1.index(state1) * len(states2) + states2.index(state2)
            )

    return result


def _find_common_paths_in_FAs(fa1, fa2):
    fai = intersect_FA(fa1, fa2)
    graph = fai.to_networkx()
    states = list(fa1.states)
    result = []

    for s in fai.start_states:
        for f in fai.final_states:
            if nx.has_path(graph, s, f):
                result.append(
                    (
                        states[s.value // len(fa2.states)],
                        states[f.value // len(fa2.states)],
                    )
                )
    return result


def query_graph_with_regexp(graph, start: set, final: set, regexp: str) -> list[tuple]:
    fa1 = build_NDFA_from_graph(graph, start, final)
    fa2 = build_DFA_from_regexp(regexp)
    return _find_common_paths_in_FAs(fa1, fa2)


def query_graph_with_python_regexp(
    graph, start: set, final: set, regexp: str
) -> list[tuple]:
    fa1 = build_NDFA_from_graph(graph, start, final)
    fa2 = build_DFA_from_python_regexp(regexp)
    return _find_common_paths_in_FAs(fa1, fa2)
