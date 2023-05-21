import pytest
import pydot
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


def test_dot():
    r = convert_to_dot("f=5;r=load('somefile');g=load('someotherfile');print(g|r);")
    assert r.to_string() != ""
