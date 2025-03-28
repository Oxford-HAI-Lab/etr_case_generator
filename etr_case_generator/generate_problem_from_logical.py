from typing import Callable, Counter

import pyetr

from etr_case_generator.etr_generator import random_etr_problem, boost_low_num_atom_problems
from etr_case_generator.etr_generator_no_queue import ETRGeneratorIndependent
from etr_case_generator.logic_types import AtomCount
from etr_case_generator.reified_problem import FullProblem, QuestionType, PartialProblem, Conclusion, \
    ReifiedView
from etr_case_generator.full_problem_creator import full_problem_from_partial_problem
from etr_case_generator.ontology import ELEMENTS, Ontology, natural_name_to_logical_name
from etr_case_generator.smt_generator import random_smt_problem, SMTProblem, generate_conclusions, \
    add_conclusions
from etr_case_generator.view_to_natural_language import view_to_natural_language
from pyetr import View

# TODO write similar method to below that takes any View and returns something like
# {A(a())}^{B(a())}
# This method would automatically be a way to map anything into our queue

def renamed_view(view: View, renames: dict[str, str]) -> View:
    new_view_str = ""
    for c in view.to_str():
        if c in renames.keys():
            new_view_str += natural_name_to_logical_name(renames[c])
        else:
            new_view_str += c
    return View.from_str(new_view_str)


def generate_problem(args, ontology: Ontology = ELEMENTS, needed_counts: Counter[AtomCount] = None, generator: ETRGeneratorIndependent=None) -> FullProblem:
    # Generate partial problems
    if args.generate_function == "random_smt_problem":
        if args.num_atoms_set:
            raise NotImplementedError("Balancing num atoms not implemented for SMT problems")
        small_ontology = ontology.create_smaller_ontology(args.num_predicates_per_problem, args.num_objects_per_problem)
        smt_problem: SMTProblem = random_smt_problem(ontology=small_ontology, total_num_pieces=args.num_pieces)
        partial_problem = smt_problem.to_partial_problem()
    elif args.generate_function == "random_etr_problem":
        # This is the main path!
        random_etr_problem_kwargs = {}
        if args.num_atoms_set:
            # partial_problem: PartialProblem = random_etr_problem()
            random_etr_problem_kwargs["bias_function"] = boost_low_num_atom_problems
        if needed_counts:
            random_etr_problem_kwargs["needed_counts"] = needed_counts
        random_etr_problem_kwargs["categorical_only"] = not args.non_categorical_okay

        assert generator is not None

        partial_problem = generator.generate_problem(needed_counts=needed_counts, categorical_only=not args.non_categorical_okay, multi_view=args.multi_view)

        # Use this space to update the natural language object mapping for the ontology.
        assert partial_problem.premises is not None
        for p in partial_problem.premises:
            assert p.logical_form_etr_view is not None
            english_form, obj_map = view_to_natural_language(
                ontology=ontology, 
                view=p.logical_form_etr_view,
                obj_map=ontology.logical_placeholder_to_short_name
            )
            p.english_form = english_form
            ontology.logical_placeholder_to_short_name.update(obj_map)

            # Now that we have the English form, replace placeholders in the ETR view
            try:
                p.logical_form_etr_view = renamed_view(
                    p.logical_form_etr_view,
                    renames=ontology.logical_placeholder_to_short_name
                )
            except Exception as e:
                # TODO This should make sure it's a pyetr.parsing.common.ParsingError
                print("ParsingException caught when renaming view.")
                print(p.logical_form_etr_view)
                print("The ontology is:", ontology.name)
                raise e

        # Do the ETR supported conclusion in addition to the premises
        assert partial_problem.etr_what_follows is not None
        assert partial_problem.etr_what_follows.logical_form_etr_view is not None
        english_form, obj_map = view_to_natural_language(
            ontology=ontology, 
            view=partial_problem.etr_what_follows.logical_form_etr_view,
            obj_map=ontology.logical_placeholder_to_short_name
        )
        partial_problem.etr_what_follows.english_form = english_form
        ontology.logical_placeholder_to_short_name.update(obj_map)
        # Now that we have the English form, replace placeholders in the ETR view
        partial_problem.etr_what_follows.logical_form_etr_view = renamed_view(
            partial_problem.etr_what_follows.logical_form_etr_view,
            renames=ontology.logical_placeholder_to_short_name
        )

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
    full_problem.etr_predicted_conclusion_is_categorical = partial_problem.etr_predicted_conclusion_is_categorical

    return full_problem
