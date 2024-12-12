from dataclasses import dataclass
import random

from pysmt.shortcuts import Symbol, And, Or, Not, Implies, Iff, is_valid
from pysmt.fnode import FNode
from pysmt.typing import BOOL, REAL, PySMTType

from etr_case_generator import Ontology
from etr_case_generator.ontology import ELEMENTS, natural_name_to_logical_name


@dataclass(kw_only=True)
class SMTProblem:
    views: list[FNode] = None

    # Yes or No format
    yes_or_no_conclusion_correct: FNode = None
    yes_or_no_conclusion_incorrect: FNode = None  # Distractor


def random_smt_problem(num_clauses: int=3, num_steps: int=3, ontology: Ontology=ELEMENTS) -> SMTProblem:
    """Generate a random SMT problem using predicates and objects from the ontology.
    
    Args:
        num_clauses: Number of views/statements to generate
        num_steps: Number of logical operations to apply in each statement
        ontology: The ontology containing predicates and objects to use
    """
    def random_operator():
        """Return a random logical operator"""
        return random.choice([And, Or, Not, Implies, Iff])

    def random_atom():
        """Generate a random atomic predicate application"""
        predicate = random.choice(ontology.predicates)
        # For now we only handle arity=1 predicates
        obj = random.choice(ontology.objects)
        # Create symbol like "red(ace)" or "magnetic(elementium)"
        return Symbol(f"{natural_name_to_logical_name(predicate.name)}({natural_name_to_logical_name(obj)})", BOOL)

    def random_term(depth=0):
        """Generate a random term with bounded depth"""
        if depth >= 2 or random.random() < 0.4:  # Base case
            return random_atom()
        
        operator = random_operator()
        if operator == Not:
            return operator(random_term(depth + 1))
        else:
            return operator(random_term(depth + 1), random_term(depth + 1))

    # Generate random views
    views = []
    for _ in range(num_clauses):
        statement = random_term()
        views.append(statement)

    return SMTProblem(views=views)
