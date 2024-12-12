from dataclasses import dataclass
from typing import Optional

from pysmt.fnode import FNode
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


def format_smt(fnode: FNode) -> str:
    """Format SMT formula without single quotes around symbols and with proper quantifier symbols"""
    # First remove quotes
    formatted = str(fnode).replace("'", "")
    # Replace quantifier text with symbols
    formatted = formatted.replace("exists", "∃")
    formatted = formatted.replace("forall", "∀")
    return formatted
from rich.panel import Panel
from rich.text import Text

from etr_case_generator.smt_generator import SMTProblem


@dataclass(kw_only=True)
class ReifiedView:
    logical_form_smt: Optional[str] = None
    logical_form_smt_fnode: Optional[FNode] = None
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
            content.append(Text("Views:", style="bold blue"))
            if self.views:
                for i, view in enumerate(self.views, 1):
                    content.append(f"  {i}. SMT: {view.logical_form_smt}")
                    content.append(f"     ETR: {view.logical_form_etr}")
                    content.append(f"     ENG: {view.english_form}")
            else:
                content.append("  None")
            content.append("")
        
        # Add yes/no section
        if show_empty or any([self.yes_or_no_conclusion, self.yes_or_no_answer is not None, self.yes_or_no_question_prose]):
            content.append(Text("Yes/No Question:", style="bold magenta"))
            content.append(f"  Question: {self.yes_or_no_question_prose}")
            if self.yes_or_no_conclusion:
                content.append(f"  Conclusion: {self.yes_or_no_conclusion.logical_form_smt}")
            content.append(f"  Answer: {self.yes_or_no_answer}")
            content.append("")
        
        # Add multiple choice section
        if show_empty or self.multiple_choices or self.multiple_choice_question_prose:
            content.append(Text("Multiple Choice:", style="bold yellow"))
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
            content.append(Text("Open Ended:", style="bold cyan"))
            content.append(f"  Question: {self.open_ended_question_prose}")
            if self.etr_predicted_conclusion:
                content.append(f"  Predicted: {self.etr_predicted_conclusion.logical_form_smt}")
            content.append("")
        
        # Create panel with all content
        panel = Panel("\n".join(str(line) for line in content), 
                     title="Reasoning Problem",
                     border_style="bright_blue")
        
        # Render to string
        with console.capture() as capture:
            console.print(panel)
        
        return capture.get()

    def __str__(self) -> str:
        return self.full_string(show_empty=False)


def full_problem_from_smt_problem(smt_problem: SMTProblem) -> FullProblem:
    """Convert an SMTProblem to a FullProblem, filling only the basic SMT views."""
    
    # Convert each FNode view to a ReifiedView
    reified_views = []
    for view in smt_problem.views:
        reified_view = ReifiedView(
            logical_form_smt=format_smt(view),  # Formatted string representation without quotes
            logical_form_smt_fnode=view,  # Store the original FNode
        )
        reified_views.append(reified_view)
    
    return FullProblem(views=reified_views)
