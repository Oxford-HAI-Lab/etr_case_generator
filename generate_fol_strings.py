# def generate_all_cases(
#     cases: list,
#     vocab_size: int,
#     negation: bool,
#     conjuncts: bool,
#     disjuncts: bool,
# ) -> list:
#     """
#     Recursive subproblem?

#     Iterative problem:
#     First generate all monadic views, then all possible extensions of these formable with conjoining, disjoining, etc.
#     If we generate all possible views, then all possible cases of length n are just every possible list of length n drawn from these views.
#     """


# def generate_recursive(n: int, []):
#     # base case: n is 0
#     if n == 1:
#         return


#     for connector in ["and", "or"]:
#         generate_recursive(n - 1)


    # Set of length n: for each variable A: { (n-1), A and (n-1), A or (n-1), ~A and (n-1), ~A or (n-1) }


# Set of variables V {A, B, C, D}
# All possible subsets P(V)
# All possible connections of variables v in P(V) (example of v might be {A, B, C})
# Take powerset of THAT
# Now working with e.g. {A, B}, and consider all sentences that include EXACTLY A and B
# That is: A and B, A or B

# ((A and B) and (C and D)) and (A and B)
# Start with atoms
# Combine everything in your set with all connectors
# Do this iteratively until the largest sequence has length |v|

# [[A, B], [C]]
# [[A, B, C]]
# [[A], [B], [C]]


# [[A]], [[B]], [[C]]
# for each monad:
#     [[A, B]], [[A, C]], [[A], [B]], [[A], [C]]


from itertools import combinations, product

def generate_atomic_formulas(variables):
    """Generate atomic formulas including the variables and their negations."""
    atomic_formulas = []
    for var in variables:
        atomic_formulas.append(var)
        atomic_formulas.append(f'~{var}')
    return atomic_formulas

def combine_binary(formulas1, formulas2):
    """Combine two sets of formulas with binary operators AND, OR."""
    combined = []
    for f1, f2 in product(formulas1, formulas2):
        combined.append(f'({f1} ∧ {f2})')
        combined.append(f'({f1} ∨ {f2})')
    return combined

def generate_boolean_formulas(variables, max_depth=2):
    """Generate all Boolean formulas for a set of variables up to a given depth."""
    formulas = generate_atomic_formulas(variables)
    all_formulas = set(formulas)  # Use a set to avoid duplicates

    # Iteratively combine formulas up to the given depth
    for depth in range(1, max_depth):
        new_formulas = set()
        for f1, f2 in combinations(all_formulas, 2):
            new_formulas.update(combine_binary([f1], [f2]))
        all_formulas.update(new_formulas)

    return sorted(all_formulas)

# Example usage
variables = ['x', 'y']
formulas = generate_boolean_formulas(variables, max_depth=3)

print("Generated Boolean formulas:")
for formula in formulas:
    print(formula)