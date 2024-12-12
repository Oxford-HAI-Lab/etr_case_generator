import argparse
# from etr_case_generator.ontology import ELEMENTS


def generate_probleem(args):
    ...


def main_loop(args):
    """Generate ETR problems.

    Args:
        n_problems (int): The number of problems to generate
        verbose (bool, optional): Whether to print debugging info. Defaults to False.
    """

    problems = []
    for _ in range(args.n_problems):
        if args.verbose:
            print(f"Generating problem {len(problems) + 1}/{args.n_problems}")
        # TODO: Generate problem here
        pass


def main():
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
    
    main_loop(args)

if __name__ == "__main__":
    main()
