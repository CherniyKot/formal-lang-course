from project.lang_utils import *


def setup_module(module):
    ...


def teardown_module(module):
    ...


def test_grammar_check():
    assert check_code("t=5;")
    assert not check_code("t5")

    assert not check_code("t=5")

    assert check_code("r=load('somefile');g=load('someotherfile');print(g|r);")


def test_dot_1():
    r = convert_to_dot("f=5;r=load('somefile');g=load('someotherfile');print(g|r);")
    assert r.to_string() != ""

    nodes = r.get_nodes()
    edges = r.get_edges()

    assert len(list(filter(lambda x: x.get("label") == "sentence", nodes))) == 4
    assert len(list(filter(lambda x: x.get("label") == "expr", nodes))) == 6
    assert len(list(filter(lambda x: x.get("label") == "id", nodes))) == 5
    assert len(nodes) == 19
    assert len(edges) == 18


def test_dot_2():
    r = convert_to_dot(
        "p = <Hello>|<World>;print(p.get_vertices().map(y=>{{y in p.states}}));"
    )
    assert r.to_string() != ""

    nodes = r.get_nodes()
    edges = r.get_edges()

    assert len(list(filter(lambda x: x.get("label") == "sentence", nodes))) == 2
    assert len(list(filter(lambda x: x.get("label") == "expr", nodes))) == 6
    assert len(list(filter(lambda x: x.get("label") == "lambda", nodes))) == 1
    assert len(nodes) == 15
    assert len(edges) == 14
