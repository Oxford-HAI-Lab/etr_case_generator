from pyetr import PredicateAtom, View

from pysmt.shortcuts import Symbol, ForAll, Exists, Solver, Not, Real, Or, Times, get_env, TRUE
from pysmt.typing import BOOL, REAL
from pysmt.logics import QF_LRA

from pysmt.shortcuts import Symbol, And, Or, Not, Real, Times, get_env
from pysmt.typing import BOOL, REAL
from pysmt.logics import QF_LRA

from typing import Dict
from pysmt.fnode import FNode
from pyetr.atoms import Atom
from pyetr.stateset import State


# Example Views:
# {'_stage': {King()Ten(),Five()Seven(),Ace()Seven()Two()}, '_supposition': {0}, '_dependency_relation': U={} E={}, '_issue_structure': {}, '_weights': {King()Ten(),Five()Seven(),Ace()Seven()Two()}}
# {'_stage': {King()Ten(),Five()Seven(),Ace()Seven()Two()}, '_supposition': {0}, '_dependency_relation': U={} E={}, '_issue_structure': {}, '_weights': {King()Ten(),Five()Seven(),Ace()Seven()Two()}}
# {'_stage': {Nine()King()Two(),~Ace()}, '_supposition': {0}, '_dependency_relation': U={} E={}, '_issue_structure': {}, '_weights': {Nine()King()Two(),~Ace()}}
# {'_stage': {Ace()Three(),Seven()}, '_supposition': {0}, '_dependency_relation': U={} E={}, '_issue_structure': {}, '_weights': {Ace()Three(),Seven()}}
# {'_stage': {Ace()Three(),Seven()}, '_supposition': {0}, '_dependency_relation': U={} E={}, '_issue_structure': {}, '_weights': {Ace()Three(),Seven()}}
# {'_stage': {Queen()Three()Two(),Eight()Three()}, '_supposition': {0}, '_dependency_relation': U={} E={}, '_issue_structure': {}, '_weights': {Queen()Three()Two(),Eight()Three()}}
# {'_stage': {~Ten(),Jack()Three()Ten()}, '_supposition': {0}, '_dependency_relation': U={} E={}, '_issue_structure': {}, '_weights': {~Ten(),Jack()Three()Ten()}}
# {'_stage': {Queen()Nine(),~Eight()~Ten()}, '_supposition': {0}, '_dependency_relation': U={} E={}, '_issue_structure': {}, '_weights': {Queen()Nine(),~Eight()~Ten()}}
# {'_stage': {Ace()Eight()~Five()}, '_supposition': {~Jack()Four()Seven()}, '_dependency_relation': U={} E={}, '_issue_structure': {}, '_weights': {Ace()Eight()~Five()}}
# {'_stage': {Eight()King()Five(),Eight()King()}, '_supposition': {0}, '_dependency_relation': U={} E={}, '_issue_structure': {}, '_weights': {Eight()King()Five(),Eight()King()}}


def atom_to_symbol_name(atom: Atom) -> str:
    assert type(atom) == PredicateAtom
    # I think using str() is fine for both functional terms and arbitrary objects
    terms = ", ".join([str(t) for t in atom.terms])
    name = f"{atom.predicate.name}({terms})"
    return name


def view_to_smt(view: View) -> FNode:
    """Convert a View object to SMT formula using PySMT.
    
    Args:
        view (View): The view to convert
        
    Returns:
        pysmt.FNode: The SMT formula representing the view
    """
    return view.to_smt()


def check_validity(premises: list[View], conclusions: list[View]) -> bool:
    """Check if the conclusions logically follow from the premises using SMT solving.
    
    Args:
        premises (list[View]): List of premise Views
        conclusions (list[View]): List of conclusion Views
        
    Returns:
        bool: True if conclusions are valid given premises, False otherwise
    """
    # Convert premises and conclusions to SMT formulas
    premise_formulas = [view_to_smt(p) for p in premises]
    conclusion_formulas = [view_to_smt(c) for c in conclusions]
    
    # Create solver
    with Solver(name='z3') as solver:
        # Add all premises
        for p in premise_formulas:
            solver.add_assertion(p)
            
        # First check: premises & conclusion should be satisfiable
        for c in conclusion_formulas:
            solver.add_assertion(c)
            
        if not solver.solve():
            return False
            
        solver.reset_assertions()
        
        # Second check: premises & not(conclusion) should be unsatisfiable 
        for p in premise_formulas:
            solver.add_assertion(p)
            
        # Add negation of all conclusions
        for c in conclusion_formulas:
            solver.add_assertion(Not(c))
            
        # If unsatisfiable, the conclusion is valid
        return not solver.solve()


def main():
    """Run some example validity checks using the SMT solver."""
    # Example 1: King()Ten() |= King()
    # This should be valid since King()Ten() implies King()
    v1 = View.from_str('{King()Ten()}^{0}')
    v2 = View.from_str('{King()}^{0}')
    print("\nExample 1: King()Ten() |= King()")
    print("Valid:", check_validity([v1], [v2]))

    # Example 2: King()Ten() |= Ten()
    # This should be valid since King()Ten() implies Ten()
    v3 = View.from_str('{Ten()}^{0}')
    print("\nExample 2: King()Ten() |= Ten()")
    print("Valid:", check_validity([v1], [v3]))

    # Example 3: King() |= King()Ten()
    # This should not be valid since King() does not imply King()Ten()
    print("\nExample 3: King() |= King()Ten()")
    print("Valid:", check_validity([v2], [v1]))

    # Example 4: King()Ten(), Ten()Jack() |= King()Jack()
    # This should be valid by transitivity
    v4 = View.from_str('{Ten()Jack()}^{0}')
    v5 = View.from_str('{King()Jack()}^{0}')
    print("\nExample 4: King()Ten(), Ten()Jack() |= King()Jack()")
    print("Valid:", check_validity([v1, v4], [v5]))


if __name__ == "__main__":
    main()
