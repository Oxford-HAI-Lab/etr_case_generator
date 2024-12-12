import argparse

from etr_case_generator.generator2.problem_in_smt import generate_problem_in_smt
from etr_case_generator.generator2.reified_problem import FullProblem


from etr_case_generator.ontology import ELEMENTS, CARDS, Ontology


def generate_problem(args, ontology: Ontology=ELEMENTS) -> FullProblem:
    return generate_problem_in_smt(args, ontology)


def generate_problem_list(n_problems: int, args) -> list[FullProblem]:
    """Generate ETR problems.

    Args:
        n_problems (int): The number of problems to generate
        verbose (bool, optional): Whether to print debugging info. Defaults to False.
    """

    problems: list[FullProblem] = []
    for i in range(args.n_problems):
        if args.verbose:
            print(f"Generating problem {len(problems) + 1}/{args.n_problems}")
        problem = generate_problem(args)
        problems.append(problem)
        print(f"Generated Problem {i + 1} of {n_problems}")
        print(problem)

    return problems


def main():
    parser = argparse.ArgumentParser(
        description="Generate a dataset of reasoning problems using ETRCaseGenerator"
    )
    parser.add_argument(
        "-n",
        "--n-problems", 
        type=int,
        default=3,
        help="Number of problems to generate"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print verbose output"
    )
    parser.add_argument("--name_shortening", type=str, default="none", help="How to shorten names of objects and predicates. Options are 'none', 'short', and 'first'.")
    args = parser.parse_args()
    
    generate_problem_list(n_problems=args.n_problems, args=args)

if __name__ == "__main__":
    main()
