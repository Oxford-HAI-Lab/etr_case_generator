from dataclasses import dataclass
import random

from pysmt.shortcuts import Symbol, And, Or, Not, Implies, Iff, ForAll, Exists, is_valid, Solver
from pysmt.fnode import FNode
from pysmt.typing import BOOL, REAL, PySMTType

from etr_case_generator import Ontology
from etr_case_generator.ontology import ELEMENTS, natural_name_to_logical_name


@dataclass(kw_only=True)
class SMTProblem:
    views: list[FNode] = None

    # Yes or No format
    yes_or_no_conclusions: list[tuple[FNode, bool]] = None  # List of (conclusion, is_correct) pairs


def random_smt_problem(args, num_clauses: int=3, num_steps: int=3, ontology: Ontology=ELEMENTS) -> SMTProblem:
    """Generate a random SMT problem with at least one necessary assignment.
    
    Args:
        num_clauses: Number of views/statements to generate
        num_steps: Number of logical operations to apply in each statement
        ontology: The ontology containing predicates and objects to use
        
    Returns:
        SMTProblem with views that have at least one necessary assignment and conclusions
        using the Logical Strength Method:
        - Correct conclusion is logically weaker than premises
        - Incorrect conclusion is logically stronger than premises
    """
    def random_operator(allow_quantifiers=False):
        """Return a random logical operator"""
        basic_ops = [And, Or, Not]  # , Implies, Iff]
        if allow_quantifiers and random.random() < 0.3:  # 30% chance of quantifier
            return random.choice([ForAll, Exists])
        return random.choice(basic_ops)

    def random_atom():
        """Generate a random atomic predicate application"""
        predicate = random.choice(ontology.predicates)
        # For now we only handle arity=1 predicates
        obj = random.choice(ontology.objects)
        # Create symbol like "red(ace)" or "magnetic(elementium)"
        return Symbol(f"{natural_name_to_logical_name(predicate.name, shorten=args.name_shortening)}({natural_name_to_logical_name(obj, shorten=args.name_shortening)})", BOOL)

    def random_term(depth=0, allow_quantifiers=False):
        """Generate a random term with bounded depth"""
        if depth >= 2 or random.random() < 0.4:  # Base case
            return random_atom()
        
        operator = random_operator(allow_quantifiers)
        if operator in (ForAll, Exists):
            # For quantifiers, we need a variable and a formula
            var = Symbol(natural_name_to_logical_name(random.choice(ontology.objects), shorten=args.name_shortening), BOOL)
            # Don't allow nested quantifiers
            return operator([var], random_term(depth + 1, allow_quantifiers=False))
        elif operator == Not:
            return operator(random_term(depth + 1))
        else:
            return operator(random_term(depth + 1), random_term(depth + 1))

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

    # Try to generate views with necessary assignments
    max_attempts = 100
    for attempt in range(max_attempts):
        # Generate random views
        views = []
        for _ in range(num_clauses):
            statement = random_term()
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
                correct_conclusion = Or(random.choice(views), random_term())
            
            # For incorrect conclusion: strengthen by adding extra conjunction
            new_atom = random_atom()
            while any(new_atom == view for view in views):
                new_atom = random_atom()
            incorrect_conclusion = And(premises, new_atom)
            
            return SMTProblem(
                views=views,
                yes_or_no_conclusions=[
                    (correct_conclusion, True),
                    (incorrect_conclusion, False)
                ]
            )

    # If we failed to find views with necessary assignments
    raise ValueError(f"Failed to generate problem with necessary assignments after {max_attempts} attempts")
