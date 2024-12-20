import textwrap
from dataclasses import dataclass
from typing import Optional, Literal, cast, get_args

from pyetr import View
from pysmt.fnode import FNode
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text

from etr_case_generator import Ontology
from etr_case_generator.generator2.formatting_smt import format_smt, smt_to_etr, smt_to_english, load_fnode_from_string
from smt_interface.smt_encoder import view_to_smt

# Different ways of asking a question
QuestionType = Literal["yes_no", "multiple_choice", "open_ended"]


@dataclass(kw_only=True)
class ReifiedView:
    logical_form_smt: Optional[str] = None
    logical_form_smt_fnode: Optional[FNode] = None
    logical_form_etr: Optional[str] = None
    english_form: Optional[str] = None

    def fill_out(self, ontology: Optional[Ontology] = None):
        if self.logical_form_etr is not None:
            view: View = View.from_str(self.logical_form_etr)
            # Consider using `view_to_smt` to go from ETR->SMT
            if self.logical_form_smt_fnode is None:
                self.logical_form_smt_fnode = view_to_smt(view)
            if self.logical_form_smt is None:
                self.logical_form_smt = format_smt(self.logical_form_smt_fnode)
        elif self.logical_form_smt_fnode is not None:
            if self.logical_form_smt is None:
                self.logical_form_smt = format_smt(self.logical_form_smt_fnode)
            if self.logical_form_etr is None:
                self.logical_form_etr = smt_to_etr(self.logical_form_smt_fnode)
        elif self.logical_form_smt_fnode is None:
                # This is not implemented
                self.logical_form_smt_fnode = load_fnode_from_string(self.logical_form_smt)

        assert self.logical_form_smt_fnode is not None

        if self.english_form is None and ontology is not None:
            # Consider using view_to_natural_language, to go from ETR->ENG
            self.english_form = smt_to_english(self.logical_form_smt_fnode, ontology)

        assert self.logical_form_smt is not None and self.logical_form_etr is not None and self.english_form is not None, "Error filling out ReifiedView. Make sure it has either an smt or etr form. It cannot be filled out from the english form."


@dataclass(kw_only=True)
class Conclusion:
    # This class only makes sense when held by a Problem object
    view: ReifiedView
    is_classically_correct: Optional[bool] = None

    # Result of default_procedure_does_it_follow function
    is_etr_predicted: Optional[bool] = None


@dataclass(kw_only=True)
class PartialProblem:
    premises: Optional[list[ReifiedView]] = None

    # There should be exactly one option which is classically correct
    possible_conclusions_from_logical: Optional[list[Conclusion]] = None

    # There should be exactly one option which is ETR-predicted
    possible_conclusions_from_etr: Optional[list[Conclusion]] = None

    # The result of the default_inference_procedure
    etr_what_follows: Optional[ReifiedView] = None

    def fill_out(self, ontology: Optional[Ontology] = None):
        if self.premises is not None:
            for premise in self.premises:
                premise.fill_out(ontology)
        if self.possible_conclusions_from_logical is not None:
            for conclusion in self.possible_conclusions_from_logical:
                conclusion.view.fill_out(ontology)
        if self.possible_conclusions_from_etr is not None:
            for conclusion in self.possible_conclusions_from_etr:
                conclusion.view.fill_out(ontology)
        if self.etr_what_follows is not None:
            self.etr_what_follows.fill_out(ontology)

        # Note that this does NOT fill out the etr_what_follows view, or the is_etr_predicted field of the conclusions.


@dataclass(kw_only=True)
class FullProblem:
    views: Optional[list[ReifiedView]] = None
    possible_conclusions: Optional[list[Conclusion]] = None  # List of (conclusion, is_classically_correct) pairs

    # TODO(andrew) Think about how to handle the two types of conclusion from PartialProblem

    # Yes or No format
    yes_or_no_conclusion_chosen_index: int = 0  # Indexes into possible_conclusions
    yes_or_no_question_prose: Optional[str] = "Does the following conclusion necessarily follow from the given statements?"
    yes_or_no_answer_guidance_prose: Optional[str] = 'Does it follow? Answer in the form of "Answer: Yes" or "Answer: No".'

    # Multiple Choice
    multiple_choices: Optional[list[Conclusion]] = None  # (view, is_correct, is_etr_predicted)
    multiple_choice_question_prose: Optional[str] = "Which of the following conclusions necessarily follows from the given statements?"
    multiple_choice_answer_guidance_prose: Optional[str] = 'Which one follows? Answer in the form of "Answer: A", "Answer: B", etc.'
    multiple_choice_options: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    # Open Ended
    etr_predicted_conclusion: Optional[ReifiedView] = None
    open_ended_question_prose: Optional[str] = "What if anything follows?"
    open_ended_answer_guidance_prose: Optional[str] = 'What follows? Answer in the format that I showed you. Write "Answer: {logical statement}".'
    open_ended_formatting_advice = textwrap.dedent("""
        For the purpose of this question, I want you to write your answer in the format of a logical statement. Here are the rules for how you should format it:
        - You can write a predicate like "f()"
        - If the predicate has arguments, you can write them like "f(x)"
        - You can do negation with "~", like "~f(x)" to mean "not f(x)"
        - You can represent "and" by writing multiple predicates without a separator, like "f(x)g(x)"
        - You can represent "or" by writing multiple predicates with a "," between them, like "f(x),g(x)"
        - You can use the "∀" to represent "for all", like "∀x f(x)"
        - You can use the "∃" to represent "there exists", like "∃x f(x)"
        - Wrap a statement in curly braces, like "{f(x)g(x)}", or "∀x {f(x)g(x)}", if there's a quantifier
        """).strip()  # TODO Add more rules here

    # Boilerplate for the question
    introductory_prose: Optional[str] = None
    answer_immediately_prose: Optional[str] = "I want you to answer immediately."
    chain_of_thought_prose: Optional[str] = "I want you to spend a few paragraphs thinking about your answer."

    def to_prompt(self, format: QuestionType = "yes_no", chain_of_thought: bool = False) -> str:
        s = self.introductory_prose
        s += "\n\n"
        for view in self.views:
            s += f"* {view.english_form}"
            if format == "open_ended" and view.logical_form_etr:
                s += f"\n  Eq: `{view.logical_form_etr}`"
            s += "\n"
        s += "\n"
        if format == "yes_no":
            s += self.yes_or_no_question_prose
            s += "\n\n"
            s += f"My Conclusion: {self.possible_conclusions[self.yes_or_no_conclusion_chosen_index].view.english_form}"
        elif format == "multiple_choice":
            s += self.multiple_choice_question_prose
            s += "\n\n"
            for i, conclusion in enumerate(self.multiple_choices):
                s += f"{self.multiple_choice_options[i]}. {conclusion.view.english_form}\n"
            s = s[:-1]  # Remove the last "\n"
        elif format == "open_ended":
            s += self.open_ended_formatting_advice
            s += "\n\n"
            s += self.open_ended_question_prose
        s += "\n\n"
        if chain_of_thought:
            s += self.chain_of_thought_prose
        else:
            s += self.answer_immediately_prose
        s += "\n\n"
        if format == "yes_no":
            s += self.yes_or_no_answer_guidance_prose
        elif format == "multiple_choice":
            s += self.multiple_choice_answer_guidance_prose
        elif format == "open_ended":
            s += self.open_ended_answer_guidance_prose
        return s

    def to_answer(self, format: QuestionType = "yes_no") -> str:
        if format == "yes_no":
            return f"{'Yes' if self.possible_conclusions[self.yes_or_no_conclusion_chosen_index].is_classically_correct else 'No'}"
        elif format == "multiple_choice":
            correct_index: int = -1
            for i, conclusion in enumerate(self.multiple_choices):
                if conclusion.is_classically_correct:
                    correct_index = i
                    break
            if correct_index == -1:
                raise ValueError("No correct answer found in multiple_choices")
            return f"{self.multiple_choice_options[correct_index]}"
        elif format == "open_ended":
            return f"{self.etr_predicted_conclusion.logical_form_etr}"

    def to_dict_for_jsonl(self, args, format: QuestionType = "yes_no", chain_of_thought: bool = False) -> dict:
        dict = {
            "question": self.to_prompt(format, chain_of_thought),
            "scoring_guide": {
                "answer": self.to_answer(format),
                "etr_predicted": self.etr_predicted_conclusion.logical_form_etr if self.etr_predicted_conclusion else None,
                "etr_predicted_is_classically_correct": "UNKNOWN",
            },
            "generation_details": {
                # TODO: Also include data like how many atoms or clauses were used in the views
                "atoms_distributed_over_views": args.num_pieces,
                "num_predicates_per_problem": args.num_predicates_per_problem,
                "num_objects_per_problem": args.num_objects_per_problem,
            }
        }
        if format == "multiple_choice":
            dict["scoring_guide"]["options"] = [
                (conclusion.view.english_form if conclusion.view.english_form else conclusion.view.logical_form_etr, conclusion.is_classically_correct) for conclusion in self.multiple_choices
            ]
        return dict


    def full_string(self, question_types: list[str] = get_args(QuestionType), show_empty: bool = False) -> str:
        console = Console(record=True)
        
        # Create the main content
        content = []
        
        # Add introductory prose
        if show_empty or self.introductory_prose:
            content.append(Text("Introductory Prose:", style="bold green"))
            content.append(f"  {self.introductory_prose}")
            content.append("")
        
        # Add views
        if show_empty or self.views:
            content.append(Text("Views:", style="bold green"))
            if self.views:
                for i, view in enumerate(self.views, 1):
                    content.append(f"  {i}. SMT: {view.logical_form_smt}")
                    if view.logical_form_etr or show_empty:
                        content.append(f"     ETR: {view.logical_form_etr}")
                    if view.english_form or show_empty:
                        content.append(f"     Eng: {view.english_form}")
                    content.append("")
            else:
                content.append("  None")
            content.append("")
        
        # Add yes/no section
        if show_empty or any([self.possible_conclusions, self.yes_or_no_question_prose]):
            content.append(Text("Yes/No Questions:", style="bold green"))
            content.append(f"  Question: {self.yes_or_no_question_prose}")
            if self.possible_conclusions:
                for i, conclusion in enumerate(self.possible_conclusions, 1):
                    content.append(f"  {i}. Conclusion: {conclusion.view.logical_form_smt}")
                    content.append(f"     Answer: {conclusion.is_classically_correct}")
            content.append("")
        
        # Add multiple choice section
        if show_empty or self.multiple_choices or self.multiple_choice_question_prose:
            content.append(Text("Multiple Choice:", style="bold green"))
            content.append(f"  Question: {self.multiple_choice_question_prose}")
            if self.multiple_choices:
                for i, conclusion in enumerate(self.multiple_choices, 1):
                    content.append(f"  {i}. {conclusion.view.logical_form_smt}")
                    content.append(f"     Correct: {conclusion.is_classically_correct}, Predicted: {conclusion.is_etr_predicted}")
            else:
                content.append("  No choices available")
            content.append("")
        
        # Add open ended section
        if show_empty or self.etr_predicted_conclusion or self.open_ended_question_prose:
            content.append(Text("Open Ended:", style="bold green"))
            content.append(f"  Question: {self.open_ended_question_prose}")
            if show_empty or self.etr_predicted_conclusion:
                content.append(f"  Predicted: {self.etr_predicted_conclusion if self.etr_predicted_conclusion else None}")
            content.append("")
        
        # Create panel with all content
        panel = Panel(
            Group(*content),  # Use Group to preserve formatting of each line
            title="Reasoning Problem",
            border_style="bright_blue"
        )
        
        # Render to string
        with console.capture() as capture:
            console.print(panel)

            for prompt_type in question_types:
                prompt_type = cast(QuestionType, prompt_type)
                prompt_panel = Panel(
                    Group(Text(f"{self.to_prompt(prompt_type)}")),
                    title=f"{prompt_type.capitalize()} Prompt",
                    border_style="bright_blue"
                )
                console.print(prompt_panel)

                answer_panel = Panel(
                    Group(Text(f"{self.to_answer(prompt_type)}")),
                    title=f"{prompt_type.capitalize()} Answer",
                    border_style="bright_blue"
                )
                console.print(answer_panel)
        
        return capture.get()

    def __str__(self) -> str:
        return self.full_string(show_empty=False)


