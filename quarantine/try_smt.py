# File 2: PySMT Examples

from pysmt.shortcuts import Symbol, ForAll, Exists, Solver, Not, Real, Or, Times, get_env, parse_formula
from pysmt.typing import BOOL, REAL
from pysmt.logics import QF_LRA
from pysmt.exceptions import PysmtSyntaxError
from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.syntax import Syntax

console = Console()


def example_1():
    console.rule("[bold blue]Example 1: Quantified View in PySMT")
    console.print(Panel("∀z ∃w {Student(z*)Reads(z,w)Book(w)}^{Student(z*)}", 
                       title="Input Formula", 
                       border_style="green"))

    Student = Symbol("Student", BOOL)
    Reads = Symbol("Reads", BOOL)
    Book = Symbol("Book", BOOL)
    z1 = Symbol("z1", BOOL)
    w1 = Symbol("w1", BOOL)

    expr = ForAll([z1], Exists([w1], Reads.Iff(Book)))
    with Solver() as solver:
        solver.add_assertion(expr)
        console.print("[yellow]Expression (PySMT representation):[/yellow]", expr.serialize())
        console.print("[yellow]Expression (string representation):[/yellow]", str(expr))
        if solver.solve():
            console.print("[bold green]Satisfiable. Model:[/bold green]", solver.get_model())
        else:
            console.print("[bold red]Unsatisfiable[/bold red]")


def example_2():
    console.rule("[bold blue]Example 2: Negation and Dependency Relations in PySMT")
    console.print(Panel("∀x {~S(x)T(x), ~S(x)~T(x)} ^ {~S(x*)}", 
                       title="Input Formula", 
                       border_style="green"))

    S = Symbol("S", BOOL)
    T = Symbol("T", BOOL)
    x2 = Symbol("x2", BOOL)

    expr = ForAll([x2], Not(S).Iff(Not(T)))
    with Solver() as solver:
        solver.add_assertion(expr)
        console.print("[yellow]Expression (PySMT representation):[/yellow]", expr.serialize())
        console.print("[yellow]Expression (string representation):[/yellow]", str(expr))
        if solver.solve():
            console.print("[bold green]Satisfiable. Model:[/bold green]", solver.get_model())
        else:
            console.print("[bold red]Unsatisfiable[/bold red]")


def example_3():
    console.rule("[bold blue]Example 3: Weighted States in PySMT using Z3")
    console.print(Panel("∀x {0.3=* P(x*)C(x), P(x*)~C(x)} ^ {P(x*)}", 
                       title="Input Formula", 
                       border_style="green"))

    P = Symbol("P", REAL)
    C = Symbol("C", REAL)
    x3 = Symbol("x3", REAL)
    weight = Real(0.3)

    # Create Z3 solver instance
    z3 = get_env().factory.Solver(name='z3', logic=QF_LRA)
    
    # Add constraints to make P and C act like booleans (0 or 1)
    z3.add_assertion(Or(P.Equals(Real(0)), P.Equals(Real(1))))
    z3.add_assertion(Or(C.Equals(Real(0)), C.Equals(Real(1))))
    
    expr = ForAll([x3], P.Equals(Times(weight, C)))
    z3.add_assertion(expr)
    
    console.print("[yellow]Expression (PySMT representation):[/yellow]", expr.serialize())
    console.print("[yellow]Expression (string representation):[/yellow]", str(expr))
    console.print("[yellow]Using solver: Z3[/yellow]")
    
    if z3.solve():
        console.print("[bold green]Satisfiable. Model:[/bold green]", z3.get_model())
    else:
        console.print("[bold red]Unsatisfiable[/bold red]")


def example_4():
    console.rule("[bold blue]Example 4: Parsing Formula from String")
    
    formula_str = "(x | y) & !z"
    console.print(Panel(f"Input string formula: {formula_str}", 
                       title="String Formula", 
                       border_style="green"))
    
    try:
        # Parse the formula string
        parsed_formula = parse_formula(formula_str)
        
        with Solver() as solver:
            solver.add_assertion(parsed_formula)
            console.print("[yellow]Parsed Expression:[/yellow]", parsed_formula.serialize())
            
            if solver.solve():
                console.print("[bold green]Satisfiable. Model:[/bold green]", solver.get_model())
            else:
                console.print("[bold red]Unsatisfiable[/bold red]")
                
    except PysmtSyntaxError as e:
        console.print(f"[bold red]Error parsing formula:[/bold red] {str(e)}")


if __name__ == "__main__":
    example_1()
    example_2()
    example_3()
    example_4()
