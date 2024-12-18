import textwrap
from dataclasses import dataclass
from typing import Optional, Literal

from pysmt.fnode import FNode
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text


@dataclass(kw_only=True)
class ReifiedView:
    logical_form_smt: Optional[str] = None
    logical_form_smt_fnode: Optional[FNode] = None
    logical_form_etr: Optional[str] = None
    english_form: Optional[str] = None


@dataclass(kw_only=True)
class FullProblem:
    views: Optional[list[ReifiedView]] = None
    possible_conclusions: Optional[list[tuple[ReifiedView, bool]]] = None  # List of (conclusion, is_correct) pairs

    # Yes or No format
    yes_or_no_conclusion_chosen_index: int = 0  # Indexes into possible_conclusions
    yes_or_no_question_prose: Optional[str] = "Does the following conclusion necessarily follow from the given statements?"
    yes_or_no_answer_guidance_prose: Optional[str] = 'Answer in the form of "Answer: Yes" or "Answer: No".'

    # Multiple Choice
    multiple_choices: Optional[list[tuple[ReifiedView, bool, bool]]] = None  # (view, is_correct, is_etr_predicted)
    multiple_choice_question_prose: Optional[str] = "Which of the following conclusions necessarily follows from the given statements?"
    multiple_choice_answer_guidance_prose: Optional[str] = 'Answer in the form of "Answer: A", "Answer: B", etc.'
    multiple_choice_options: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    # Open Ended
    etr_predicted_conclusion: Optional[ReifiedView] = None
    open_ended_question_prose: Optional[str] = "What if anything follows?"
    open_ended_answer_guidance_prose: Optional[str] = 'Answer in the format that I showed you.'
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

    def to_prompt(self, format: Literal["yes_no", "multiple_choice", "open_ended"] = "yes_no", chain_of_thought: bool = False) -> str:
        s = self.introductory_prose
        s += "\n\n"
        for view in self.views:
            s += f"* {view.english_form}"
            if format == "open_ended" and view.logical_form_etr:
                s += f"\n  Or, here it is in the format that PySMT uses: {view.logical_form_smt}"
            s += "\n"
        s += "\n"
        if format == "yes_no":
            s += self.yes_or_no_question_prose
            s += "\n\n"
            s += f"My Conclusion: {self.possible_conclusions[self.yes_or_no_conclusion_chosen_index][0].english_form}"
            s += "\n\n"
            s += self.yes_or_no_answer_guidance_prose
        elif format == "multiple_choice":
            s += self.multiple_choice_question_prose
            s += "\n\n"
            for i, (view, is_correct, is_etr_predicted) in enumerate(self.multiple_choices):
                s += f"{self.multiple_choice_options[i]}. {view.english_form}\n"
            s += "\n"
            s += self.multiple_choice_answer_guidance_prose
        elif format == "open_ended":
            s += self.open_ended_question_prose
            s += "\n\n"
            s += self.open_ended_answer_guidance_prose
        s += "\n\n"
        if chain_of_thought:
            s += self.chain_of_thought_prose
        else:
            s += self.answer_immediately_prose
        return s

    def full_string(self, show_empty: bool = False) -> str:
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
                for i, (conclusion, is_correct) in enumerate(self.possible_conclusions, 1):
                    content.append(f"  {i}. Conclusion: {conclusion.logical_form_smt}")
                    content.append(f"     Answer: {is_correct}")
            content.append("")
        
        # Add multiple choice section
        if show_empty or self.multiple_choices or self.multiple_choice_question_prose:
            content.append(Text("Multiple Choice:", style="bold green"))
            content.append(f"  Question: {self.multiple_choice_question_prose}")
            if self.multiple_choices:
                for i, (view, is_correct, is_predicted) in enumerate(self.multiple_choices, 1):
                    content.append(f"  {i}. {view.logical_form_smt}")
                    content.append(f"     Correct: {is_correct}, Predicted: {is_predicted}")
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

            for prompt_type in ["yes_no", "multiple_choice", "open_ended"]:
                prompt_panel = Panel(
                    Group(Text(f"{self.to_prompt(prompt_type)}")),
                    title=f"{prompt_type.capitalize()} Prompt",
                    border_style="bright_blue"
                )
                console.print(prompt_panel)
        
        return capture.get()

    def __str__(self) -> str:
        return self.full_string(show_empty=False)


