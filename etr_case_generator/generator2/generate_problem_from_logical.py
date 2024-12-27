from typing import get_args

from etr_case_generator.generator2.etr_generator import random_etr_problem
from etr_case_generator.generator2.reified_problem import FullProblem, QuestionType, PartialProblem, Conclusion, \
    ReifiedView
from etr_case_generator.generator2.full_problem_creator import full_problem_from_partial_problem
from etr_case_generator.ontology import ELEMENTS, Ontology
from etr_case_generator.generator2.smt_generator import random_smt_problem, SMTProblem, generate_conclusions, \
    add_conclusions
from etr_case_generator.view_to_natural_language import view_to_natural_language


def generate_problem(args, ontology: Ontology = ELEMENTS) -> FullProblem:
    # Generate partial problems
    if args.generate_function == "random_smt_problem":
        small_ontology = ontology.create_smaller_ontology(args.num_predicates_per_problem, args.num_objects_per_problem)
        smt_problem: SMTProblem = random_smt_problem(ontology=small_ontology, total_num_pieces=args.num_pieces)
        partial_problem = smt_problem.to_partial_problem()
    elif args.generate_function == "random_etr_problem":
        partial_problem: PartialProblem = random_etr_problem(ontology=ontology)

        # Use this space to update the natural language object mapping for the ontology.
        assert partial_problem.premises is not None
        for p in partial_problem.premises:
            assert p.logical_form_etr_view is not None
            english_form, obj_map = view_to_natural_language(
                ontology=ontology, 
                view=p.logical_form_etr_view,
                obj_map=ontology.short_name_to_full_name
            )
            p.english_form = english_form
            ontology.short_name_to_full_name.update(obj_map)
    else:
        raise ValueError(f"Unknown generate_function: {args.generate_function}")

    # Fill out the partial problem as much as possible, e.g. fill in the ETR from the SMT and vice versa
    partial_problem.fill_out(ontology=ontology)
    partial_problem.add_etr_predictions(ontology=ontology)
    partial_problem.add_classical_logic_predictions()
    if partial_problem.possible_conclusions_from_etr is None and partial_problem.possible_conclusions_from_logical is None:
        # If there are no conclusions, make some!
        add_conclusions(partial_problem, ontology=ontology)

    # Flesh out the problems with text and everything
    full_problem: FullProblem = full_problem_from_partial_problem(partial_problem, ontology=ontology)

    return full_problem
