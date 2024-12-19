import argparse
import json
import random
from typing import get_args

from etr_case_generator.generator2.problem_in_smt import generate_problem_in_smt
from etr_case_generator.generator2.reified_problem import FullProblem, QuestionType

from etr_case_generator.ontology import Ontology, get_all_ontologies, natural_name_to_logical_name


def generate_problem_list(n_problems: int, args) -> list[FullProblem]:
    """Generate ETR problems.

    Args:
        n_problems (int): The number of problems to generate
        verbose (bool, optional): Whether to print debugging info. Defaults to False.
    """
    all_ontologies: list[Ontology] = get_all_ontologies()
    for o in all_ontologies:
        o.fill_mapping()
        o.preferred_name_shortening_scheme = args.name_shortening

    problems: list[FullProblem] = []
    for i in range(args.n_problems):
        if args.verbose:
            print(f"Generating problem {len(problems) + 1}/{args.n_problems}")

        # Generate a random ontology
        ontology = random.choice(all_ontologies)
        small_ontology = ontology.create_smaller_ontology(args.num_predicates_per_problem, args.num_objects_per_problem)

        problem = generate_problem_in_smt(args, ontology=small_ontology)
        problems.append(problem)
        print(f"Generated Problem {i + 1} of {n_problems}")
        print(problem.full_string(show_empty=True))

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
    parser.add_argument("--num_predicates_per_problem", type=int, default=3, help="Number of predicates to use in each problem")
    parser.add_argument("--num_objects_per_problem", type=int, default=3, help="Number of objects to use in each problem")
    parser.add_argument("--name_shortening", type=str, default="none", help="How to shorten names of objects and predicates. Options are 'none', 'short', and 'first'.")
    parser.add_argument("--num_follows", type=int, default=3, help="Number of potential variable assignments which might follow, the top level size of the DNF form of the logical conclusion from the premises.")
    parser.add_argument("--num_clauses", type=int, default=3, help="A measure of the complexity of the premises.")
    parser.add_argument("--chain_of_thought_prompt", type=str, default="no", help="Whether to include a chain of thought prompt. Options are 'yes', 'no', and 'both'.")
    parser.add_argument("--save_file_name", type=str, default="problems", help="Name for saved jsonl files")

    args = parser.parse_args()

    # TODO Args like num_clauses for the actual generation

    problems: list[FullProblem] = generate_problem_list(n_problems=args.n_problems, args=args)

    # Save to file
    for prompt_type in get_args(QuestionType):
        if args.chain_of_thought_prompt == "no" or args.chain_of_thought_prompt == "both":
            fname = f"datasets/{args.save_file_name}_{prompt_type}.jsonl"
            with open(fname, "w") as f:
                for problem in problems:
                    f.write(json.dumps(problem.to_dict_for_jsonl(prompt_type, chain_of_thought=False)) + "\n")
            print(f"Saved file {fname}")

        if args.chain_of_thought_prompt == "yes" or args.chain_of_thought_prompt == "both":
            fname = f"datasets/{args.save_file_name}_{prompt_type}_with_cot.jsonl"
            with open(fname, "w") as f:
                for problem in problems:
                    f.write(json.dumps(problem.to_dict_for_jsonl(prompt_type, chain_of_thought=True)) + "\n")
            print(f"Saved file {fname}")

if __name__ == "__main__":
    main()
