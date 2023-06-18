import io
import sys

from project import Visitor
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
    assert len(nodes) == 14
    assert len(edges) == 13


def run_visitor(code):
    stream = InputStream(code)

    lexer = GramLexer(stream)
    token_stream = CommonTokenStream(lexer)
    parser = GramParser(token_stream)
    tree = parser.prog()

    visitor = Visitor()

    visitor.visit(tree)


def test_interpreter_basic():
    result = io.StringIO()
    with result as sys.stdout:
        run_visitor("print((<hello>:<world>).get_labels());")
        assert set(result.getvalue().strip()[1:-1].split(", ")) == {"hello", "world"}


def test_interpreter_load():
    result = io.StringIO()
    with result as sys.stdout:
        run_visitor("t =load('bzip'); print(t.get_vertices());print(t.get_edges());")
        result = result.getvalue().splitlines()
        assert len(result[0].strip()[1:-1].split(", ")) == 632
        assert len(result[1].strip()[1:-1].split("), (")) == 556


def test_interpreter_lambda():
    result = io.StringIO()
    with result as sys.stdout:
        run_visitor(
            "t =[1,2,3,4]; print(t.map(x=>{{x*x}}));print(t.filter(x=>{{x%2==0}}));"
        )
        result = result.getvalue().splitlines()
        assert result[0].strip()[1:-1].split(", ") == ["1", "4", "9", "16"]
        assert result[1].strip()[1:-1].split(", ") == ["2", "4"]


def test_interpreter_sets_and_lists():
    result = io.StringIO()
    with result as sys.stdout:
        run_visitor("t =[1,2,3,4];print(t); print(set(t)); print(list(set(t)));")
        result = result.getvalue().splitlines()
        assert result[0].strip() == "[1, 2, 3, 4]"
        assert result[1].strip() == "{1, 2, 3, 4}"
        assert result[2].strip() == "[1, 2, 3, 4]"


def test_interpreter_start_final():
    result = io.StringIO()
    code = (
        "t =load('bzip'); print(t.get_start());print(t.get_final());"
        "t1 = t.set_start({1,2,3}).set_final({4,5});"
        "print(t1.get_start()); print(t1.get_final());"
    )
    with result as sys.stdout:
        run_visitor(code)
        result = result.getvalue().splitlines()
        assert len(result[0].strip()[1:-1].split(", ")) == 632
        assert len(result[1].strip()[1:-1].split(", ")) == 632
        assert result[2].strip() == "{1, 2, 3}"
        assert result[3].strip() == "{4, 5}"
