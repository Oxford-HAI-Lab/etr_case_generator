import argparse
import json
import random
from typing import get_args
from tqdm import tqdm

from etr_case_generator.generator2.generate_problem_from_logical import generate_problem
from etr_case_generator.generator2.reified_problem import FullProblem, QuestionType

from etr_case_generator.ontology import Ontology, get_all_ontologies, natural_name_to_logical_name


def generate_problem_list(n_problems: int, args, question_types: list[str]) -> list[FullProblem]:
    """Generate ETR problems.

    Args:
        n_problems (int): The number of problems to generate
        verbose (bool, optional): Whether to print debugging info. Defaults to False.
    """
    all_ontologies: list[Ontology] = get_all_ontologies()
    # Only SMT problem generation requires this mapping pre-filled. ETR problems will
    # fill it themselves.
    if args.generate_function == "random_smt_problem":
        for o in all_ontologies:
            o.preferred_name_shortening_scheme = args.name_shortening
            o.fill_mapping()

    # Create a counter for each quadrant (erotetic, classical), for the args.balance==True case
    quadrant_counts = {
        (True, True): 0,   # (erotetic, classical)
        (True, False): 0,  # (erotetic, non-classical)
        (False, True): 0,  # (non-erotetic, classical)
        (False, False): 0  # (non-erotetic, non-classical)
    }
    num_needed_per_quadrant: int = (n_problems + 3) // 4  # Round up division

    problems: list[FullProblem] = []
    for i in tqdm(range(args.n_problems), desc="Generating problems"):

        # Generate a random ontology
        ontology = random.choice(all_ontologies)

        # Generate a random problem
        try:
            problem: FullProblem = generate_problem(args, ontology=ontology)

            if args.balance:
                problem_is_erotetic: bool = problem.get_yes_no_conclusion().is_etr_predicted
                problem_is_classical: bool = problem.get_yes_no_conclusion().is_classically_correct
                
                # Check if we need more problems in this quadrant
                current_quadrant = (problem_is_erotetic, problem_is_classical)
                if quadrant_counts[current_quadrant] >= num_needed_per_quadrant:
                    continue  # Skip this problem if we have enough in this quadrant
                
                quadrant_counts[current_quadrant] += 1
        except Exception as e:
            print(f"Failed to generate problem {i + 1} of {n_problems}")
            print(e)
            continue

        problems.append(problem)
        # print(f"Generated Problem {i + 1} of {n_problems}")
        # print(problem.full_string(show_empty=True, question_types=question_types))

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
    parser.add_argument("--num_predicates_per_problem", type=int, default=3, help="Number of predicates to use in each problem. Not used by all generate functions.")
    parser.add_argument("--num_objects_per_problem", type=int, default=3, help="Number of objects to use in each problem. Not used by all generate functions.")
    parser.add_argument("--name_shortening", type=str, default="none", help="How to shorten names of objects and predicates. Options are 'none', 'short', and 'first'.")
    # parser.add_argument("--num_follows", type=int, default=3, help="Number of potential variable assignments which might follow, the top level size of the DNF form of the logical conclusion from the premises.")
    # parser.add_argument("--num_clauses", type=int, default=3, help="A measure of the complexity of the premises.")
    parser.add_argument("--num_pieces", type=int, default=3, help="Number of pieces to use in the premises of each problem. For example, there are for pieces in `(a or b) and (c or d)`.")
    parser.add_argument("--chain_of_thought_prompt", type=str, default="no", help="Whether to include a chain of thought prompt. Options are 'yes', 'no', and 'both'.")
    parser.add_argument("--question_type", type=str, default="all", help="Type of question to ask. Options are 'all', 'yes_no', 'multiple_choice', 'open_ended'.", choices=["all"] + list(get_args(QuestionType)))
    parser.add_argument("--save_file_name", type=str, default="problems", help="Name for saved jsonl files")
    parser.add_argument("--generate_function", type=str, default="random_smt_problem", help="Which function to use in generation.", choices=["random_smt_problem", "random_etr_problem"])
    parser.add_argument("--balance", help="Balance the dataset through the 4 quadrants of erotetic and classical yes/no.", action="store_true")
    # TODO(Ryan): Add parameters for problem generation here
    args = parser.parse_args()

    if args.question_type == "all":
        question_types = get_args(QuestionType)
    else:
        assert args.question_type in get_args(QuestionType), f"Invalid question type: {args.question_type}, must be in: {get_args(QuestionType)}"
        question_types = [args.question_type]

    # Most of the logic occurs here!
    problems: list[FullProblem] = generate_problem_list(n_problems=args.n_problems, args=args, question_types=question_types)

    # Save to file
    for prompt_type in question_types:
        if args.chain_of_thought_prompt == "no" or args.chain_of_thought_prompt == "both":
            fname = f"datasets/{args.save_file_name}_{prompt_type}.jsonl"
            with open(fname, "w") as f:
                for problem in problems:
                    f.write(json.dumps(problem.to_dict_for_jsonl(args, format=prompt_type, chain_of_thought=False)) + "\n")
            print(f"Saved file {fname}")

        if args.chain_of_thought_prompt == "yes" or args.chain_of_thought_prompt == "both":
            fname = f"datasets/{args.save_file_name}_{prompt_type}_with_cot.jsonl"
            with open(fname, "w") as f:
                for problem in problems:
                    f.write(json.dumps(problem.to_dict_for_jsonl(args, format=prompt_type, chain_of_thought=True)) + "\n")
            print(f"Saved file {fname}")

if __name__ == "__main__":
    main()
