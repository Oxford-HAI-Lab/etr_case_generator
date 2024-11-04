from pyetr import View

from pysmt.shortcuts import Symbol, ForAll, Exists, Solver, Not, Real, Or, Times, get_env
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


def view_to_smt(view: View) -> FNode:
    """Convert a View object to SMT formula using PySMT.
    
    Args:
        view (View): The view to convert
        
    Returns:
        pysmt.FNode: The SMT formula representing the view
    """
    # Create SMT symbols for each predicate atom in the view
    symbols: Dict[str, FNode] = {}
    for atom in view.atoms:
        name = str(atom)
        if name not in symbols:
            symbols[name] = Symbol(name, BOOL)

    def state_to_smt(state: State) -> FNode:
        """Convert a State to conjunction of literals
        
        Args:
            state (State): The state to convert
            
        Returns:
            pysmt.FNode: The SMT formula representing the state
        """
        terms = []
        for atom in state:
            sym = symbols[str(atom)]
            # Handle negation
            if not atom.predicate.verifier:
                sym = Not(sym)
            terms.append(sym)
        return And(terms) if terms else Symbol("TRUE", BOOL)

    # Convert stage to disjunction of states
    stage_formula = Or([state_to_smt(state) for state in view.stage])
    
    # Handle weights if present
    weight_constraints = []
    for state, weight in view.weights.items():
        if not weight.is_null:
            state_sym = state_to_smt(state)
            # Create real-valued weight symbol
            weight_sym = Real(float(str(weight)))
            weight_constraints.append(
                state_sym.Iff(Times(weight_sym, Symbol("1", REAL)))
            )
    
    # Combine stage formula with weight constraints
    formula = stage_formula
    if weight_constraints:
        formula = And(formula, And(weight_constraints))
        
    # Handle supposition if not verum
    if not view.supposition.is_verum:
        supp_formula = Or([state_to_smt(state) for state in view.supposition])
        formula = supp_formula.Implies(formula)
        
    return formula


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

