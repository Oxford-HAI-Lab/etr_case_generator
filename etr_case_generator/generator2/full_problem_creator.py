from etr_case_generator import Ontology
from etr_case_generator.generator2.etr_logic import get_etr_conclusion
from etr_case_generator.generator2.formatting_smt import format_smt, smt_to_etr, smt_to_english
from etr_case_generator.generator2.reified_problem import FullProblem, ReifiedView
from etr_case_generator.ontology import ELEMENTS
from etr_case_generator.generator2.smt_generator import SMTProblem


def full_problem_from_smt_problem(smt_problem: SMTProblem, ontology: Ontology=ELEMENTS) -> FullProblem:
    """Convert an SMTProblem to a FullProblem, including yes/no and multiple choice conclusions."""

    # Convert each FNode view to a ReifiedView
    reified_views = []
    for view in smt_problem.views:
        reified_view = ReifiedView(
            logical_form_smt=format_smt(view),  # Formatted string representation without quotes
            logical_form_smt_fnode=view,  # Store the original FNode
            logical_form_etr=smt_to_etr(view),  # Convert to ETR notation
            english_form=smt_to_english(view, ontology),  # Convert to natural English
        )
        reified_views.append(reified_view)

    # Create ReifiedViews for conclusions if they exist
    yes_no_conclusions = []
    if smt_problem.yes_or_no_conclusions:
        for conclusion_fnode, is_correct in smt_problem.yes_or_no_conclusions:
            reified_conclusion = ReifiedView(
                logical_form_smt=format_smt(conclusion_fnode),
                logical_form_smt_fnode=conclusion_fnode,
                logical_form_etr=smt_to_etr(conclusion_fnode),
                english_form=smt_to_english(conclusion_fnode, ontology),
            )
            yes_no_conclusions.append((reified_conclusion, is_correct))

    # Set up multiple choice options from the yes/no conclusions
    multiple_choices = []
    if yes_no_conclusions:
        for conclusion, is_correct in yes_no_conclusions:
            # (view, is_correct, is_etr_predicted)
            multiple_choices.append((conclusion, is_correct, None))

    # Determine the ETR predicted conclusion
    etr_predicted_conclusion = get_etr_conclusion(views=reified_views)

    return FullProblem(
        introductory_prose=ontology.introduction,
        views=reified_views,
        # Yes/No section
        yes_or_no_conclusions=yes_no_conclusions if yes_no_conclusions else None,
        yes_or_no_question_prose="Does the following conclusion necessarily follow from the given statements?",
        # Multiple choice section
        multiple_choices=multiple_choices if multiple_choices else None,
        multiple_choice_question_prose="Which of the following conclusions necessarily follows from the given statements?",
        # Open ended question
        open_ended_question_prose="What if anything follows?",
        etr_predicted_conclusion=etr_predicted_conclusion,
    )
