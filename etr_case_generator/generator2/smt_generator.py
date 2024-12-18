from dataclasses import dataclass
import random

from pysmt.shortcuts import Symbol, And, Or, Not, Implies, Iff, ForAll, Exists, is_valid, Solver
from typing import List, Union, Optional
from pysmt.fnode import FNode
from pysmt.typing import BOOL, REAL, PySMTType

from etr_case_generator import Ontology
from etr_case_generator.ontology import ELEMENTS, natural_name_to_logical_name, NameShorteningScheme


@dataclass(kw_only=True)
class SMTProblem:
    views: list[FNode] = None
    views_cnf: list[FNode] = None  # Views converted to CNF form

    # Yes or No format
    yes_or_no_conclusions: list[tuple[FNode, bool]] = None  # List of (conclusion, is_correct) pairs


def random_atom(ontology: Ontology, name_shortening_scheme: NameShorteningScheme) -> Symbol:
    """Generate a random atomic predicate application"""
    predicate = random.choice(ontology.predicates)
    pred_name = natural_name_to_logical_name(predicate.name, shorten=name_shortening_scheme)
    # For now we only handle arity=1 predicates
    obj = random.choice(ontology.objects)
    obj_name = {natural_name_to_logical_name(obj, shorten=name_shortening_scheme)}
    # Create symbol like "red(ace)" or "magnetic(elementium)"
    return Symbol(
        name=f"{pred_name}({obj_name})",
        typename=BOOL
    )


def has_only_one_set_of_necessary_assignments(views: list[FNode]) -> bool:
    """Returns true if only one set of assignments is possible given these views"""
    premises = And(views)
    solver = Solver()
    solver.add_assertion(premises)

    # TODO
    ...


def random_smt_problem(ontology: Ontology=ELEMENTS,
                       # TODO Add these to the args in the main script
                       num_clauses: int = 5,
                       min_disjuncts_per_clause: int = 2,
                       max_disjuncts_per_clause: int = 4,
                       max_num_views: int = 3,
                       ) -> SMTProblem:
    # TODO This needs to be overhauled! This function could be total junk for all I know!

    # Possible atoms
    # TODO This might be too many or too few, idk
    possible_atoms = [random_atom(ontology, ontology.preferred_name_shortening_scheme) for _ in range(num_clauses * min_disjuncts_per_clause // 2)]

    # The algorithm here is that we generate up to max_num_views views, each of which is a conjunction of disjunctions in CNF
    # There will be exactly num_clauses number of clauses distributed across those views
    # Each clause will have between min_disjuncts_per_clause and max_disjuncts_per_clause disjuncts

    # Distribute clauses across views
    num_views = random.randint(1, max_num_views)
    clauses_per_view = [0] * num_views
    for i in range(num_clauses):
        clauses_per_view[random.randint(0, num_views - 1)] += 1

    views = []
    for num_clauses_in_view in clauses_per_view:
        clauses = []
        for _ in range(num_clauses_in_view):
            num_disjuncts = random.randint(min_disjuncts_per_clause, max_disjuncts_per_clause)
            disjuncts = random.sample(possible_atoms, min(num_disjuncts, len(possible_atoms)))
            clause = Or(disjuncts)
            clauses.append(clause)
        
        if clauses:
            view = And(clauses)
            views.append(view)

    return SMTProblem(views=views)
