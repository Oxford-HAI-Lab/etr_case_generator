from dataclasses import dataclass
from typing import Optional

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

    # Yes or No format
    yes_or_no_conclusions: Optional[list[tuple[ReifiedView, bool]]] = None  # List of (conclusion, is_correct) pairs
    yes_or_no_question_prose: Optional[str] = None

    # Multiple Choice
    multiple_choices: Optional[list[tuple[ReifiedView, bool, bool]]] = None  # (view, is_correct, is_etr_predicted)
    multiple_choice_question_prose: Optional[str] = None

    # Open Ended
    etr_predicted_conclusion: Optional[ReifiedView] = None
    open_ended_question_prose: Optional[str] = None

    # Details for printing
    introductory_prose: Optional[str] = None
    mapping: Optional[dict[str, str]] = None  # logical_form -> english_form, this must be bijective

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
        if show_empty or any([self.yes_or_no_conclusions, self.yes_or_no_question_prose]):
            content.append(Text("Yes/No Questions:", style="bold green"))
            content.append(f"  Question: {self.yes_or_no_question_prose}")
            if self.yes_or_no_conclusions:
                for i, (conclusion, is_correct) in enumerate(self.yes_or_no_conclusions, 1):
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
        
        return capture.get()

    def __str__(self) -> str:
        return self.full_string(show_empty=False)


