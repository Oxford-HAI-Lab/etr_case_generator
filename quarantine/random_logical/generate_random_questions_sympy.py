import random
from typing import List, Dict, Optional
from itertools import product
from sympy import symbols, And, Or, Not, to_cnf, to_dnf, satisfiable, Symbol, true, false, simplify, simplify_logic
from sympy.logic.boolalg import BooleanFunction


def generate_literal(variable: Symbol) -> Symbol:
    return Not(variable) if random.choice([True, False]) else variable


def generate_clause(variables: List[Symbol], min_literals: int, max_literals: int) -> Or:
    num_literals = random.randint(min_literals, min(max_literals, len(variables)))
    chosen_vars = random.sample(variables, num_literals)
    return Or(*[generate_literal(var) for var in chosen_vars])


def _generate_random_cnf(num_clauses: int, min_literals_per_clause: int, max_literals_per_clause: int,
                         num_variables: int) -> And:
    variables = symbols(f'x:{num_variables}')
    clauses = [generate_clause(variables, min_literals_per_clause, max_literals_per_clause) for _ in range(num_clauses)]
    return And(*clauses)


def _random_logical_statement(num_variables: int, num_steps: int = 5) -> BooleanFunction:
    # Create N variables (x1, x2, ..., xn)
    variables = symbols(f'x1:{num_variables + 1}')

    # Define a random logical operator generator
    def random_operator():
        return random.choice([And, Or, Not])

    # Define a random term generator (variable or NOT variable)
    def random_term():
        var = random.choice(variables)
        if random.choice([True, False]):
            return Not(var)
        return var

    # Start building the random logical statement
    statement = random_term()
    # print(statement)

    # Randomly apply operators and combine terms
    for _ in range(num_steps):
        operator = random_operator()
        if operator == Not:
            statement = operator(statement)
        else:
            statement = operator(statement, random_term())
        # print(statement)

    return statement


def find_necessary_assignments(expr) -> Dict[Symbol, Optional[bool]]:
    necessary = {}
    for var in expr.free_symbols:
        true_sat = satisfiable(expr.subs(var, true))
        false_sat = satisfiable(expr.subs(var, false))

        if true_sat and not false_sat:
            necessary[var] = True
        elif false_sat and not true_sat:
            necessary[var] = False
        else:
            necessary[var] = None

    return necessary


def to_natural_language(expr):
    return str(expr).replace('&', 'and').replace('|', 'or').replace('~', 'not ')


def create_random_questions(n: int, num_clauses: int, min_literals_per_clause: int, max_literals_per_clause: int,
                            num_variables: int) -> List[Dict]:
    questions = []

    for _ in range(n):
        # random_expr = _generate_random_cnf(num_clauses, min_literals_per_clause, max_literals_per_clause, num_variables)
        random_expr = _random_logical_statement(num_variables, 10)
        necessary_assignments = find_necessary_assignments(random_expr)

        cnf_str = str(to_cnf(random_expr))
        dnf_str = str(to_dnf(random_expr))
        natural_str = to_natural_language(random_expr)

        follows = [f"{var} is {'True' if value else 'False'}"
                   for var, value in necessary_assignments.items()
                   if value is not None]

        questions.append({
            "statement": str(random_expr),
            "cnf": cnf_str,
            "dnf": dnf_str,
            "natural": natural_str,
            "necessary_assignments": necessary_assignments,
            "follows": follows,
            "num_clauses": num_clauses,
            "num_variables": num_variables
        })

    return questions


def main():
    # Example usage of create_random_questions
    questions = create_random_questions(
        n=2,
        num_clauses=3,
        min_literals_per_clause=2,
        max_literals_per_clause=3,
        num_variables=4
    )

    print("Generated Questions:")
    for i, question in enumerate(questions, 1):
        print(f"\nQuestion {i}:")
        print(f"Statement: {question['statement']}")
        print(f"CNF: {question['cnf']}")
        print(f"DNF: {question['dnf']}")
        print(f"Natural Language: {question['natural']}")
        print("Necessary Assignments:")
        for var, value in question['necessary_assignments'].items():
            print(f"  {var}: {value}")
        print("Follows:")
        for follow in question['follows']:
            print(f"  - {follow}")
        print(f"Number of Clauses: {question['num_clauses']}")
        print(f"Number of Variables: {question['num_variables']}")

    # Example usage of _random_logical_statement
    print("\nExample of a random logical expression:")
    random_expr = _random_logical_statement(num_variables=4, num_steps=5)
    print(f"Original expression: {random_expr}")
    print(f"Simplified (simplify): {simplify(random_expr)}")
    print(f"Simplified (simplify_logic): {simplify_logic(random_expr)}")
    print(f"CNF: {to_cnf(random_expr)}")
    print(f"DNF: {to_dnf(random_expr)}")
    print(f"Natural Language: {to_natural_language(random_expr)}")

    # Truth table using bool_map
    variables = random_expr.free_symbols
    print("\nTruth Table:")
    for values in product([True, False], repeat=len(variables)):
        assignment = dict(zip(variables, values))
        result = random_expr.subs(assignment)
        print(f"{assignment}: {result}")


if __name__ == "__main__":
    main()
