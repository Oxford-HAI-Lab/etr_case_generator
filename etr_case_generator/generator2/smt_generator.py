import math
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
    obj_name = natural_name_to_logical_name(obj, shorten=name_shortening_scheme)

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
                       # "Total num pieces" refers to the count of variables, so like `(a or b or c) and (d or e)` would have 5 pieces
                       total_num_pieces: int = 5,
                       ) -> SMTProblem:
    # Possible atoms
    # TODO This might be too many or too few, idk
    possible_atoms: list[Symbol] = [random_atom(ontology, ontology.preferred_name_shortening_scheme) for _ in range(total_num_pieces)]

    # The algorithm here is that we generate up to max_num_views views, each of which is a conjunction of disjunctions in CNF
    # There will be exactly num_clauses number of clauses distributed across those views
    # Each clause will have between min_disjuncts_per_clause and max_disjuncts_per_clause disjuncts

    views = cnf_generation(total_num_pieces, possible_atoms)

    print("Got SMT Problem with views:")
    print(views)

    # Now, need to generate some bogus yes/no conclusions
    # For now, just generate some random ones
    # TODO This is a placeholder
    yes_or_no_conclusions = []
    for _ in range(3):
        conclusion = random.choice(possible_atoms)
        is_correct = False
        yes_or_no_conclusions.append((conclusion, is_correct))
    # Mark one as true
    yes_or_no_conclusions[0] = (yes_or_no_conclusions[0][0], True)

    smt_problem = SMTProblem(
        views=views,
        views_cnf=views,  # Because of the way we construct it...
        yes_or_no_conclusions=yes_or_no_conclusions,
    )

    return smt_problem


def cnf_generation(total_num_pieces: int, possible_atoms: list[Symbol]) -> list[FNode]:
    # TODO, this doesn't reflect total_num_pieces perfectly
    max_disjuncts_per_clause = 4
    max_num_views = 3
    min_disjuncts_per_clause = 2
    # num_clauses = int(total_num_pieces / 2.5)

    # Distribute clauses across views
    num_pieces_per_view = [0] * max_num_views
    for i in range(total_num_pieces):
        num_pieces_per_view[random.randint(0, len(num_pieces_per_view) - 1)] += 1
    num_pieces_per_view = [nc for nc in num_pieces_per_view if nc > 0]

    num_pieces_remaining = total_num_pieces

    views = []
    for num_pieces_in_view in num_pieces_per_view:
        clauses = []
        pieces_remaining_in_view = num_pieces_in_view
        while pieces_remaining_in_view > 0:
            num_disjuncts = random.randint(min_disjuncts_per_clause, max_disjuncts_per_clause)
            num_disjuncts = min(num_disjuncts, len(possible_atoms))
            num_disjuncts = min(num_disjuncts, num_pieces_remaining)

            if num_disjuncts == 0:
                break

            disjuncts = random.sample(possible_atoms, num_disjuncts)
            clause = Or(disjuncts)
            clauses.append(clause)

            num_pieces_remaining -= num_disjuncts
            pieces_remaining_in_view -= num_disjuncts

        print(f"Built view with {num_pieces_in_view} pieces:")
        print(clauses)
        print(f"Num pieces remaining in view: {pieces_remaining_in_view}")

        if clauses:
            view = And(clauses)
            views.append(view)

    print("Views:")
    print(views)
    print(f"Num pieces remaining: {num_pieces_remaining}")
    return views
