import json
import inspect
import random
import argparse
import re
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


def update_to_ontology(partial_problem: PartialProblem, ontology: Ontology) -> PartialProblem:
    """
    Replace predicates and objects in the partial problem with random ones from the ontology.
    Ensures consistent mapping across all premises and conclusions.
    
    This function thoroughly updates all parts of the problem, including:
    - All premises
    - ETR what follows conclusion
    - Possible conclusions from logical
    - Possible conclusions from ETR
    
    Args:
        partial_problem: The original problem to update
        ontology: The ontology to use for replacements
        
    Returns:
        A new PartialProblem with updated predicates and objects
        
    Raises:
        AssertionError: If any part of the problem wasn't properly updated
    """
    # Create a copy of the partial problem
    from copy import deepcopy
    new_problem = deepcopy(partial_problem)
    
    # Verify we have premises to work with
    assert new_problem.premises is not None and len(new_problem.premises) > 0, "No premises found in partial problem"
    
    # Extract all predicates and objects from the problem
    all_etr_text = ""
    for premise in new_problem.premises:
        assert premise.logical_form_etr is not None, "Premise missing logical_form_etr"
        all_etr_text += premise.logical_form_etr + " "
    
    # If there's an ETR what follows, include it in the text to analyze
    if new_problem.etr_what_follows and new_problem.etr_what_follows.logical_form_etr:
        all_etr_text += new_problem.etr_what_follows.logical_form_etr + " "
    
    # Include possible conclusions in the text to analyze
    if new_problem.possible_conclusions_from_logical:
        for conclusion in new_problem.possible_conclusions_from_logical:
            if conclusion.view and conclusion.view.logical_form_etr:
                all_etr_text += conclusion.view.logical_form_etr + " "
    
    if new_problem.possible_conclusions_from_etr:
        for conclusion in new_problem.possible_conclusions_from_etr:
            if conclusion.view and conclusion.view.logical_form_etr:
                all_etr_text += conclusion.view.logical_form_etr + " "
    
    # Find all predicate names (words followed by open parenthesis)
    predicate_pattern = r'([A-Za-z][A-Za-z0-9_]*)\('
    predicates = set(re.findall(predicate_pattern, all_etr_text))
    
    # Find all object names (words followed by '()')
    object_pattern = r'([A-Za-z][A-Za-z0-9_]*)\(\)'
    objects = set(re.findall(object_pattern, all_etr_text))
    
    # Remove special keywords that shouldn't be replaced
    special_keywords = {'forall', 'exists', 'and', 'or', 'not', 'implies', 'iff', 
                       'A', 'E', 'x', 'y', 'z', 'w', 'v', 'u', 't', 's'}
    predicates = {p for p in predicates if p.lower() not in special_keywords}
    
    # Ensure we have enough predicates and objects in the ontology
    assert len(ontology.predicates) > 0, "Ontology has no predicates"
    assert len(ontology.objects) > 0, "Ontology has no objects"
    
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
    
    # Helper function to apply mappings to a single ETR string
    def apply_mappings_to_etr(etr_str):
        if not etr_str:
            return etr_str
            
        result = etr_str
        # Replace predicates
        for old_pred, new_pred in predicate_mapping.items():
            # Use word boundaries to ensure we only replace whole words
            result = re.sub(r'\b' + old_pred + r'\(', 
                           natural_name_to_logical_name(new_pred, "none") + '(', 
                           result)
        
        # Replace objects
        for old_obj, new_obj in object_mapping.items():
            # Use word boundaries to ensure we only replace whole words
            result = re.sub(r'\b' + old_obj + r'\(\)', 
                           natural_name_to_logical_name(new_obj, "none") + '()', 
                           result)
        
        return result
    
    # Helper function to update a ReifiedView
    def update_reified_view(view):
        if not view:
            return
            
        if view.logical_form_etr:
            original = view.logical_form_etr
            view.logical_form_etr = apply_mappings_to_etr(view.logical_form_etr)
            # Verify the update happened if there were mappings to apply
            if predicates or objects:
                assert view.logical_form_etr != original or not any(p in original for p in predicates) and not any(o in original for o in objects), \
                    f"Failed to update ETR: {original}"
            
            # Recreate the ETR view with the updated text
            view.logical_form_etr_view = cases.View.from_str(view.logical_form_etr)
    
    # Apply mappings to all premises
    for premise in new_problem.premises:
        update_reified_view(premise)
    
    # If there's an ETR what follows, update it too
    if new_problem.etr_what_follows:
        update_reified_view(new_problem.etr_what_follows)
    
    # Update possible conclusions from logical
    if new_problem.possible_conclusions_from_logical:
        for conclusion in new_problem.possible_conclusions_from_logical:
            if conclusion.view:
                update_reified_view(conclusion.view)
    
    # Update possible conclusions from ETR
    if new_problem.possible_conclusions_from_etr:
        for conclusion in new_problem.possible_conclusions_from_etr:
            if conclusion.view:
                update_reified_view(conclusion.view)
    
    # Verify that all premises were updated
    for i, premise in enumerate(new_problem.premises):
        assert premise.logical_form_etr_view is not None, f"Premise {i} missing logical_form_etr_view after update"
    
    # Verify that ETR what follows was updated if it exists
    if new_problem.etr_what_follows:
        assert new_problem.etr_what_follows.logical_form_etr_view is not None, \
            "etr_what_follows missing logical_form_etr_view after update"
    
    return new_problem

def create_reified_view_from_pyetr_view(view_str: str) -> ReifiedView:
    """Convert a pyETR View string to a ReifiedView object."""
    reified_view = ReifiedView()
    reified_view.logical_form_etr = view_str
    # Create the ETR view object to enable atom counting and other operations
    reified_view.logical_form_etr_view = cases.View.from_str(view_str)
    return reified_view

def prepare_partial_problem(case: Dict[str, Any], ontology: Ontology) -> tuple[PartialProblem, ReifiedView]:
    """
    Create and prepare a PartialProblem from a case with the given ontology.
    
    Args:
        case: The case dictionary containing premises and conclusion
        ontology: The ontology to use for the problem
        
    Returns:
        A tuple of (partial_problem, correct_conclusion)
    """
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
        seed_id=case['name'],
        etr_what_follows=correct_conclusion  # Set the correct conclusion as etr_what_follows
    )
    
    # Create a Conclusion object for the correct conclusion
    etr_conclusion = Conclusion(view=correct_conclusion)
    etr_conclusion.is_etr_predicted = True
    etr_conclusion.is_classically_correct = True
    
    # Set up possible conclusions
    partial_problem.possible_conclusions_from_logical = [etr_conclusion]
    partial_problem.possible_conclusions_from_etr = [etr_conclusion]
    
    # Replace generic predicates and objects with domain-specific ones
    # This will update all parts of the problem including the conclusion
    partial_problem = update_to_ontology(partial_problem, ontology)
    
    # Fill out the premises with the ontology
    for premise in partial_problem.premises:
        premise.fill_out(ontology)
    
    # Get the updated conclusion from the partial problem
    correct_conclusion = partial_problem.etr_what_follows
    assert correct_conclusion is not None, "Correct conclusion is missing after update_to_ontology"
    
    # Fill out the conclusion with the ontology
    correct_conclusion.fill_out(ontology)
    
    # Verify that all parts were properly filled out
    assert all(premise.english_form is not None for premise in partial_problem.premises), \
        "Some premises are missing english_form after fill_out"
    assert correct_conclusion.english_form is not None, \
        "Correct conclusion is missing english_form after fill_out"
    
    return partial_problem, correct_conclusion

def create_multiple_choice_options(case: Dict[str, Any], all_cases: List[Dict[str, Any]], 
                                  ontology: Ontology, correct_conclusion: ReifiedView) -> list[Conclusion]:
    """
    Create multiple choice options including the correct conclusion and 3 wrong ones.
    
    Args:
        case: The current case
        all_cases: All available cases to choose wrong conclusions from
        ontology: The ontology to use
        correct_conclusion: The correct conclusion for this problem
        
    Returns:
        A list of Conclusion objects for multiple choice
    """
    wrong_conclusions = []
    multiple_choices = []
    
    # Get 3 random wrong conclusions
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
    etr_conclusion = Conclusion(view=correct_conclusion)
    etr_conclusion.is_etr_predicted = True
    etr_conclusion.is_classically_correct = True  # Assuming ETR and classical logic agree for these examples
    
    # Add the correct conclusion to multiple_choices
    multiple_choices.append(etr_conclusion)
    random.shuffle(multiple_choices)
    
    return multiple_choices

def create_yes_no_options(correct_conclusion: ReifiedView, wrong_views: list[ReifiedView]) -> list[Conclusion]:
    """
    Create yes/no question options including the correct conclusion and some wrong ones.
    
    Args:
        correct_conclusion: The correct conclusion
        wrong_views: List of wrong views to choose from
        
    Returns:
        A list of Conclusion objects for yes/no questions
    """
    possible_conclusions = []
    
    # Create a Conclusion object for the correct conclusion
    etr_conclusion = Conclusion(view=correct_conclusion)
    etr_conclusion.is_etr_predicted = True
    etr_conclusion.is_classically_correct = True
    
    possible_conclusions = [etr_conclusion]
    
    # Add some wrong conclusions as distractors
    for wrong_view in wrong_views[:2]:  # Add up to 2 wrong conclusions
        wrong_conclusion = Conclusion(view=wrong_view)
        wrong_conclusion.is_etr_predicted = False
        wrong_conclusion.is_classically_correct = False
        possible_conclusions.append(wrong_conclusion)
    
    random.shuffle(possible_conclusions)
    return possible_conclusions

def create_full_problem(case: Dict[str, Any], all_cases: List[Dict[str, Any]], 
                        ontology: Ontology, question_type: QuestionType = "multiple_choice") -> FullProblem:
    """Create a FullProblem from a case."""
    # Prepare the partial problem and correct conclusion
    partial_problem, correct_conclusion = prepare_partial_problem(case, ontology)
    
    # Get wrong conclusions for multiple choice or yes/no questions
    wrong_conclusions = []
    multiple_choices = []
    possible_conclusions = []
    
    # Create a Conclusion object for the correct conclusion
    etr_conclusion = Conclusion(view=correct_conclusion)
    etr_conclusion.is_etr_predicted = True
    etr_conclusion.is_classically_correct = True
    
    # Generate options based on question type
    if question_type == "multiple_choice":
        multiple_choices = create_multiple_choice_options(case, all_cases, ontology, correct_conclusion)
        # Extract wrong views for potential use in yes/no questions
        wrong_conclusions = [conclusion.view for conclusion in multiple_choices 
                            if not conclusion.is_classically_correct]
    
    if question_type == "yes_no":
        # If we already have wrong conclusions from multiple choice, use them
        if not wrong_conclusions:
            # Otherwise, generate some wrong conclusions
            for _ in range(2):
                random_case = random.choice(all_cases)
                if random_case != case:
                    try:
                        wrong_view = create_reified_view_from_pyetr_view(random_case['c'])
                        wrong_view.fill_out(ontology)
                        wrong_conclusions.append(wrong_view)
                    except Exception:
                        continue
        
        possible_conclusions = create_yes_no_options(correct_conclusion, wrong_conclusions)
    
    # The ETR predicted conclusion is already set up in prepare_partial_problem
    # Just verify that it's still properly set
    assert partial_problem.etr_what_follows is not None, "ETR predicted conclusion is missing"
    assert partial_problem.possible_conclusions_from_logical is not None, "Possible conclusions from logical is missing"
    assert partial_problem.possible_conclusions_from_etr is not None, "Possible conclusions from ETR is missing"
    
    # Create the FullProblem with all required fields
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
