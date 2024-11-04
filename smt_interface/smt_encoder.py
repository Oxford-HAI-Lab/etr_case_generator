from pyetr import View

from pysmt.shortcuts import Symbol, ForAll, Exists, Solver, Not, Real, Or, Times, get_env
from pysmt.typing import BOOL, REAL
from pysmt.logics import QF_LRA

from pysmt.shortcuts import Symbol, And, Or, Not, Real, Times, get_env
from pysmt.typing import BOOL, REAL
from pysmt.logics import QF_LRA


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


def view_to_smt(view: View):
    """Convert a View object to SMT formula using PySMT.
    
    Args:
        view (View): The view to convert
        
    Returns:
        pysmt.FNode: The SMT formula representing the view
    """
    # Create SMT symbols for each predicate atom in the view
    symbols = {}
    for atom in view.atoms:
        name = str(atom)
        if name not in symbols:
            symbols[name] = Symbol(name, BOOL)

    def state_to_smt(state):
        """Convert a State to conjunction of literals"""
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
