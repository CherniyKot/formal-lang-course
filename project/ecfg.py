from collections import defaultdict
from pyformlang.finite_automaton.state import State
from pyformlang.cfg import CFG
from pyformlang.finite_automaton import *
from pyformlang.regular_expression import Regex

from project.rfa import RFA


class ECFG:
    """
    Represents extended context-free grammar
    """

    def __init__(self, start: State = None, transitions: dict[State, Regex] = None):
        self.start = start
        self.transitions = transitions if transitions is not None else {}

    @staticmethod
    def read_from_text(text: str):
        """
        Parces ECFG from text
        """
        result = ECFG()

        for line in text.splitlines():
            h, t = line.split("->")

            nt = h.strip()
            if result.start is None:
                result.start = State(nt)

            r = t.strip()
            result.transitions[State(nt)] = Regex(r)

        return result

    @staticmethod
    def read_from_file(path: str):
        """
        Parces ECFG from file
        """
        return ECFG.read_from_text(open(path).read())

    def to_rfa(self):
        """
        Transforms ECFG to RFA
        """
        return RFA(
            self.start, {s: r.to_epsilon_nfa() for s, r in self.transitions.items()}
        )

    @staticmethod
    def from_CFG(cfg: CFG):
        """
        Transforms CFG to ECFG
        """
        result = ECFG()
        result.start = cfg.start_symbol

        tr = defaultdict(list)

        for p in cfg.productions:
            tr[p.head].append(
                " ".join(map(lambda t: t.value, p.body)) if len(p.body) > 0 else "$"
            )
        for h, b in tr.items():
            result.transitions[State(h)] = Regex("|".join(b))
        return result
