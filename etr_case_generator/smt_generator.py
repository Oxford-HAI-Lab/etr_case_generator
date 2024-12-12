from dataclasses import dataclass
import random

from pysmt.shortcuts import Symbol, And, Or, Not, Implies, Iff, is_valid
from pysmt.fnode import FNode
from pysmt.typing import BOOL, REAL, PySMTType

from etr_case_generator import Ontology
from etr_case_generator.ontology import ELEMENTS


@dataclass(kw_only=True)
class SMTProblem:
    views: list[FNode] = None

    # Yes or No format
    yes_or_no_conclusion_correct: FNode = None
    yes_or_no_conclusion_incorrect: FNode = None  # Distractor


def random_smt_problem(num_variables: int=3, num_clauses: int=3, min_literals_per_clause: int=3, max_literals_per_clause: int=3, num_steps: int = 3, ontology: Ontology=ELEMENTS) -> SMTProblem:
    # Define a random logical operator generator
    # TODO(andrew) This is shit! It needs to be massively improved.
    def random_operator():
        return random.choice([And, Or, Not])

    # Define a random term generator (variable or NOT variable)
    def random_term(variables):
        var = random.choice(variables)
        if random.choice([True, False]):
            return Not(var)
        return var

    # Create random variables
    variables = [Symbol(f'x{i}', BOOL) for i in range(num_variables)]

    # Generate random views
    views = []
    for _ in range(num_clauses):
        # Start building the random logical statement
        statement = random_term(variables)

        # Randomly apply operators and combine terms
        for _ in range(num_steps):
            operator = random_operator()
            if operator == Not:
                statement = operator(statement)
            else:
                statement = operator(statement, random_term(variables))
        
        views.append(statement)

    return SMTProblem(views=views)
