from typing import Dict, List, Union, Optional
from pysmt.shortcuts import Symbol, And, Or, Not, Implies, Iff, is_valid
from pysmt.fnode import FNode
from pysmt.typing import BOOL, REAL, PySMTType
import random

# Keep track of variable counts
var_counts: Dict[str, int] = {'x': 0, 'y': 0}

def random_symbol(prefix: str = "x", type: PySMTType = BOOL) -> FNode:
    """Generate a sequential symbol with given prefix and type"""
    global var_counts
    var_counts[prefix] += 1
    return Symbol(f"{prefix}{var_counts[prefix]}", type)

def count_nodes(formula: FNode) -> int:
    """Count the number of nodes in a formula"""
    if formula.is_symbol():
        return 1
    return 1 + sum(count_nodes(arg) for arg in formula.args())

def random_bool_expr(depth: int = 0, max_depth: int = 4, target_nodes: int = 15, current_nodes: int = 0) -> FNode:
    """
    Generate a random boolean expression with target number of nodes
    
    Args:
        depth: Current depth in the expression tree
        max_depth: Maximum allowed depth
        target_nodes: Target total number of nodes
        current_nodes: Current number of nodes created
    """
    nodes_remaining = target_nodes - current_nodes
    
    # If we need just one more node, return a symbol
    if nodes_remaining <= 1 or depth >= max_depth:
        return random_symbol()
    
    # Adjust probabilities based on depth and remaining nodes
    if depth < 2 and nodes_remaining > 8:  # At start, prefer complex operations
        weights = {
            'not': 0.05,
            'and': 0.35,
            'or': 0.35,
            'implies': 0.15,
            'iff': 0.10
        }
    elif nodes_remaining > 4:  # Mid-depth, mix of operations
        weights = {
            'not': 0.15,
            'and': 0.30,
            'or': 0.30,
            'implies': 0.15,
            'iff': 0.10
        }
    else:  # Near max depth or few nodes left, prefer simpler operations
        weights = {
            'not': 0.30,
            'and': 0.25,
            'or': 0.25,
            'implies': 0.10,
            'iff': 0.10
        }
    
    op = random.choices(list(weights.keys()), list(weights.values()))[0]
    
    if op == 'not':
        subexpr = random_bool_expr(depth + 1, max_depth, nodes_remaining - 1, current_nodes + 1)
        return Not(subexpr)
    elif op in ('and', 'or'):
        # Calculate how many terms we can afford
        max_possible_terms = (nodes_remaining - 1) // 2  # Each term needs at least 1 node
        num_terms = min(3, max(2, max_possible_terms))  # Between 2 and 3 terms
        terms = []
        nodes_per_term = (nodes_remaining - 1) // num_terms
        
        for i in range(num_terms):
            term = random_bool_expr(depth + 1, max_depth, nodes_per_term, 
                                  current_nodes + 1 + len(terms))
            terms.append(term)
        
        return And(terms) if op == 'and' else Or(terms)
    else:  # implies or iff
        # Split remaining nodes roughly evenly between two sides
        half_nodes = (nodes_remaining - 1) // 2
        left = random_bool_expr(depth + 1, max_depth, half_nodes, current_nodes + 1)
        right = random_bool_expr(depth + 1, max_depth, half_nodes, 
                               current_nodes + 1 + count_nodes(left))
        return Implies(left, right) if op == 'implies' else Iff(left, right)

def to_cnf(formula: FNode) -> FNode:
    """Convert formula to Conjunctive Normal Form (CNF)"""
    # First convert implications and iffs
    formula = eliminate_implications(formula)
    
    # Push negations inward using De Morgan's laws
    formula = push_negations(formula)
    
    # Distribute Or over And
    formula = distribute_or_over_and(formula)
    
    return formula

def to_dnf(formula: FNode) -> FNode:
    """Convert formula to Disjunctive Normal Form (DNF)"""
    # First convert implications and iffs
    formula = eliminate_implications(formula)
    
    # Push negations inward using De Morgan's laws
    formula = push_negations(formula)
    
    # Distribute And over Or
    formula = distribute_and_over_or(formula)
    
    return formula

def distribute_and_over_or(formula: FNode) -> FNode:
    """Distribute And over Or"""
    if formula.is_and():
        # Find any Or terms
        or_terms = [arg for arg in formula.args() if arg.is_or()]
        if or_terms:
            # Take first Or term and distribute
            or_term = or_terms[0]
            other_terms = [arg for arg in formula.args() if arg is not or_term]
            distributed = [And(distribute_and_over_or(or_arg), 
                           *[distribute_and_over_or(term) for term in other_terms])
                         for or_arg in or_term.args()]
            return Or(distributed)
        else:
            return And([distribute_and_over_or(arg) for arg in formula.args()])
    elif formula.is_or():
        return Or([distribute_and_over_or(arg) for arg in formula.args()])
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

def format_formula(formula: FNode) -> str:
    """Format formula for display with minimal parentheses"""
    def _format(f: FNode, parent_op: Optional[str] = None) -> str:
        if f.is_symbol():
            return f.symbol_name()
        elif f.is_not():
            return f"¬{_format(f.arg(0), 'not')}"
        
        # Get operator and arguments
        if f.is_and():
            op, args = "∧", f.args()
        elif f.is_or():
            op, args = "∨", f.args()
        elif f.is_implies():
            op, args = "→", f.args()
        elif f.is_iff():
            op, args = "↔", f.args()
        else:
            return f.serialize()
            
        # Format arguments
        formatted_args = [_format(arg, op) for arg in args]
        
        # Join with operator
        result = f" {op} ".join(formatted_args)
        
        # Add parentheses only if needed
        needs_parens = False
        if parent_op:
            # Order of precedence: ¬ > ∧ > ∨ > → > ↔
            precedence = {"not": 4, "∧": 3, "∨": 2, "→": 1, "↔": 0}
            if precedence.get(op, -1) < precedence.get(parent_op, -1):
                needs_parens = True
                
        return f"({result})" if needs_parens else result
        
    return _format(formula)

def get_variables(formula: FNode) -> set[FNode]:
    """Get all variables in a formula"""
    if formula.is_symbol():
        return {formula}
    return set().union(*(get_variables(arg) for arg in formula.args()))

def print_assignments(formula: FNode, max_solutions: int = 5) -> None:
    """
    Print satisfying assignments for the formula using iterative solving
    
    Args:
        formula: The formula to find assignments for
        max_solutions: Maximum number of solutions to show
    """
    from pysmt.shortcuts import Solver, Or, Not, And
    
    solutions = []
    vars_to_check = get_variables(formula)
    
    with Solver() as solver:
        solver.add_assertion(formula)
        
        while len(solutions) < max_solutions:
            if solver.solve():
                model = solver.get_model()
                solution = {var.symbol_name(): model.get_value(var).constant_value() 
                          for var in vars_to_check}
                solutions.append(solution)
                
                # Add blocking clause to prevent this solution
                block = Or([Not(var) if model.get_value(var).constant_value() 
                          else var for var in vars_to_check])
                solver.add_assertion(block)
            else:
                break
    
    if not solutions:
        print("\nFormula is UNSATISFIABLE")
        return
        
    print(f"\nFound {len(solutions)} satisfying assignment(s):")
    for i, solution in enumerate(solutions, 1):
        assignments = [f"{var}={str(value).lower()}" for var, value in sorted(solution.items())]
        print(f"Solution {i}: {', '.join(assignments)}")
    
    if len(solutions) == max_solutions:
        print(f"\nNote: Only showing first {max_solutions} solutions")

def main() -> None:
    # Generate random formula with target size
    formula: FNode = random_bool_expr(target_nodes=20)
    print("Original formula:")
    print(format_formula(formula))
    
    # Convert to CNF
    cnf_formula = to_cnf(formula)
    print("\nCNF formula:")
    print(format_formula(cnf_formula))
    
    # Convert to DNF
    dnf_formula = to_dnf(formula)
    print("\nDNF formula:")
    print(format_formula(dnf_formula))
    
    # Print satisfying assignments
    print_assignments(formula)

if __name__ == "__main__":
    main()
