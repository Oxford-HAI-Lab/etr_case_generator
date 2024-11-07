import argparse
import json
import itertools

from pysmt.fnode import FNode

from etr_case_generator import ETRCaseGenerator
from etr_case_generator.ontology import CARDS
from typing import Optional
from dataclasses_json import dataclass_json
from dataclasses import dataclass

from smt_interface.smt_encoder import check_validity


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a dataset of reasoning problems using ETRCaseGenerator"
    )
    parser.add_argument("--dataset_name", type=str, default="etr_for_lm_eval.jsonl", help="Name of the dataset (.jsonl)")
    parser.add_argument(
        "-n",
        "--n_problems",
        type=int,
        default=10,
        help="Number of problems to generate",
    )
    parser.add_argument(
        "--balance",
        action="store_true",
        default=False,
        help="Whether to enforce balanced conclusions between ETR and classical validity.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print verbose output",
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        default=False,
        help="Print problems to stdout instead of saving to file",
    )
    args = parser.parse_args()
    return args


def generate_problems_with_set_conclusions(
    generator: ETRCaseGenerator,
    n_problems,
    conclusions_follow_by_etr: Optional[bool],
    conclusions_valid: Optional[bool],
    verbose: bool = False,
):
    problems = []
    if verbose:
        print(
            f"Generating {n_problems} problems. "
            f"ETR={conclusions_follow_by_etr}; Classical={conclusions_valid}"
        )
    while len(problems) < n_problems:
        for p in generator.generate_reasoning_problems(
            n_views=20,
            categorical_conclusions=conclusions_follow_by_etr,
            n_trials_timeout=1000,
            verbose=verbose,
        ):
            if len(problems) >= n_problems:
                break

            # Check if the conclusion is classically valid
            valid_conclusion = check_validity(p.premise_views, [p.question_conclusion_view])
            
            # If not, and we're enforcing classical validity, skip this problem
            if conclusions_valid == True and not valid_conclusion:
                continue

            p.classically_valid_conclusion = valid_conclusion

            if verbose: print(f"Conclusions: ETR={p.etr_conclusion_is_categorical}, classical={p.classically_valid_conclusion}")

            problems.append(p.to_dict())

    return problems


def main(
    dataset_name: str,
    n_problems: int,
    balance: bool,
    verbose: bool = False,
    print_only: bool = False
):
    """Generate ETR problems for use in lm_eval.

    Args:
        dataset_name (str): The name of the dataset to write.
        n_problems (int): The size of the dataset to generate.
        balance (bool): Whether the dataset should be balanced between ETR and classical
            validity. If true, enforces the confusion matrix between "follows by ETR"
            and "follows classically" to be balanced.
        verbose (bool, optional): Whether to print debugging info. Defaults to False.
        print_only (bool, optional): Whether to just print results and not save them to
            a file. Defaults to False.
    """
    # For now, we're just working with cards (and cards only work with basic objects)
    g = ETRCaseGenerator(ontology=CARDS)
    dataset = []

    if balance:
        for etr, classical in itertools.product([True, False], repeat=2):
            dataset += generate_problems_with_set_conclusions(
                generator=g,
                n_problems=-(-n_problems // 4),  # Round up
                conclusions_follow_by_etr=etr,
                conclusions_valid=classical,
                verbose=verbose,
            )
    else:
        dataset += generate_problems_with_set_conclusions(
            generator=g,
            n_problems=n_problems / 4,
            conclusions_follow_by_etr=None,
            conclusions_valid=None,
            verbose=verbose,
        )


    formatted_problems = []
    for problem in dataset:
        formatted_problem = {
            "question": problem["full_prose"],
            "scoring_guide": {
                **problem,
                "etr_answer": "YES" if problem["question_conclusion_is_etr_conclusion"] else "NO",
                "logically_correct_answer": "YES" if problem["classically_valid_conclusion"] else "NO",
            }
        }
        print(json.dumps(formatted_problem, indent=2))
        formatted_problems.append(formatted_problem)
        
    if not print_only:
        if verbose:
            print(
                f"Saving dataset of length {len(dataset)} to datasets/{dataset_name}"
            )
        with open(f"datasets/{dataset_name}", "w") as f:
            for problem in formatted_problems:
                f.write(json.dumps(problem) + "\n")


if __name__ == "__main__":
    args = parse_args()
    main(
        dataset_name=args.dataset_name,
        n_problems=args.n_problems,
        balance=args.balance,
        verbose=args.verbose,
        print_only=args.print_only
    )
