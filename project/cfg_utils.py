from pyformlang.cfg import *


def read_cfg_from_file(path: str) -> CFG:
    with open(path) as file:
        return CFG.from_text(file.read())


def to_wcnf(cfg: CFG):
    # Can I not do it manually?
    #
    # terminals = cfg.terminals
    # newSymbols:set[Variable] = set()
    # new_productions:set[Production] = set()
    # for p in cfg.productions:
    #     if len(p.body)>1:
    #         for t in set(p.body) & terminals:
    #             v = Variable(t.value)
    #             while p.body.count(t)>0:
    #                 i = p.body.index(t)
    #                 p.body[i]=v
    #
    #             cfg+= add(v)
    #             new_productions.add(Production(v,[t]))

    prods = cfg._get_productions_with_only_single_terminals()
    prods = cfg._decompose_productions(prods)
    cfg = CFG(start_symbol=cfg.start_symbol, productions=prods)

    cfg = cfg.eliminate_unit_productions()
    cfg = cfg.remove_useless_symbols()
    return cfg
