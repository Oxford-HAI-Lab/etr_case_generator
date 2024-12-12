from dataclasses import dataclass
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from etr_case_generator.smt_generator import SMTProblem


@dataclass(kw_only=True)
class ReifiedView:
    logical_form_smt: Optional[str] = None
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

    def __str__(self) -> str:
        console = Console(record=True)
        
        # Create the main content
        content = []
        
        # Add introductory prose if present
        if self.introductory_prose:
            content.append(Text(self.introductory_prose, style="bold green"))
            content.append("")
        
        # Add views
        if self.views:
            content.append(Text("Views:", style="bold blue"))
            for i, view in enumerate(self.views, 1):
                if view.logical_form_smt:
                    content.append(f"  {i}. SMT: {view.logical_form_smt}")
                if view.logical_form_etr:
                    content.append(f"     ETR: {view.logical_form_etr}")
                if view.english_form:
                    content.append(f"     ENG: {view.english_form}")
                content.append("")
        
        # Add yes/no section if present
        if self.yes_or_no_conclusion:
            content.append(Text("Yes/No Question:", style="bold magenta"))
            if self.yes_or_no_question_prose:
                content.append(f"  Question: {self.yes_or_no_question_prose}")
            content.append(f"  Conclusion: {self.yes_or_no_conclusion.logical_form_smt}")
            if self.yes_or_no_answer is not None:
                content.append(f"  Answer: {self.yes_or_no_answer}")
            content.append("")
        
        # Add multiple choice section if present
        if self.multiple_choices:
            content.append(Text("Multiple Choice:", style="bold yellow"))
            if self.multiple_choice_question_prose:
                content.append(f"  Question: {self.multiple_choice_question_prose}")
            for i, (view, is_correct, is_predicted) in enumerate(self.multiple_choices, 1):
                content.append(f"  {i}. {view.logical_form_smt}")
                content.append(f"     Correct: {is_correct}, Predicted: {is_predicted}")
            content.append("")
        
        # Add open ended section if present
        if self.etr_predicted_conclusion or self.open_ended_question_prose:
            content.append(Text("Open Ended:", style="bold cyan"))
            if self.open_ended_question_prose:
                content.append(f"  Question: {self.open_ended_question_prose}")
            if self.etr_predicted_conclusion:
                content.append(f"  Predicted: {self.etr_predicted_conclusion.logical_form_smt}")
        
        # Create panel with all content
        panel = Panel("\n".join(str(line) for line in content), 
                     title="Reasoning Problem",
                     border_style="bright_blue")
        
        # Render to string
        with console.capture() as capture:
            console.print(panel)
        
        return capture.get()


def full_problem_from_smt_problem(smt_problem: SMTProblem) -> FullProblem:
    """Convert an SMTProblem to a FullProblem, filling only the basic SMT views."""
    
    # Convert each FNode view to a ReifiedView
    reified_views = []
    for view in smt_problem.views:
        reified_view = ReifiedView(
            logical_form_smt=str(view),  # Basic string representation of FNode
            logical_form_etr=None,  # Leave ETR form empty for now
        )
        reified_views.append(reified_view)
    
    return FullProblem(views=reified_views)
