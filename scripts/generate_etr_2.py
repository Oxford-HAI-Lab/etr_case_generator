import argparse
from etr_case_generator import ETRCaseGenerator
from etr_case_generator.ontology import ELEMENTS


def main(n_problems: int, verbose: bool = False):
    """Generate ETR problems.

    Args:
        n_problems (int): The number of problems to generate
        verbose (bool, optional): Whether to print debugging info. Defaults to False.
    """
    generator = ETRCaseGenerator(ontology=ELEMENTS)
    
    problems = []
    for _ in range(n_problems):
        if verbose:
            print(f"Generating problem {len(problems) + 1}/{n_problems}")
        # TODO: Generate problem here
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a dataset of reasoning problems using ETRCaseGenerator"
    )
    parser.add_argument(
        "-n",
        "--n-problems", 
        type=int,
        default=10,
        help="Number of problems to generate"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print verbose output"
    )
    args = parser.parse_args()
    
    main(n_problems=args.n_problems, verbose=args.verbose)
