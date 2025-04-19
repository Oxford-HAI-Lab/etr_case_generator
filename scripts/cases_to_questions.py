import json
import inspect
import random
import argparse
from typing import List, Dict, Any
from pyetr import cases

from etr_case_generator.reified_problem import FullProblem, QuestionType, PartialProblem, ReifiedView, Conclusion
from etr_case_generator.ontology import Ontology, get_all_ontologies, natural_name_to_logical_name
from etr_case_generator.full_problem_creator import full_problem_from_partial_problem


def get_case_info(case_class) -> Dict[str, Any]:
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


def update_to_ontology(partial_problem: PartialProblem, ontology: Ontology) -> None:
    """
    Replace predicates and objects in the partial problem with random ones from the ontology.
    Ensures consistent mapping across all premises and conclusions.
    """
    import re
    
    # Extract all predicates and objects from the problem
    all_etr_text = ""
    for premise in partial_problem.premises:
        all_etr_text += premise.logical_form_etr + " "
    
    # Find all predicate names (words followed by open parenthesis)
    predicate_pattern = r'([A-Za-z][A-Za-z0-9_]*)\('
    predicates = set(re.findall(predicate_pattern, all_etr_text))
    
    # Find all object names (words followed by '()')
    object_pattern = r'([A-Za-z][A-Za-z0-9_]*)\(\)'
    objects = set(re.findall(object_pattern, all_etr_text))
    
    # Remove special keywords that shouldn't be replaced
    special_keywords = {'forall', 'exists', 'and', 'or', 'not', 'implies', 'iff'}
    predicates = {p for p in predicates if p.lower() not in special_keywords}
    
    # Create random mappings
    predicate_mapping = {}
    available_predicates = [pred.name for pred in ontology.predicates]
    random.shuffle(available_predicates)
    
    for i, pred in enumerate(predicates):
        if i < len(available_predicates):
            predicate_mapping[pred] = available_predicates[i]
        else:
            # If we run out of ontology predicates, reuse them
            predicate_mapping[pred] = available_predicates[i % len(available_predicates)]
    
    object_mapping = {}
    available_objects = [obj for obj in ontology.objects]
    random.shuffle(available_objects)
    
    for i, obj in enumerate(objects):
        if i < len(available_objects):
            object_mapping[obj] = available_objects[i]
        else:
            # If we run out of ontology objects, reuse them
            object_mapping[obj] = available_objects[i % len(available_objects)]
    
    # Apply mappings to all premises
    for premise in partial_problem.premises:
        # Replace predicates
        for old_pred, new_pred in predicate_mapping.items():
            # Use word boundaries to ensure we only replace whole words
            premise.logical_form_etr = re.sub(r'\b' + old_pred + r'\(', 
                                             natural_name_to_logical_name(new_pred, "none") + '(', 
                                             premise.logical_form_etr)
        
        # Replace objects
        for old_obj, new_obj in object_mapping.items():
            # Use word boundaries to ensure we only replace whole words
            premise.logical_form_etr = re.sub(r'\b' + old_obj + r'\(\)', 
                                             natural_name_to_logical_name(new_obj, "none") + '()', 
                                             premise.logical_form_etr)
        
        # Recreate the ETR view with the updated text
        premise.logical_form_etr_view = cases.View.from_str(premise.logical_form_etr)
    
    # If there's an ETR what follows, update it too
    if partial_problem.etr_what_follows:
        for old_pred, new_pred in predicate_mapping.items():
            partial_problem.etr_what_follows.logical_form_etr = re.sub(
                r'\b' + old_pred + r'\(', 
                natural_name_to_logical_name(new_pred, "none") + '(', 
                partial_problem.etr_what_follows.logical_form_etr)
        
        for old_obj, new_obj in object_mapping.items():
            partial_problem.etr_what_follows.logical_form_etr = re.sub(
                r'\b' + old_obj + r'\(\)', 
                natural_name_to_logical_name(new_obj, "none") + '()', 
                partial_problem.etr_what_follows.logical_form_etr)
        
        partial_problem.etr_what_follows.logical_form_etr_view = cases.View.from_str(
            partial_problem.etr_what_follows.logical_form_etr)

def create_reified_view_from_pyetr_view(view_str: str) -> ReifiedView:
    """Convert a pyETR View string to a ReifiedView object."""
    reified_view = ReifiedView()
    reified_view.logical_form_etr = view_str
    # Create the ETR view object to enable atom counting and other operations
    reified_view.logical_form_etr_view = cases.View.from_str(view_str)
    return reified_view

def create_full_problem(case: Dict[str, Any], all_cases: List[Dict[str, Any]], 
                        ontology: Ontology, question_type: QuestionType = "multiple_choice") -> FullProblem:
    """Create a FullProblem from a case."""
    # Prepare the ontology with the preferred naming scheme
    ontology.preferred_name_shortening_scheme = "short"
    ontology.fill_mapping()
    
    # Create the premises (views)
    premises = [create_reified_view_from_pyetr_view(v) for v in case['v']]
    
    # Create the correct conclusion
    correct_conclusion = create_reified_view_from_pyetr_view(case['c'])
    
    # Create a PartialProblem first
    partial_problem = PartialProblem(
        premises=premises,
        seed_id=case['name']
    )
    
    # Replace generic predicates and objects with domain-specific ones
    update_to_ontology(partial_problem, ontology)
    
    # Fill out the premises with the ontology
    for premise in partial_problem.premises:
        premise.fill_out(ontology)
    
    # Get 3 random wrong conclusions for multiple choice
    wrong_conclusions = []
    possible_conclusions = []
    multiple_choices = []
    
    if question_type == "multiple_choice":
        attempts = 0
        while len(wrong_conclusions) < 3 and attempts < 20:
            attempts += 1
            random_case = random.choice(all_cases)
            if random_case != case and random_case['c'] not in [w.logical_form_etr for w in wrong_conclusions]:
                try:
                    wrong_view = create_reified_view_from_pyetr_view(random_case['c'])
                    wrong_view.fill_out(ontology)
                    wrong_conclusions.append(wrong_view)
                    
                    # Create a Conclusion object for each wrong conclusion
                    wrong_conclusion = Conclusion(view=wrong_view)
                    wrong_conclusion.is_etr_predicted = False
                    wrong_conclusion.is_classically_correct = False
                    multiple_choices.append(wrong_conclusion)
                except Exception:
                    continue
    
    # Create a Conclusion object for the correct conclusion
    correct_conclusion.fill_out(ontology)
    etr_conclusion = Conclusion(view=correct_conclusion)
    etr_conclusion.is_etr_predicted = True
    etr_conclusion.is_classically_correct = True  # Assuming ETR and classical logic agree for these examples
    
    # Add the correct conclusion to multiple_choices
    if question_type == "multiple_choice":
        multiple_choices.append(etr_conclusion)
        random.shuffle(multiple_choices)
    
    # For yes/no questions, create possible conclusions
    if question_type == "yes_no":
        possible_conclusions = [etr_conclusion]
        # Add some wrong conclusions as distractors
        for wrong_view in wrong_conclusions[:2]:  # Add up to 2 wrong conclusions
            wrong_conclusion = Conclusion(view=wrong_view)
            wrong_conclusion.is_etr_predicted = False
            wrong_conclusion.is_classically_correct = False
            possible_conclusions.append(wrong_conclusion)
        random.shuffle(possible_conclusions)
    
    # Set up the ETR predicted conclusion in the partial problem
    partial_problem.etr_what_follows = correct_conclusion
    partial_problem.possible_conclusions_from_logical = [etr_conclusion]
    partial_problem.possible_conclusions_from_etr = [etr_conclusion]
    
    # Create the FullProblem with all required fields
    from etr_case_generator.full_problem_creator import full_problem_from_partial_problem
    problem = full_problem_from_partial_problem(partial_problem, ontology)
    
    # Override some fields that might have been set differently
    if question_type == "multiple_choice":
        problem.multiple_choices = multiple_choices
    if question_type == "yes_no":
        problem.possible_conclusions = possible_conclusions
        if possible_conclusions:
            # Set the yes_or_no_conclusion_chosen_index to the index of the correct conclusion
            for i, conclusion in enumerate(possible_conclusions):
                if conclusion.is_classically_correct:
                    problem.yes_or_no_conclusion_chosen_index = i
                    break
    
    # Add metadata
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
                        default=["all"],
                        help="Question types to generate ('all' generates all types)")
    parser.add_argument("--chain-of-thought", action="store_true",
                        help="Include chain of thought prompts")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Get all cases from cases.__all__
    all_cases: list[dict[str, Any]] = []
    for name in cases.__all__:
        if hasattr(cases, name):
            obj = getattr(cases, name)
            if inspect.isclass(obj) and issubclass(obj, cases.BaseExample) and obj != cases.BaseExample:
                try:
                    case_info = get_case_info(obj)
                    all_cases.append(case_info)
                except Exception as e:
                    print(f"Error getting info for case {name}: {str(e)}")
    
    # For development/testing, use a small subset
    all_cases = [get_case_info(case) for case in [cases.e1, cases.e2, cases.e3]]  # TODO: Remove after development is done  -- Aider: DO NOT REMOVE

    print(f"Found {len(all_cases)} valid cases from cases.__all__")
    
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
                    
                    # Randomly select a subset of predicates and objects for variety
                    num_predicates = min(random.randint(3, 6), len(ontology.predicates))
                    num_objects = min(random.randint(3, 6), len(ontology.objects))
                    smaller_ontology = ontology.create_smaller_ontology(num_predicates, num_objects)
                    
                    # Create a full problem
                    problem = create_full_problem(case, all_cases, smaller_ontology, question_type)
                    full_problems.append(problem)
            except Exception as e:
                print(f"Error processing case {case['name']}: {str(e)}")
                raise e

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
