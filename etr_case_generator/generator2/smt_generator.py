import math
from dataclasses import dataclass
import random

from pyetr import FunctionalTerm, PredicateAtom
from pysmt.shortcuts import Symbol, And, Or, Not, Implies, Iff, ForAll, Exists, is_valid, Solver
from typing import List, Union, Optional, cast
from pysmt.fnode import FNode
from pysmt.typing import BOOL, REAL, PySMTType

from etr_case_generator import Ontology
from etr_case_generator.generator2.reified_problem import PartialProblem, ReifiedView, Conclusion
from etr_case_generator.ontology import ELEMENTS, natural_name_to_logical_name, NameShorteningScheme


@dataclass(kw_only=True)
class SMTProblem:
    views: list[FNode] = None
    views_cnf: list[FNode] = None  # Views converted to CNF form

    # Yes or No format
    yes_or_no_conclusions: list[tuple[FNode, bool]] = None  # List of (conclusion, is_correct) pairs

    def to_partial_problem(self) -> PartialProblem:
        premises = []
        for view in self.views:
            premises.append(ReifiedView(logical_form_smt_fnode=view))
        conclusions = []
        for conclusion, is_correct in self.yes_or_no_conclusions:
            conclusions.append(Conclusion(view=ReifiedView(logical_form_smt_fnode=conclusion), is_classically_correct=is_correct))
        return PartialProblem(premises=premises, possible_conclusions_from_logical=conclusions)


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


def smt_atom_from_etr_atom(etr_atom: PredicateAtom) -> Symbol:
    """Convert an ETR PredicateAtom to an SMT Symbol."""
    assert len(etr_atom.terms) == 1, "Only unary predicates are supported"
    assert type(etr_atom.terms[0]) == FunctionalTerm, "Only functional terms are supported"
    return Symbol(
        name=f"{etr_atom.predicate.name}({etr_atom.terms[0].f.name})",
    )


def has_a_good_number_of_necessary_assignments(views: list[FNode], min_solutions: int = 1,
                                               max_solutions: int = 5) -> bool:
    """
    Returns true if the number of possible solutions is within the specified range.

    Args:
        views: List of boolean formula nodes representing the constraints
        min_solutions: Minimum acceptable number of solutions (default: 1)
        max_solutions: Maximum acceptable number of solutions (default: 5)

    Returns:
        bool: True if number of solutions is within [min_solutions, max_solutions], False otherwise
    """
    # print(f"\n=== Checking for {min_solutions}-{max_solutions} solutions ===")
    # print("Input views:")
    # for i, view in enumerate(views):
    #     print(f"  View {i}: {view}")

    premises = And(views)
    # print(f"\nCombined premises: {premises}")

    # Extract all unique predicate applications
    def get_atoms(formula: FNode) -> set[FNode]:
        if formula.is_symbol():
            return {formula}
        return set().union(*(get_atoms(child) for child in formula.args()))

    atoms = set()
    for view in views:
        atoms.update(get_atoms(view))

    # print("\nExtracted atomic predicates:")
    # for atom in atoms:
    #     print(f"  {atom}")

    # Find solutions until we exceed max_solutions or run out
    solutions = []
    solver = Solver()
    solver.add_assertion(premises)

    while len(solutions) <= max_solutions:
        if not solver.solve():
            break

        # Get the current solution
        current_solution = solver.get_model()
        solutions.append(current_solution)

        # print(f"\nFound solution #{len(solutions)}:")
        # for atom in atoms:
        #     print(f"  {atom} = {current_solution.get_value(atom)}")
        #
        # if len(solutions) > max_solutions:
        #     print(f"\nExceeded maximum of {max_solutions} solutions!")
        #     return False

        # Add constraint to exclude this solution
        solution_constraints = []
        for atom in atoms:
            if current_solution.get_value(atom).is_true():
                solution_constraints.append(atom)
            else:
                solution_constraints.append(Not(atom))
        solver.add_assertion(Not(And(solution_constraints)))

    num_solutions = len(solutions)
    # print(f"\nFound {num_solutions} total solutions")

    if num_solutions < min_solutions:
        # print(f"Too few solutions (minimum is {min_solutions})")
        return False
    elif num_solutions > max_solutions:
        # print(f"Too many solutions (maximum is {max_solutions})")
        return False
    else:
        # print(f"Number of solutions ({num_solutions}) is within acceptable range [{min_solutions}, {max_solutions}]")
        return True


def generate_conclusions(views: list[FNode], possible_atoms: list[Symbol], num_wrong: int = 3) -> list[
    tuple[FNode, bool]]:
    """
    Generate conclusions that include compound statements (AND, OR).
    Returns a list of (conclusion, is_correct) pairs where:
    - Correct conclusions are necessarily true/false given the views
    - Wrong conclusions are contingent (could be either true or false)

    Args:
        views: List of boolean formula nodes representing the constraints
        possible_atoms: List of atomic predicates that can be used
        num_wrong: Number of wrong conclusions to generate
    """
    # print("\n=== Generating conclusions ===")
    premises = And(views)
    conclusions = []

    # Helper to test if a formula is necessary (true/false in all models)
    def is_necessary(formula: FNode) -> tuple[bool, bool]:
        """Returns (is_necessary, necessary_value)"""
        # Test if it must be true
        solver_true = Solver()
        solver_true.add_assertion(premises)
        solver_true.add_assertion(Not(formula))
        must_be_true = not solver_true.solve()

        # Test if it must be false
        solver_false = Solver()
        solver_false.add_assertion(premises)
        solver_false.add_assertion(formula)
        must_be_false = not solver_false.solve()

        return (must_be_true or must_be_false, must_be_true)

    # Generate some compound formulas to test
    def generate_compound_formula() -> FNode:
        """Generate a random compound formula"""
        formula_type = random.choice(['ATOM', 'AND', 'OR'])
        if formula_type == 'ATOM':
            return random.choice(possible_atoms)
        elif formula_type == 'AND':
            atoms = random.sample(possible_atoms, 2)
            return And(atoms)
        else:  # OR
            atoms = random.sample(possible_atoms, 2)
            return Or(atoms)

    # First find a correct conclusion (something that's necessary)
    # print("\nLooking for necessary conclusion...")
    attempts = 0
    while len(conclusions) == 0 and attempts < 100:
        attempts += 1
        candidate = generate_compound_formula()
        is_nec, nec_value = is_necessary(candidate)
        if is_nec:
            conclusions.append((candidate, nec_value))
            # print(f"Found necessary {'truth' if nec_value else 'falsehood'}: {candidate}")
            break

    # Now generate wrong conclusions (things that are contingent)
    # print("\nGenerating contingent conclusions...")
    wrong_attempts = 0
    while len(conclusions) < num_wrong + 1 and wrong_attempts < 100:
        wrong_attempts += 1
        candidate = generate_compound_formula()

        # Check if it's contingent (can be both true and false)
        solver_true = Solver()
        solver_true.add_assertion(premises)
        solver_true.add_assertion(candidate)
        can_be_true = solver_true.solve()

        solver_false = Solver()
        solver_false.add_assertion(premises)
        solver_false.add_assertion(Not(candidate))
        can_be_false = solver_false.solve()

        if can_be_true and can_be_false:
            # It's contingent! Add it as a wrong answer
            # print(f"Found contingent statement: {candidate}")
            conclusions.append((candidate, False))

    # print(f"\nGenerated {len(conclusions)} conclusions after {attempts + wrong_attempts} attempts")
    random.shuffle(conclusions)  # Randomize order
    return conclusions


def random_smt_problem(ontology: Ontology=ELEMENTS,
                       # TODO Add these to the args in the main script
                       # "Total num pieces" refers to the count of variables, so like `(a or b or c) and (d or e)` would have 5 pieces
                       total_num_pieces: int = 5,
                       ) -> SMTProblem:
    # Possible atoms
    # TODO This might be too many or too few, idk
    num_generated_atoms = total_num_pieces
    possible_atoms: list[Symbol] = [random_atom(ontology, ontology.preferred_name_shortening_scheme) for _ in range(total_num_pieces * 10)]  # Overgenerate
    possible_atoms = list(set(possible_atoms))  # Remove duplicates from possible_atoms
    possible_atoms = possible_atoms[:num_generated_atoms]  # Trim down to the right number of atoms

    # print("Made this smaller list of atoms for the problem:")
    # print(possible_atoms)

    # The algorithm here is that we generate up to max_num_views views, each of which is a conjunction of disjunctions in CNF
    # There will be exactly num_clauses number of clauses distributed across those views
    # Each clause will have between min_disjuncts_per_clause and max_disjuncts_per_clause disjuncts

    while True:
        views = cnf_generation(total_num_pieces, possible_atoms)

        if has_a_good_number_of_necessary_assignments(views):
            break

    # print("Got SMT Problem with views:")
    # print(views)

    yes_or_no_conclusions = generate_conclusions(views, possible_atoms, num_wrong=3)

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

        # print(f"Built view with {num_pieces_in_view} pieces:")
        # print(clauses)
        # print(f"Num pieces remaining in view: {pieces_remaining_in_view}")

        if clauses:
            view = And(clauses)
            views.append(view)

    # print("Views:")
    # print(views)
    # print(f"Num pieces remaining: {num_pieces_remaining}")
    return views

def add_conclusions(partial_problem: PartialProblem, ontology: Ontology, num_wrong: int = 3):
    # Use the logical forms of the premises to get possibly relevant atoms for the
    # conclusions
    possible_atoms = set()
    assert partial_problem.premises is not None
    for premise in partial_problem.premises:
        assert premise.logical_form_etr_view is not None
        possible_atoms.update(
            [
                smt_atom_from_etr_atom(
                    cast(PredicateAtom, a)
                ) for a in premise.logical_form_etr_view.atoms
            ]
        )

    possible_atoms = list(possible_atoms)[:6]  # Trim down to the right number of atoms

    generated_conclusions = generate_conclusions([p.logical_form_smt_fnode for p in partial_problem.premises], possible_atoms, num_wrong=num_wrong)
    partial_problem.possible_conclusions_from_logical = []
    for conclusion, is_correct in generated_conclusions:
        partial_problem.possible_conclusions_from_logical.append(
            Conclusion(view=ReifiedView(logical_form_smt_fnode=conclusion), is_classically_correct=is_correct))
    partial_problem.fill_out(ontology=ontology)  # Fill out the conclusions
    for c in partial_problem.possible_conclusions_from_logical:
        c.view.english_form += " !!! THIS CONCLUSION IS BOGUS !!!"
