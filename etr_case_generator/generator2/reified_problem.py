from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class ReifiedView:
    logical_form_z3: Optional[str] = None
    logical_form_etr: Optional[str] = None
    english_form: Optional[str] = None
    mapping: Optional[dict[str, str]] = None  # logical_form -> english_form, this must be bijective


@dataclass(kw_only=True)
class FullProblem:
    views: Optional[list[ReifiedView]] = None

    # Yes or No format
    yes_or_no_conclusion: Optional[ReifiedView] = None
    yes_or_no_answer: Optional[bool] = None
    yes_or_no_question_prose: Optional[str] = None

    # Multiple Choice
    multiple_choices: Optional[list[tuple[ReifiedView, bool, bool]]] = None  # (view, is_correct, is_etr_predicted)
    multiple_choice_question_prose: Optional[str] = None

    # Open Ended
    etr_predicted_conclusion: Optional[ReifiedView] = None
    open_ended_question_prose: Optional[str] = None

    # Details for printing
    introductory_prose: Optional[str] = None
