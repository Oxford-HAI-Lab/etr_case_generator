
from pysmt.shortcuts import Symbol, And, Or, Not, Implies, Iff, ForAll, Exists, is_valid, Solver
from pysmt.fnode import FNode


def does_it_follow(views: list[FNode], conclusion: FNode) -> bool:
    """Check if the conclusion follows from the views"""
    solver = Solver()
    premises = And(views)
    solver.add_assertion(premises)
    solver.add_assertion(Not(conclusion))
    return not solver.solve()
