import random
from sympy import symbols, And, Or, Not, to_cnf, to_dnf, simplify_logic, Symbol, Function


def random_logical_statement(num_variables: int, num_steps: int = 5):
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
    print(statement)

    # Randomly apply operators and combine terms
    for _ in range(num_steps):
        operator = random_operator()
        if operator == Not:
            statement = operator(statement)
        else:
            statement = operator(statement, random_term())
        print(statement)

    return statement


if __name__ == '__main__':
    # Generate and print the random logical statement
    logical_statement = random_logical_statement(5, 10)
    print("Random logical statement:")
    print(logical_statement)

    # Convert to CNF, simplify, and print
    cnf_statement = to_cnf(logical_statement)
    print("\nSimplified CNF form:")
    print(cnf_statement)

    # Convert to DNF, simplify, and print
    dnf_statement = to_dnf(logical_statement)
    print("\nSimplified DNF form:")
    print(dnf_statement)

    # Test universal and existential quantifiers
    print("\nTesting universal and existential quantifiers:")
    
    x = Symbol('x')
    y = Symbol('y')
    P = Function('P')
    Q = Function('Q')

    # Universal quantifier example
    forall_expr = ForAll(x, P(x))
    print("Universal quantifier example:")
    print(forall_expr)

    # Existential quantifier example
    exists_expr = Exists(x, Q(x))
    print("\nExistential quantifier example:")
    print(exists_expr)

    # Combining quantifiers
    combined_expr = ForAll(x, Exists(y, And(P(x), Q(y))))
    print("\nCombined quantifiers example:")
    print(combined_expr)

    # Negating quantifiers
    negated_forall = Not(ForAll(x, P(x)))
    print("\nNegated universal quantifier:")
    print(negated_forall)
    print("Simplified:")
    print(simplify_logic(negated_forall))

    negated_exists = Not(Exists(x, Q(x)))
    print("\nNegated existential quantifier:")
    print(negated_exists)
    print("Simplified:")
    print(simplify_logic(negated_exists))
