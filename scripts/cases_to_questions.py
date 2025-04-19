import json
import inspect
import random
import argparse
from typing import List, Dict, Any
from pyetr import cases

from etr_case_generator.reified_problem import FullProblem, QuestionType, PartialProblem, ReifiedView
from etr_case_generator.ontology import Ontology, get_all_ontologies, natural_name_to_logical_name


def get_case_info(case_class):
    info = {
        "name": case_class.__name__,
        "docstring": inspect.getdoc(case_class),
    }
    if hasattr(case_class, 'v'):
        info['v'] = [str(view) for view in case_class.v]
    if hasattr(case_class, 'c'):
        info['c'] = str(case_class.c) if isinstance(case_class.c, cases.View) else ' '.join(str(view) for view in case_class.c)

    # Add prob variable if it exists
    if hasattr(case_class, 'prob'):
        info['prob'] = str(case_class.prob)

    # Add g1 and g2 variables if they exist
    if hasattr(case_class, 'g1'):
        info['g1'] = str(case_class.g1)
    if hasattr(case_class, 'g2'):
        info['g2'] = str(case_class.g2)

    # Add custom functions if they exist
    custom_functions = [attr for attr in dir(case_class) if callable(getattr(case_class, attr)) and not attr.startswith("__")]
    if custom_functions:
        info['custom_functions'] = custom_functions

    return info


def create_reified_view_from_pyetr_view(view_str: str) -> ReifiedView:
    """Convert a pyETR View string to a ReifiedView object."""
    reified_view = ReifiedView()
    reified_view.logical_form_etr = view_str
    return reified_view

def create_full_problem(case: Dict[str, Any], all_cases: List[Dict[str, Any]], 
                        ontology: Ontology, question_type: QuestionType = "multiple_choice") -> FullProblem:
    """Create a FullProblem from a case."""
    # Create the premises (views)
    premises = [create_reified_view_from_pyetr_view(v) for v in case['v']]
    
    # Create the correct conclusion
    correct_conclusion = create_reified_view_from_pyetr_view(case['c'])
    
    # Get 3 random wrong conclusions for multiple choice
    wrong_conclusions = []
    if question_type == "multiple_choice":
        while len(wrong_conclusions) < 3:
            random_case = random.choice(all_cases)
            if random_case != case and random_case['c'] not in [w.logical_form_etr for w in wrong_conclusions]:
                wrong_conclusions.append(create_reified_view_from_pyetr_view(random_case['c']))
    
    # Create the FullProblem
    problem = FullProblem()
    problem.views = premises
    problem.etr_predicted_conclusion = correct_conclusion
    problem.classically_correct_conclusion = correct_conclusion  # Assuming ETR and classical logic agree for these examples
    
    # For multiple choice, add the wrong conclusions
    if question_type == "multiple_choice":
        problem.wrong_conclusions = wrong_conclusions
    
    # Fill out the problem with the ontology
    problem.fill_out(ontology=ontology)
    
    # Add metadata
    problem.seed_id = case['name']
    problem.description = case.get('docstring', '')
    
    return problem


def parse_args():
    parser = argparse.ArgumentParser(description="Generate ETR questions from pyETR cases")
    parser.add_argument("-n", "--num-problems", type=int, default=3, 
                        help="Number of problems to generate per case")
    parser.add_argument("-o", "--output", type=str, default="datasets/etr_61_cases",
                        help="Base name for output files (without extension)")
    parser.add_argument("-t", "--question-types", nargs="+", 
                        choices=["all", "multiple_choice", "yes_no", "open_ended"], 
                        default=["multiple_choice"],
                        help="Question types to generate ('all' generates all types)")
    parser.add_argument("--chain-of-thought", action="store_true",
                        help="Include chain of thought prompts")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Get all cases
    all_cases = []
    for name, obj in inspect.getmembers(cases):
        if inspect.isclass(obj) and issubclass(obj, cases.BaseExample) and obj != cases.BaseExample:
            all_cases.append(get_case_info(obj))
    
    # Get all ontologies
    all_ontologies = get_all_ontologies()
    
    # Determine which question types to generate
    question_types = args.question_types
    if "all" in question_types:
        question_types = ["multiple_choice", "yes_no", "open_ended"]
    
    # Generate problems for each question type
    for question_type in question_types:
        full_problems = []
        
        # For each case, generate n problems with different ontologies
        for case in all_cases:
            try:
                for _ in range(args.num_problems):
                    # Choose a random ontology
                    ontology = random.choice(all_ontologies)
                    
                    # Create a full problem
                    problem = create_full_problem(case, all_cases, ontology, question_type)
                    full_problems.append(problem)
            except Exception as e:
                print(f"Error processing case {case['name']}: {str(e)}")
                continue
        
        # Shuffle the problems
        random.shuffle(full_problems)
        
        # Save to file
        output_file = f"{args.output}_{question_type}"
        if args.chain_of_thought:
            output_file += "_with_cot"
        output_file += ".jsonl"
        
        with open(output_file, 'w') as f:
            for problem in full_problems:
                f.write(json.dumps(problem.to_dict_for_jsonl(args, format=question_type, 
                                                            chain_of_thought=args.chain_of_thought)) + '\n')
        
        print(f"Generated {len(full_problems)} problems in {output_file}")


if __name__ == "__main__":
    main()
