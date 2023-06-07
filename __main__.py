import sys

from antlr4 import FileStream, CommonTokenStream

from gen.GramLexer import GramLexer
from gen.GramParser import GramParser
from project.interpreter import Visitor


stream = FileStream(sys.argv[1])

lexer = GramLexer(stream)
token_stream = CommonTokenStream(lexer)
parser = GramParser(token_stream)
tree = parser.prog()

visitor = Visitor()

visitor.visit(tree)
