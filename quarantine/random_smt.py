from pysmt.shortcuts import Symbol, ForAll, Exists, Not, And, Or, Implies, Real, Times
from pysmt.rewritings import conjunctive_partition, disjunctive_partition
from pysmt.rewritings import nnf
from pysmt.typing import BOOL, REAL
import random
from rich import print
from rich.panel import Panel
from rich.console import Console

def replace_logic_symbols(formula_str: str) -> str:
    """Replace ASCII logic symbols with Unicode equivalents"""
    replacements = {
        "forall": "∀",
        "exists": "∃", 
        "->": "→",
        "&": "∧",
        "|": "∨",
        "!": "¬"
    }
    result = formula_str
    for ascii_sym, unicode_sym in replacements.items():
        result = result.replace(ascii_sym, unicode_sym)
    return result

console = Console()

# Keep track of variable counts and types
var_counts = {'x': 0, 'y': 0}

def random_symbol(prefix="x", type=BOOL):
    """Generate a sequential symbol with given prefix and type"""
    global var_counts
    var_counts[prefix] += 1
    return Symbol(f"{prefix}{var_counts[prefix]}", type)

def random_bool_expr():
    """Generate a random boolean expression"""
    ops = [
        lambda x, y: And(x, y),
        lambda x, y: Or(x, y),
        lambda x, y: Implies(x, y),
        lambda x: Not(x)
    ]

    # Generate base symbols
    s1 = random_symbol()
    s2 = random_symbol()

    # Pick random operation
    op = random.choice(ops)
    if op.__code__.co_argcount == 1:
        return op(s1)
    return op(s1, s2)

def random_real_comparison():
    """Generate a random real-valued comparison that returns a boolean"""
    s1 = random_symbol(prefix="y", type=REAL)
    s2 = random_symbol(prefix="y", type=REAL)
    # Use simpler fractions: 0.25, 0.5, or 0.75
    weight = Real(random.choice([0.25, 0.5, 0.75]))
    expr = Times(weight, s1)

    # Compare with another real to create a boolean expression
    return expr.Equals(s2)

def build_random_formula(num_build_steps=2, bool_prob=0.6, num_random_quantifiers=1):
    """Build a random formula with n boolean components and num_build_steps inner components
    
    Args:
        num_build_steps (int): Number of build steps to perform
        bool_prob (float): Probability of generating boolean expressions vs real comparisons
    """
    # Reset variable counts for each new formula
    global var_counts
    var_counts = {'x': 0, 'y': 0}

    expr = random_bool_expr()

    for _ in range(num_build_steps):
        # Randomly choose between pure boolean or real comparison
        if random.random() < bool_prob:  # Default 60% chance of boolean
            new_expr = random_bool_expr()
        else:
            new_expr = random_real_comparison()

        # Combine boolean expressions
        expr = And([expr, new_expr])

    # Add requested number of quantifiers
    for _ in range(num_random_quantifiers):
        var = random_symbol(prefix="x", type=BOOL)
        if random.random() < 0.6:  # 60% chance of ForAll
            expr = ForAll([var], expr)
        else:
            expr = Exists([var], expr)

    return expr

def to_dnf(formula):
    """Convert formula to DNF form"""
    # First convert to NNF (Negation Normal Form)
    nnf_formula = nnf(formula)
    
    # Get disjunctive partitions
    partitions = disjunctive_partition(nnf_formula)

    # Otherwise combine with Or
    return Or(partitions)

def main():
    console.rule("[bold blue]Random SMT Formula Generator")

    for i in range(5):
        num_build_steps = i + 3

        formula = build_random_formula(num_build_steps=num_build_steps, bool_prob=1.0, num_random_quantifiers=0)
        dnf_formula = to_dnf(formula)

        console.print(Panel(
            "[yellow]Num Build Steps: [/yellow]" + str(num_build_steps) + 
            "\n[yellow]Original Formula: [/yellow]" + replace_logic_symbols(formula.serialize()) +
            "\n[yellow]DNF Form: [/yellow]" + replace_logic_symbols(dnf_formula.serialize()),
            title=f"Generated Formula {i+1}",
            border_style="green"))

        # console.print("[yellow]Expression (serialized):[/yellow]", replace_logic_symbols(formula.serialize()))

if __name__ == "__main__":
    main()
