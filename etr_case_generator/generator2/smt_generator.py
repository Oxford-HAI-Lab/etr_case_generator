from dataclasses import dataclass
import random

from pysmt.shortcuts import Symbol, And, Or, Not, Implies, Iff, ForAll, Exists, is_valid, Solver
from typing import List, Union, Optional
from pysmt.fnode import FNode
from pysmt.typing import BOOL, REAL, PySMTType

from etr_case_generator import Ontology
from etr_case_generator.ontology import ELEMENTS, natural_name_to_logical_name


@dataclass(kw_only=True)
class SMTProblem:
    views: list[FNode] = None
    views_cnf: list[FNode] = None  # Views converted to CNF form

    # Yes or No format
    yes_or_no_conclusions: list[tuple[FNode, bool]] = None  # List of (conclusion, is_correct) pairs


def to_cnf(formula: FNode) -> FNode:
    """Convert formula to Conjunctive Normal Form (CNF)"""
    # First convert implications and iffs
    formula = eliminate_implications(formula)
    
    # Push negations inward using De Morgan's laws
    formula = push_negations(formula)
    
    # Distribute Or over And
    formula = distribute_or_over_and(formula)
    
    return formula

def eliminate_implications(formula: FNode) -> FNode:
    """Eliminate implications and iff from formula"""
    if formula.is_implies():
        # a → b becomes ¬a ∨ b
        a = eliminate_implications(formula.arg(0))
        b = eliminate_implications(formula.arg(1))
        return Or(Not(a), b)
    elif formula.is_iff():
        # a ↔ b becomes (a → b) ∧ (b → a)
        a = eliminate_implications(formula.arg(0))
        b = eliminate_implications(formula.arg(1))
        return And(Or(Not(a), b), Or(Not(b), a))
    elif formula.is_and():
        return And([eliminate_implications(arg) for arg in formula.args()])
    elif formula.is_or():
        return Or([eliminate_implications(arg) for arg in formula.args()])
    elif formula.is_not():
        return Not(eliminate_implications(formula.arg(0)))
    else:
        return formula

def push_negations(formula: FNode) -> FNode:
    """Push negations inward using De Morgan's laws"""
    if formula.is_not():
        child = formula.arg(0)
        if child.is_and():
            # ¬(a ∧ b) becomes ¬a ∨ ¬b
            return Or([push_negations(Not(arg)) for arg in child.args()])
        elif child.is_or():
            # ¬(a ∨ b) becomes ¬a ∧ ¬b
            return And([push_negations(Not(arg)) for arg in child.args()])
        elif child.is_not():
            # ¬¬a becomes a
            return push_negations(child.arg(0))
        else:
            return formula
    elif formula.is_and():
        return And([push_negations(arg) for arg in formula.args()])
    elif formula.is_or():
        return Or([push_negations(arg) for arg in formula.args()])
    else:
        return formula

def distribute_or_over_and(formula: FNode) -> FNode:
    """Distribute Or over And"""
    if formula.is_or():
        # Find any And terms
        and_terms = [arg for arg in formula.args() if arg.is_and()]
        if and_terms:
            # Take first And term and distribute
            and_term = and_terms[0]
            other_terms = [arg for arg in formula.args() if arg is not and_term]
            distributed = [Or(distribute_or_over_and(and_arg), 
                           *[distribute_or_over_and(term) for term in other_terms])
                         for and_arg in and_term.args()]
            return And(distributed)
        else:
            return Or([distribute_or_over_and(arg) for arg in formula.args()])
    elif formula.is_and():
        return And([distribute_or_over_and(arg) for arg in formula.args()])
    return formula


def random_operator(allow_quantifiers=False):
    """Return a random logical operator"""
    basic_ops = [And, Or, Not]  # , Implies, Iff]
    if allow_quantifiers and random.random() < 0.3:  # 30% chance of quantifier
        return random.choice([ForAll, Exists])
    return random.choice(basic_ops)

def random_atom(ontology, args):
    """Generate a random atomic predicate application"""
    predicate = random.choice(ontology.predicates)
    # For now we only handle arity=1 predicates
    obj = random.choice(ontology.objects)
    # Create symbol like "red(ace)" or "magnetic(elementium)"
    return Symbol(f"{natural_name_to_logical_name(predicate.name, shorten=args.name_shortening)}({natural_name_to_logical_name(obj, shorten=args.name_shortening)})", BOOL)

def random_term(ontology, args, depth=0, allow_quantifiers=False):
    """Generate a random term with bounded depth"""
    if depth >= 2 or random.random() < 0.4:  # Base case
        return random_atom(ontology, args)

    operator = random_operator(allow_quantifiers)
    if operator in (ForAll, Exists):
        # For quantifiers, we need a variable and a formula
        var = Symbol(natural_name_to_logical_name(random.choice(ontology.objects), shorten=args.name_shortening), BOOL)
        # Don't allow nested quantifiers
        return operator([var], random_term(depth + 1, allow_quantifiers=False))
    elif operator == Not:
        return operator(random_term(ontology, args, depth + 1))
    else:
        return operator(random_term(ontology, args, depth + 1), random_term(ontology, args, depth + 1))

def has_necessary_assignments(views: list[FNode]) -> bool:
    """Check if the conjunction of views has any necessary assignments"""
    premises = And(views)
    solver = Solver()
    solver.add_assertion(premises)

    # Get all variables used in the formula
    variables = premises.get_free_variables()

    # For each variable, check if it must be True or False
    for var in variables:
        # Check if var must be True
        solver.push()
        solver.add_assertion(Not(var))
        if not solver.solve():
            solver.pop()
            return True
        solver.pop()

        # Check if var must be False
        solver.push()
        solver.add_assertion(var)
        if not solver.solve():
            solver.pop()
            return True
        solver.pop()

    return False


def random_smt_problem(args, num_clauses: int=3, num_steps: int=3, ontology: Ontology=ELEMENTS) -> SMTProblem:
    # TODO This needs to be overhauled! This function could be total junk for all I know!

    # Here's how this function should work:
    # * Ontology needs to have the args.shortening stored on it...
    # * TODO: fill this out
    # * TODO: Delete this junk and have aider regenerate it!

    # Try to generate views with necessary assignments
    max_attempts = 100
    for attempt in range(max_attempts):
        # Generate random views
        views = []
        for _ in range(num_clauses):
            statement = random_term(ontology, args)
            views.append(statement)

        # Check if these views create any necessary assignments
        if has_necessary_assignments(views):
            # Generate conclusions as before
            premises = And(views)
            
            # For correct conclusion: take a subset of the views or weaken with OR
            if random.random() < 0.5 and len(views) > 1:
                subset_size = random.randint(1, len(views) - 1)
                correct_conclusion = And(random.sample(views, subset_size))
            else:
                correct_conclusion = Or(random.choice(views), random_term(ontology, args))
            
            # For incorrect conclusion: strengthen by adding extra conjunction
            new_atom = random_atom(ontology, args)
            while any(new_atom == view for view in views):
                new_atom = random_atom(ontology, args)
            incorrect_conclusion = And(premises, new_atom)
            
            # Convert views to CNF
            views_cnf = [to_cnf(view) for view in views]

            print(f"Generated problem after {attempt + 1} attempts")
            
            return SMTProblem(
                views=views,
                views_cnf=views_cnf,
                yes_or_no_conclusions=[
                    (correct_conclusion, True),
                    (incorrect_conclusion, False)
                ]
            )

    # If we failed to find views with necessary assignments
    raise ValueError(f"Failed to generate problem with necessary assignments after {max_attempts} attempts")
