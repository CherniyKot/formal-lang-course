from pyformlang.finite_automaton.state import State

from pyformlang.finite_automaton import EpsilonNFA

from scipy.sparse import *

from project.finite_automata_utils import convert_FA_to_matrix_form


class RFA:
    """
    Represents recursive finite automaton
    """

    def __init__(
        self, start: State = None, transitions: dict[State, EpsilonNFA] = None
    ):
        """
        :param start: Start state
        :param transitions: Transitions of RFA
        """
        self.start = start
        self.transitions = transitions if transitions is not None else {}

    def to_matrix_form(self):
        """
        Creates a boolean decomposition of the RFA
        """
        result = dict()
        for s, nfa in self.transitions.items():
            result[s] = convert_FA_to_matrix_form(nfa)

        return result

    def minimize(self):
        """
        Returns minimized version of current RFA
        """
        return RFA(
            self.start, {s: nfa.minimize() for s, nfa in self.transitions.items()}
        )
