from pyformlang.cfg import *


def read_cfg_from_file(path: str) -> CFG:
    """
    Returns CFG built from the text file
    :param path: path to the file with CFG description
    :return: CFG built by description in file
    """
    with open(path) as file:
        return CFG.from_text(file.read())


def to_wcnf(cfg: CFG) -> CFG:
    """
    Returns CFG in Weak Normal Chomsky Form that is equivalent to the original
    :param cfg: original CFG
    :return: CFG equivalent to the original but in Weak Normal Chomsky Form
    """
    cfg = cfg.eliminate_unit_productions()
    cfg = cfg.remove_useless_symbols()

    prods = cfg._get_productions_with_only_single_terminals()
    prods = cfg._decompose_productions(prods)
    return CFG(start_symbol=cfg.start_symbol, productions=prods)
