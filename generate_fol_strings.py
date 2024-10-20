import argparse
import re

from itertools import combinations_with_replacement, product


def generate_atomic_formulas(variables):
    """Generate atomic formulas including the variables and their negations."""
    atomic_formulas = []
    for var in variables:
        atomic_formulas.append(f"{var}()")
        atomic_formulas.append(f"~{var}()")
    return atomic_formulas


def combine_binary(formulas1, formulas2) -> list[str]:
    """Combine two sets of formulas with binary operators AND, OR."""
    combined = []
    for f1, f2 in product(formulas1, formulas2):
        combined.append(f"({f1} ∧ {f2})")
        combined.append(f"({f1} ∨ {f2})")
    return combined


def prune_redundant_formulas(formulas):
    """Prune logically redundant formulas from the set.

    Args:
        formulas (_type_): _description_
    """
    pruned = set()
    for formula in formulas:
        # Extract the set of variables in the formula
        variables = set(
            [
                v
                for v in formula.replace("~", "")
                .replace("(", "")
                .replace(")", "")
                .split(" ")
                if v.isalpha()
            ]
        )

        # Find the character value of the lowest variable in the formula, and subtract
        # 'A' from it
        min_variable = ord(min(variables)) - ord("A")

        # Now for each variable in the original formula, match and shift it down by
        # min_variable
        for var in variables:
            formula = formula.replace(var, chr(ord(var) - min_variable))
        pruned.add(formula)

    return pruned


def generate_boolean_formulas(variables, max_depth=2):
    """Generate all Boolean formulas for a set of variables up to a given depth."""
    formulas = generate_atomic_formulas(variables)
    all_formulas = set(formulas)

    # We don't need redundant atomic formulas in the final output, but we need them to
    # generate other boolean combinations
    final_formulas = set(["A()", "~A()"])

    # Iteratively combine formulas up to the given depth
    for depth in range(1, max_depth):
        new_formulas = set()
        for f1, f2 in combinations_with_replacement(all_formulas, 2):
            f1_alpha = re.sub(r"[^a-zA-Z]", "", f1)
            f2_alpha = re.sub(r"[^a-zA-Z]", "", f2)
            if f1_alpha <= f2_alpha:
                new_formulas.update(combine_binary([f1], [f2]))
        all_formulas.update(new_formulas)
        final_formulas.update(new_formulas)

    final_formulas_distinct = prune_redundant_formulas(final_formulas)

    return sorted(final_formulas_distinct)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate Boolean formulas.")
    parser.add_argument(
        "--vocab_size", type=int, help="Number of variables in the vocabulary"
    )
    parser.add_argument(
        "--depth", type=int, help="Depth of boolean formulas to generate"
    )
    return parser.parse_args()


def generate_variables(vocab_size: int) -> list[str]:
    """Generate a list of variables based on the vocabulary size."""
    variables = []
    for i in range(vocab_size):
        variables.append(chr(ord("A") + i % 26) * (i // 26 + 1))
    return variables


def main(vocab_size: int, depth: int) -> list[str]:
    variables = generate_variables(vocab_size)
    formulas = generate_boolean_formulas(variables, max_depth=depth)

    print(f"Generated {len(formulas)} Boolean formulas.")
    return formulas


if __name__ == "__main__":
    args = parse_arguments()
    main(args.vocab_size, args.depth)
