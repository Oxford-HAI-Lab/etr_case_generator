from dataclasses import dataclass


@dataclass
class ReifiedView:
    logical_form: str
    english_form: str
    mapping: dict[str, str]  # logical_form -> english_form, this must be bijective


@dataclass
class FullProblem:
    views: list[ReifiedView]

    # Yes or No format
    yes_or_no_conclusion: ReifiedView
    yes_or_no_answer: bool
    yes_or_no_question_prose: str

    # Multiple Choice
    multiple_choices: list[tuple[ReifiedView, bool, bool]]  # (view, is_correct, is_etr_predicted)
    multiple_choice_question_prose: str

    # Open Ended
    etr_predicted_conclusion: ReifiedView
    open_ended_question_prose: str

    # Details for printing
    introductory_prose: str
