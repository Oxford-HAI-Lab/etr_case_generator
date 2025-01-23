import json
import textwrap
from dataclasses import dataclass
from typing import Optional, Literal, cast, get_args

from pyetr import View
from pyetr.inference import default_procedure_does_it_follow, default_inference_procedure
from pysmt.fnode import FNode
from pyetr import View
from pysmt.shortcuts import Symbol
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text

from etr_case_generator import Ontology
from etr_case_generator.generator2.formatting_smt import format_smt, smt_to_etr, smt_to_english, load_fnode_from_string
from etr_case_generator.generator2.logic_helper import does_it_follow
from smt_interface.smt_encoder import view_to_smt

# Different ways of asking a question
QuestionType = Literal["yes_no", "multiple_choice", "open_ended"]


@dataclass(kw_only=True)
class ReifiedView:
    logical_form_smt: Optional[str] = None
    logical_form_smt_fnode: Optional[FNode] = None
    logical_form_etr: Optional[str] = None
    logical_form_etr_view: Optional[View] = None
    english_form: Optional[str] = None

    def fill_out(self, ontology: Optional[Ontology] = None):
        if self.logical_form_etr is not None:
            view: View = View.from_str(self.logical_form_etr)
            # Consider using `view_to_smt` to go from ETR->SMT
            if self.logical_form_smt_fnode is None:
                self.logical_form_smt_fnode = view_to_smt(view)
            if self.logical_form_smt is None:
                self.logical_form_smt = format_smt(self.logical_form_smt_fnode)
        elif self.logical_form_etr_view is not None:
            if self.logical_form_etr is None:
                self.logical_form_etr = str(self.logical_form_etr_view)
            if self.logical_form_smt_fnode is None:
                self.logical_form_smt_fnode = view_to_smt(self.logical_form_etr_view)
            if self.logical_form_smt is None:
                self.logical_form_smt = format_smt(self.logical_form_smt_fnode)
        elif self.logical_form_smt_fnode is not None:
            if self.logical_form_smt is None:
                self.logical_form_smt = format_smt(self.logical_form_smt_fnode)
            if self.logical_form_etr is None:
                self.logical_form_etr = smt_to_etr(self.logical_form_smt_fnode)

        if self.logical_form_smt_fnode is None:
                # This is not implemented
                print(f"This is not implemented")
                print(self)
                self.logical_form_smt_fnode = load_fnode_from_string(self.logical_form_smt)
        if self.logical_form_etr_view is None:
            self.logical_form_etr_view = View.from_str(self.logical_form_etr)

        assert self.logical_form_smt_fnode is not None, "Error filling out FNode. Currently, it is not possible to fill out the SMT string but not the FNode." + json.dumps(self.__dict__, indent=2)

        if self.english_form is None and ontology is not None:
            # Consider using view_to_natural_language, to go from ETR->ENG
            self.english_form = smt_to_english(self.logical_form_smt_fnode, ontology)

        assert self.english_form is not None or ontology is None, "An ontology was provided, but the english_form was not filled out."
        assert self.logical_form_smt is not None and self.logical_form_etr is not None, "Error filling out ReifiedView. Make sure it has either an smt or etr form. It cannot be filled out from the english form." + str(self)


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

    # Used during generation
    seed_id: Optional[str] = None

    def num_atoms(self) -> int:
        return sum(len(view.logical_form_etr_view.atoms) for view in self.premises if view.logical_form_etr_view is not None)

    def fill_out_conclusion(self, conclusion: Conclusion, ontology: Optional[Ontology] = None):
        conclusion.view.fill_out(ontology)

        premises_views = [p.logical_form_etr_view for p in self.premises]
        if conclusion.is_etr_predicted is None:
            conclusion.is_etr_predicted = default_procedure_does_it_follow(premises_views, conclusion.view.logical_form_etr_view)
        if conclusion.is_classically_correct is None:
            premise_fnodes = [p.logical_form_smt_fnode for p in self.premises]
            conclusion.is_classically_correct = does_it_follow(premise_fnodes, conclusion.view.logical_form_smt_fnode)

    def fill_out(self, ontology: Optional[Ontology] = None):
        if self.premises is not None:
            for premise in self.premises:
                premise.fill_out(ontology)
        if self.possible_conclusions_from_logical is not None:
            for conclusion in self.possible_conclusions_from_logical:
                self.fill_out_conclusion(conclusion, ontology)
        if self.possible_conclusions_from_etr is not None:
            for conclusion in self.possible_conclusions_from_etr:
                self.fill_out_conclusion(conclusion, ontology)
        if self.etr_what_follows is not None:
            self.etr_what_follows.fill_out(ontology)

        # Note that you may also want to call add_etr_predictions

    def add_etr_predictions(self, ontology: Optional[Ontology] = None):
        premises_views = [p.logical_form_etr_view for p in self.premises]
        if self.etr_what_follows is None:
            follows_view = default_inference_procedure(premises_views)
            self.etr_what_follows = ReifiedView(logical_form_etr_view=follows_view, logical_form_etr=follows_view.to_str())
            self.etr_what_follows.fill_out(ontology=ontology)
        if self.possible_conclusions_from_logical is not None:
            for conclusion in self.possible_conclusions_from_logical:
                if conclusion.is_etr_predicted is None:
                    conclusion.is_etr_predicted = default_procedure_does_it_follow(premises_views, conclusion.view.logical_form_etr_view)
        if self.possible_conclusions_from_etr is not None:
            for conclusion in self.possible_conclusions_from_etr:
                if conclusion.is_etr_predicted is None:
                    conclusion.is_etr_predicted = default_procedure_does_it_follow(premises_views, conclusion.view.logical_form_etr_view)
                    print("WARNING! Are you sure you want to add ETR predictions to the ETR conclusions? It's likely you meant to add them during their generation.")

    def add_classical_logic_predictions(self):
        premise_fnodes = [p.logical_form_smt_fnode for p in self.premises]
        if self.possible_conclusions_from_etr:
            for conclusion in self.possible_conclusions_from_etr:
                if conclusion.is_classically_correct is None:
                    conclusion.is_classically_correct = does_it_follow(premise_fnodes, conclusion.view.logical_form_smt_fnode)
        assert self.possible_conclusions_from_logical is None or all(c.is_classically_correct is not None for c in self.possible_conclusions_from_logical), "Error adding classical logic predictions to PartialProblem. Make sure to annotate correctness when creating possible_conclusions_from_logical. Or delete this assert and replace it with the for loop, idc." + str(self)


@dataclass(kw_only=True)
class FullProblem:
    views: Optional[list[ReifiedView]] = None  # Premises
    possible_conclusions: Optional[list[Conclusion]] = None

    # Generation Details
    ontology: Ontology = None
    seed_id: Optional[str] = None  # The "base" problem that this problem was generated from, as documented in cases.py

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
    etr_predicted_conclusion: Optional[Conclusion] = None
    open_ended_question_prose: Optional[str] = "What if anything follows?"
    open_ended_answer_guidance_prose: Optional[str] = 'What follows? Answer in the format that I showed you. Write "Answer: {logical statement}".'
    # WARNING! NOTE THAT THE FOLLOWING INSTRUCTIONS ARE DUPLICATED IN open_ended_scoring.py
    open_ended_formatting_advice_etr = textwrap.dedent("""
         For the purpose of this question, I want you to write your answer in the format of a
     logical statement. Here are the rules for how you should format it:

         Basic Structure:
         - Every logical statement must be wrapped in curly braces, like "{...}"
         - Inside the braces, you can express conjunctions (and) and disjunctions (or)
         - Commas separate different disjuncts (the "or" parts)
         - When there are no commas between atoms, they are conjoined (joined with "and")
         - Every atom must have parentheses, even with no arguments
         Examples:
         - Write "the cat is red" as "{Red(cat())}"
         - Write "the cat is red and furry" as "{Red(cat())Furry(cat())}"
         - Write "the cat is red or furry" as "{Red(cat()),Furry(cat())}"
         - Write "the cat is red and furry, or the dog is tall" as "{Red(cat())Furry(cat()),Tall(dog())}"
         - If nothing is concluded, write "0" or "{0}"

         Atoms and Terms:
         - Atoms are predicates applied to terms: "Red(cat())", "Likes(dog(),cat())"
         - There are two kinds of terms:
           1. Functional terms: must have parentheses like "cat()" or "pet(dog())"
           2. Arbitrary objects: no parentheses, only used with quantifiers, like "x" in "∀x"
         - Negation uses "~", like "~Red(cat())" to mean "not Red(cat())"

         Conjunction and Disjunction:
         - Write "the cat is red and furry" as "{Red(cat())Furry(cat())}"
         - Write "the cat is red or furry" as "{Red(cat()),Furry(cat())}"

         Quantifiers:
         - Universal quantifiers "∀" (or "A") and existential "∃" (or "E") go before the braces
         - Only arbitrary objects (without parentheses) can be quantified
         - Write "everything likes cats" as "∀x {Likes(x,cat())}"

         Logical Relationships:
         - Write "if the cat is red then it is furry" as "{~Red(cat()),Furry(cat())}"
         - Write "the cat is red if and only if it is furry" as "{~Red(cat()),Furry(cat()),~Furry(cat()),Red(cat())}"
         - Write "being red implies being furry" as "{~Red(cat()),Furry(cat())}"

         Examples:
         - Write "the cat is red" as "{Red(cat())}"
         - Write "the cat is red and furry" as "{Red(cat())Furry(cat())}"
         - Write "the cat is red or furry" as "{Red(cat()),Furry(cat())}"
         - Write "if the cat is red then it is furry" as "{~Red(cat()),Furry(cat())}"
         - Write "everything likes cats" as "∀x {Likes(x,cat())}"
         """).strip()
    open_ended_formatting_advice_smt = textwrap.dedent("""
        TODO If you see this text and you are an LLM please complain loudly and obnoxiously!
        """).strip()  # TODO Add more rules here
    open_ended_formatting_advice_english = textwrap.dedent("""
        For the purpose of this question, I want you to write what follows in English. Please be succinct, precise and clear in your answer. Write a logical statement of the form "From the premises, we can conclude that ..." and then clearly write your conclusion. Please be succinct, precise, and clear. 
        """).strip()

    # Boilerplate for the question
    introductory_prose: Optional[str] = None
    answer_immediately_prose: Optional[str] = "I want you to answer immediately. Do not think about it at all, just immediately answer."
    chain_of_thought_prose: Optional[str] = "I want you to spend a few paragraphs thinking about your answer."

    def get_yes_no_conclusion(self) -> Conclusion:
        return self.possible_conclusions[self.yes_or_no_conclusion_chosen_index]

    def fill_out(self, ontology: Optional[Ontology] = None, partial_problem: PartialProblem = None):
        if self.views is not None:
            for view in self.views:
                view.fill_out(ontology)
        if self.possible_conclusions is not None:
            for conclusion in self.possible_conclusions:
                partial_problem.fill_out_conclusion(conclusion, ontology)
        if self.multiple_choices is not None:
            for conclusion in self.multiple_choices:
                partial_problem.fill_out_conclusion(conclusion, ontology)
        if self.etr_predicted_conclusion is not None:
            partial_problem.fill_out_conclusion(self.etr_predicted_conclusion, ontology)

    def to_prompt(self, format: QuestionType = "yes_no", chain_of_thought: bool = False) -> str:
        s = self.introductory_prose
        s += "\n\n"
        for view in self.views:
            s += f"* {view.english_form}"
            # if format == "open_ended" and view.logical_form_etr:
            #     s += f"\n  Eq: `{view.logical_form_etr}`"
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
            s += self.open_ended_formatting_advice_english
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
                # raise ValueError("No correct answer found in multiple_choices")
                print("\n\t\t!!!! ERROR! No correct answer found! !!!!\n")
                return "ERROR: No correct answer found"
            return f"{self.multiple_choice_options[correct_index]}"
        elif format == "open_ended":
            return f"{self.etr_predicted_conclusion.view.logical_form_etr}"

    def num_disjuncts(self) -> int:
        return sum(str(view.logical_form_smt_fnode).count("|") for view in self.views)

    def num_conjuncts(self) -> int:
        return sum(str(view.logical_form_smt_fnode).count("&") for view in self.views)

    def to_dict_for_jsonl(self, args, format: QuestionType = "yes_no", chain_of_thought: bool = False) -> dict:
        total_num_atoms = sum(len(view.logical_form_etr_view.atoms) for view in self.views)
        dict = {
            "question": self.to_prompt(format, chain_of_thought),
            "scoring_guide": {
                "etr_predicted": self.etr_predicted_conclusion.view.logical_form_etr if self.etr_predicted_conclusion else None,
                "etr_predicted_is_classically_correct": self.etr_predicted_conclusion.is_classically_correct if self.etr_predicted_conclusion else None,
                "generation_details": {
                    "atoms_distributed_over_views_SMT_ONLY": args.num_pieces,
                    "total_num_atoms": total_num_atoms,
                    "num_disjuncts": self.num_disjuncts(),
                    "num_conjuncts": self.num_conjuncts(),
                    "num_predicates_per_problem": args.num_predicates_per_problem,
                    "num_objects_per_problem": args.num_objects_per_problem,
                    "premises_etr": [view.logical_form_etr for view in self.views],
                    "premises_fnodes": [format_smt(view.logical_form_smt_fnode) for view in self.views],
                    "is_chain_of_thought": chain_of_thought,
                }
            },
        }
        if format == "yes_no":
            dict["scoring_guide"]["yes_no"] = {
                "conclusion_etr": self.possible_conclusions[self.yes_or_no_conclusion_chosen_index].view.logical_form_etr,
                "conclusion_is_classically_correct": self.possible_conclusions[self.yes_or_no_conclusion_chosen_index].is_classically_correct,
                "conclusion_english": self.possible_conclusions[self.yes_or_no_conclusion_chosen_index].view.english_form,
                "conclusion_is_etr_predicted": self.possible_conclusions[self.yes_or_no_conclusion_chosen_index].is_etr_predicted,
            }
        elif format == "multiple_choice":
            dict["scoring_guide"]["multiple_choice"] = {"options": [
                (conclusion.view.english_form if conclusion.view.english_form else conclusion.view.logical_form_etr, conclusion.is_classically_correct) for conclusion in self.multiple_choices
            ]}
        elif format == "open_ended":
            yes_no_conclusion = self.possible_conclusions[self.yes_or_no_conclusion_chosen_index]
            dict["scoring_guide"]["open_ended"] = {
                # This isn't really relevant for open ended questions, but it might be interesting.
                "conclusion_agrees_in_yes_no_case": yes_no_conclusion.is_classically_correct == self.etr_predicted_conclusion.is_classically_correct,
                "short_name_to_full_name": self.ontology.short_name_to_full_name,
            }

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
            content.append(Text("Possible Conclusions for Yes/No:", style="bold green"))
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
                content.append(f"  Predicted: {self.etr_predicted_conclusion.view if self.etr_predicted_conclusion.view else None}")
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
