import networkx as nx
from antlr4 import *

from pyformlang.finite_automaton import *
from pyformlang.regular_expression import *

import project.cfg_utils
from gen.GramLexer import GramLexer
from gen.GramParser import GramParser
from gen.GramVisitor import GramVisitor
import graph_utils as gu
import finite_automata_utils as fau


class Visitor(GramVisitor):
    class ID:
        def __init__(self, val: str):
            self.value = val

    def __init__(self):
        self.vars = dict()

    def extractExprResult(self, expr_ctx):
        expr_r = expr_ctx.accept(self)
        if isinstance(expr_r, Visitor.ID):
            return expr_r.value
        else:
            return expr_r

    # Visit a parse tree produced by GramParser#op.
    def visitOp(self, ctx: GramParser.OpContext):
        expr_c = ctx.expr()
        if isinstance(expr_c, list):
            expr1_c, expr2_c = expr_c
        else:
            expr1_c, expr_c = expr_c, None

        op_c: GramParser.OperatorContext = ctx.operator()

        expr1_r = self.extractExprResult(expr1_c)
        expr2_r = self.extractExprResult(expr2_c)

        op = op_c.accept(self)

        if not isinstance(expr1_r, nx.MultiDiGraph):
            raise Exception(f"Type {type(expr1_r)} is not valid for \"{op}\" operation")

        result = EpsilonNFA.from_networkx(expr1_r)

        if op == 'set_final':
            if not isinstance(expr2_r, set):
                raise Exception(f"Type {type(expr2_r)} is not valid for \"{op}\" operation")
            result.final_states.clear()
            result.final_states.update(expr2_r)

        elif op == 'set_start':
            if not isinstance(expr2_r, set):
                raise Exception(f"Type {type(expr2_r)} is not valid for \"{op}\" operation")
            result.start_states.clear()
            result.start_states.update(expr2_r)

        elif op == 'add_start':
            if not isinstance(expr2_r, set):
                raise Exception(f"Type {type(expr2_r)} is not valid for \"{op}\" operation")
            result.start_states.update(expr2_r)

        elif op == 'add_final':
            if not isinstance(expr2_r, set):
                raise Exception(f"Type {type(expr2_r)} is not valid for \"{op}\" operation")
            result.final_states.update(expr2_r)

        elif op == 'get_start':
            if expr2_r is not None:
                raise Exception(f"No argument is needed in \"{op}\" operation")
            return set(result.start_states)

        elif op == 'get_final':
            if expr2_r is not None:
                raise Exception(f"No argument is needed in \"{op}\" operation")
            return set(result.final_states)

        elif op == 'get_reachable':
            if expr2_r is not None:
                raise Exception(f"No argument is needed in \"{op}\" operation")
            t: nx.MultiDiGraph = nx.transitive_closure(expr1_r)
            result = set()
            for e in t.edges:
                result.add((e[0], e[1]))
            return result

        elif op == 'get_vertices':
            if expr2_r is not None:
                raise Exception(f"No argument is needed in \"{op}\" operation")
            return set(expr1_r.nodes)

        elif op == 'get_edges':
            if expr2_r is not None:
                raise Exception(f"No argument is needed in \"{op}\" operation")
            return set(expr1_r.edges)

        elif op == 'get_labels':
            if expr2_r is not None:
                raise Exception(f"No argument is needed in \"{op}\" operation")
            return set(expr1_r.nodes.data('label'))

        else:
            raise Exception("You should not be here")

    # Visit a parse tree produced by GramParser#intersect.
    def visitIntersect(self, ctx: GramParser.IntersectContext):
        expr1_c, expr2_c = ctx.expr()
        g1 = self.extractExprResult(expr1_c)
        g2 = self.extractExprResult(expr2_c)

        if isinstance(g1, nx.MultiDiGraph) and isinstance(g2, nx.MultiDiGraph):
            return nx.intersection(g1, g2)
        elif isinstance(g1, set) and isinstance(g2, set):
            return g1 & g2
        else:
            raise Exception(f"Types {type(g1)} and {type(g2)} are not valid for intersect operation")

    # Visit a parse tree produced by GramParser#concat.
    def visitConcat(self, ctx: GramParser.ConcatContext):
        expr1_c, expr2_c = ctx.expr()
        g1 = self.extractExprResult(expr1_c)
        g2 = self.extractExprResult(expr2_c)

        if isinstance(g1, nx.MultiDiGraph) and isinstance(g2, nx.MultiDiGraph):
            return EpsilonNFA.from_networkx(g1).concatenate(EpsilonNFA.from_networkx(g2)).to_networkx()
        else:
            raise Exception(f"Types {type(g1)} and {type(g2)} are not valid for concat operation")

    # Visit a parse tree produced by GramParser#union.
    def visitUnion(self, ctx: GramParser.UnionContext):
        expr1_c, expr2_c = ctx.expr()
        g1 = self.extractExprResult(expr1_c)
        g2 = self.extractExprResult(expr2_c)

        if isinstance(g1, nx.MultiDiGraph) and isinstance(g2, nx.MultiDiGraph):
            return nx.union(g1, g2)
        elif isinstance(g1, set) and isinstance(g2, set):
            return g1 | g2
        else:
            raise Exception(f"Types {type(g1)} and {type(g2)} are not valid for union operation")

    # Visit a parse tree produced by GramParser#star.
    def visitStar(self, ctx: GramParser.StarContext):
        expr_c = ctx.expr()
        g = self.extractExprResult(expr_c)

        if not isinstance(g, nx.MultiDiGraph):
            raise Exception(f"Type {type(g)} is not valid for star operation")

        return EpsilonNFA.from_networkx(g).kleene_star().to_networkx()

    # Visit a parse tree produced by GramParser#var.
    def visitVar(self, ctx: GramParser.VarContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GramParser#symb.
    def visitSymb(self, ctx: GramParser.SymbContext):
        str_c: GramParser.StringContext = ctx.STRING()
        symb = str_c.accept(self)
        result: EpsilonNFA = Regex(symb).to_epsilon_nfa()
        return result.to_networkx()

    # Visit a parse tree produced by GramParser#print.
    def visitPrint(self, ctx: GramParser.PrintContext):
        expr_c: GramParser.ExprContext = ctx.expr()
        expr_r = self.extractExprResult(expr_c)

        if isinstance(expr_r, nx.MultiDiGraph):
            print(nx.nx_pydot.to_pydot(expr_r).to_string())
        else:
            print(expr_r)

    # Visit a parse tree produced by GramParser#bind.
    def visitBind(self, ctx: GramParser.BindContext):
        id_c: GramParser.IdContext = ctx.id_()
        expr_c: GramParser.ExprContext = ctx.expr()
        self.vars[id_c.accept(self)] = self.extractExprResult(expr_c)

    # Visit a parse tree produced by GramParser#load.
    def visitLoad(self, ctx: GramParser.LoadContext):
        path_c: GramParser.StringContext = ctx.v()
        return gu.get_graph(path_c.accept(self))

    # Visit a parse tree produced by GramParser#map.
    def visitMap(self, ctx: GramParser.MapContext):
        expr_c: GramParser.ExprContext = ctx.expr()
        lambda_c: GramParser.LambdaContext = ctx.lambda_()

        expr_res = expr_c.accept(self)

        if isinstance(expr_res, set):
            s = expr_res
        elif isinstance(expr_res, Visitor.ID):
            id = expr_res.value
            if id not in self.vars:
                raise Exception(f"Var \"{id}\" is not found")

            s = self.vars[id]

            if not isinstance(s, set):
                raise Exception(f"\"{type(s)}\" is not a valid type for map")
        else:
            raise Exception(f"\"{type(expr_res)}\" is not a valid type for map")

        lam: callable = lambda_c.accept(self)

        return set(lam(s))

    # Visit a parse tree produced by GramParser#filter.
    def visitFilter(self, ctx: GramParser.FilterContext):
        expr_c: GramParser.ExprContext = ctx.expr()
        lambda_c: GramParser.LambdaContext = ctx.lambda_()

        expr_res = expr_c.accept(self)

        if isinstance(expr_res, set):
            s = expr_res
        elif isinstance(expr_res, Visitor.ID):
            id = expr_res.value
            if id not in self.vars:
                raise Exception(f"Var \"{id}\" is not found")

            s = self.vars[id]

            if not isinstance(s, set):
                raise Exception(f"\"{type(s)}\" is not a valid type for map")
        else:
            raise Exception(f"\"{type(expr_res)}\" is not a valid type for map")

        lam: callable = lambda_c.accept(self)

        r = list(s)
        result = []
        for flag, val in zip(lam(s), r):
            if flag: r.append(val)
        return set(result)

    # Visit a parse tree produced by GramParser#lambda.
    def visitLambda(self, ctx: GramParser.LambdaContext):
        id_c: GramParser.IdContext = ctx.id_()
        code_c: GramParser.CodeContext = ctx.code()

        id = id_c.accept(self)
        code = code_c.accept(self)

        def func(s: set):
            result = list()
            for i in s:
                r = None
                exec(f'r = lambda {id}:{code}({i})', self.vars)
                result.append(r)
            return result

        return func

    # Visit a parse tree produced by GramParser#id.
    def visitId(self, ctx: GramParser.IdContext):
        return Visitor.ID(ctx.getText())

    # Visit a parse tree produced by GramParser#string.
    def visitString(self, ctx: GramParser.StringContext):
        return str(ctx.value())

    # Visit a parse tree produced by GramParser#int.
    def visitInt(self, ctx: GramParser.IntContext):
        return int(ctx.INT())

    # Visit a parse tree produced by GramParser#set.
    def visitSet(self, ctx: GramParser.SetContext):
        v_c = ctx.v()
        if isinstance(v_c, list):
            result = set()
            for c in v_c:
                result.add(c.accept(self))
            return result
        elif v_c is GramParser.VContext:
            return {v_c.accept(self)}
        else:
            return set()

    # Visit a parse tree produced by GramParser#operator.
    def visitOperator(self, ctx: GramParser.OperatorContext):
        return ctx.getText()

    # Visit a parse tree produced by GramParser#code.
    def visitCode(self, ctx: GramParser.CodeContext):
        return ctx.value()

    # Visit a parse tree produced by GramParser#par.
    def visitPar(self, ctx: GramParser.ParContext):
        return self.visitChildren(ctx.expr())
