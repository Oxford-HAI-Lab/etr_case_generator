import argparse
import json
from etr_case_generator.generator import ETRCaseGenerator


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a dataset of reasoning problems using ETRCaseGenerator"
    )
    parser.add_argument("dataset_name", type=str, help="Name of the dataset")
    parser.add_argument(
        "-n",
        "--n_problems",
        type=int,
        default=100,
        help="Number of problems to generate",
    )
    parser.add_argument(
        "--categorical_conclusions",
        choices=["all", "parity", "random"],
        default="all",
        help="Enforce ETR conclusions are categorical in all problems, or enforce parity, or nothing",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print verbose output",
    )
    args = parser.parse_args()
    return args


def generate_reasoning_problems(
    generator, n_problems, require_categorical: bool, verbose: bool = False
):
    problems = []
    while len(problems) < n_problems:
        for p in generator.generate_reasoning_problems(
            n_views=20,
            require_categorical_etr=require_categorical,
            n_trials_timeout=1000,
            verbose=verbose,
        ):
            if len(problems) >= n_problems:
                break
            problems.append(p.to_dict())
        if verbose:
            print("===> Retrying... Dataset so far: ", len(problems))

    return problems


def main(
    dataset_name: str, n_problems: int, categorical_conclusions: str, verbose: bool
):
    g = ETRCaseGenerator()
    dataset = []

    if categorical_conclusions == "parity":
        for require_categorical in [True, False]:
            dataset += generate_reasoning_problems(
                generator=g,
                n_problems=n_problems / 2,
                require_categorical=require_categorical,
                verbose=verbose,
            )
    else:
        require_categorical = False
        if categorical_conclusions == "all":
            require_categorical = True

        dataset += generate_reasoning_problems(
            generator=g,
            n_problems=n_problems,
            require_categorical=require_categorical,
            verbose=verbose,
        )

    if verbose:
        print(
            f"Saving dataset of length {len(dataset)} to datasets/{dataset_name}.json"
        )
    json.dump(dataset, open(f"datasets/{dataset_name}.json", "w"))


if __name__ == "__main__":
    args = parse_args()
    main(
        dataset_name=args.dataset_name,
        n_problems=args.n_problems,
        categorical_conclusions=args.categorical_conclusions,
        verbose=args.verbose,
    )
