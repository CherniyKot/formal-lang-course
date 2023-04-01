import networkx as nx
from pyformlang.finite_automaton import *
from pyformlang.regular_expression import *
from scipy.sparse import *


def build_DFA_from_regexp(regexp: str) -> DeterministicFiniteAutomaton:
    """
    Builds DFA from regexp string
    :param regexp: basic regexp string
    :return: DFA equivalent to the regexp
    """
    regexp = Regex(regexp)
    return regexp.to_epsilon_nfa().minimize()


def build_DFA_from_python_regexp(regexp: str) -> DeterministicFiniteAutomaton:
    """
    Builds DFA from python regexp string
    :param regexp: python regexp string
    :return: DFA equivalent to the regexp
    """
    regexp = PythonRegex(regexp)
    return regexp.to_epsilon_nfa().minimize()


def build_NDFA_from_graph(
    graph: nx.DiGraph, start: set[State] = None, final: set[State] = None
) -> EpsilonNFA:
    """
    Builds NDFA from graph representation, start and final nodes
    :param graph: Graph representation of the resulting NDFA
    :param start: Start states of the resulting NDFA. If None - all states are considered start states
    :param final: Final states of the resulting NDFA. If None - all states are considered final states
    :return: NDFA built from graph representation, start and final nodes
    """
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
    """
    Creates a boolean decomposition of the NDFA
    :param fa: NDFA to be decomposed
    :return: Dict of pairs [symbol - adjacency matrix] representing the original NDFA
    """
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
    """
    Intersects two NDFAs
    :param fa1: first NDFA
    :param fa2: second NDFA
    :return: NDFA that accepts only words accepted by both original NDFAs
    """
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


def _find_common_paths_in_FAs(
    fa1: EpsilonNFA, fa2: EpsilonNFA
) -> list[tuple[State, State]]:
    """
    Returns list of pairs [start state - final state] from first NDFA that satisfy both NDFAs
    :param fa1: first NDFA
    :param fa2: second NDFA
    :return: List of pairs [start state - final state] from first NDFA that satisfy both NDFAs
    """
    fai = intersect_FA(fa1, fa2)
    graph = nx.transitive_closure(nx.DiGraph(fai.to_networkx()))
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


def query_graph_with_regexp(
    graph: nx.DiGraph, start: set, final: set, regexp: str
) -> list[tuple]:
    """
    Returns list of pairs [start vertex - final vertex] from graph that satisfy graph as an ANDA and regexp simultaneously
    :param graph: Graph representation of the NDFA
    :param start: Start states of the NDFA. If None - all states are considered start states
    :param final: Final states of the resulting NDFA. If None - all states are considered final states
    :param regexp: basic regexp string
    :return: List of pairs [start vertex - final vertex] from graph that satisfy graph as an ANDA and regexp simultaneously
    """
    fa1 = build_NDFA_from_graph(graph, start, final)
    fa2 = build_DFA_from_regexp(regexp)
    return _find_common_paths_in_FAs(fa1, fa2)


def query_graph_with_python_regexp(
    graph: nx.DiGraph, start: set, final: set, regexp: str
) -> list[tuple]:
    """
    Returns list of pairs [start vertex - final vertex] from graph that satisfy graph as an ANDA and python regexp simultaneously
    :param graph: Graph representation of the NDFA
    :param start: Start states of the NDFA. If None - all states are considered start states
    :param final: Final states of the resulting NDFA. If None - all states are considered final states
    :param regexp: python regexp string
    :return: List of pairs [start vertex - final vertex] from graph that satisfy graph as an ANDA and python regexp simultaneously
    """
    fa1 = build_NDFA_from_graph(graph, start, final)
    fa2 = build_DFA_from_python_regexp(regexp)
    return _find_common_paths_in_FAs(fa1, fa2)
