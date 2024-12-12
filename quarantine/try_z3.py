# File 1: Z3 Examples

import z3
from z3 import Bool, ForAll, Exists, Solver, Not, Real
from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.syntax import Syntax

console = Console()

def example_1():
    console.rule("[bold blue]Example 1: Quantified View in Z3")
    console.print(Panel("PyETR: ∀z ∃w {Student(z*)Reads(z,w)Book(w)}^{Student(z*)}", 
                       title="Input Formula", 
                       border_style="green"))
    Student = Bool('Student')
    Reads = Bool('Reads')
    Book = Bool('Book')
    z = Bool('z')
    w = Bool('w')
    expr = ForAll([z], Exists([w], Reads == Book))
    solver = Solver()
    solver.add(expr)
    console.print("[yellow]Expression (Z3 representation):[/yellow]", expr)
    console.print("[yellow]Expression (string representation):[/yellow]", str(expr))
    console.print("[yellow]Expression (raw format):[/yellow]", expr.sexpr())  # S-expression format
    if solver.check() == z3.sat:
        console.print("[bold green]Satisfiable. Model:[/bold green]", solver.model())
    else:
        console.print("[bold red]Unsatisfiable[/bold red]")

def example_2():
    console.rule("[bold blue]Example 2: Negation and Dependency Relations in Z3")
    console.print(Panel("PyETR: ∀x {~S(x)T(x), ~S(x)~T(x)} ^ {~S(x*)}", 
                       title="Input Formula", 
                       border_style="green"))
    S = Bool('S')
    T = Bool('T')
    x = Bool('x')
    expr = ForAll([x], S == Not(T))
    solver = Solver()
    solver.add(expr)
    console.print("[yellow]Expression (Z3 representation):[/yellow]", expr)
    console.print("[yellow]Expression (string representation):[/yellow]", str(expr))
    console.print("[yellow]Expression (raw format):[/yellow]", expr.sexpr())  # S-expression format
    if solver.check() == z3.sat:
        console.print("[bold green]Satisfiable. Model:[/bold green]", solver.model())
    else:
        console.print("[bold red]Unsatisfiable[/bold red]")

def example_3():
    console.rule("[bold blue]Example 3: Weighted States in Z3")
    console.print(Panel("PyETR: ∀x {0.3=* P(x*)C(x), P(x*)~C(x)} ^ {P(x*)}", 
                       title="Input Formula", 
                       border_style="green"))
    P = z3.Real('P')
    C = z3.Real('C')
    x = z3.Real('x')
    weight = z3.RealVal(0.3)
    solver = z3.Solver()
    # Constrain P and C to be 0 or 1 to represent boolean values
    solver.add(z3.Or(P == 0, P == 1))
    solver.add(z3.Or(C == 0, C == 1))
    expr = ForAll([x], P == weight * C)
    solver.add(expr)
    console.print("[yellow]Expression (Z3 representation):[/yellow]", expr)
    console.print("[yellow]Expression (string representation):[/yellow]", str(expr))
    console.print("[yellow]Expression (raw format):[/yellow]", expr.sexpr())  # S-expression format
    if solver.check() == z3.sat:
        console.print("[bold green]Satisfiable. Model:[/bold green]", solver.model())
    else:
        console.print("[bold red]Unsatisfiable[/bold red]")

if __name__ == "__main__":
    example_1()
    example_2()
    example_3()
