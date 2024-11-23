from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json
from etr_case_generator.generator import ETRCaseGenerator
from etr_case_generator.view_to_natural_language import view_to_natural_language
from pyetr import View
from pyetr.inference import (
    default_inference_procedure,
    default_procedure_does_it_follow,
)
from smt_interface.smt_encoder import check_validity
from typing import Optional


class ReasoningProblem:
    def __init__(self, generator: ETRCaseGenerator):
        self.premises: list[tuple[View, str]] = []
        self.etr_conclusion: tuple[View, str] = (View.get_verum(), "")

        self.etr_conclusion_is_categorical: bool = False
        self.etr_conclusion_is_logically_valid: Optional[bool] = (
            None  # TODO shouldn't be optional
        )

        self.generator = generator
        self.obj_map: dict[str, str] = {}

        self.query: tuple[View, str] = self.etr_conclusion
        self.etr_predicts_query_follows: bool = False
        self.query_is_logically_consistent: bool = False

    def update_premises(self, premises: list[View]):
        self.premises = []
        self.obj_map = {}
        for view in premises:
            nl, self.obj_map = view_to_natural_language(
                self.generator.ontology, view, self.obj_map
            )
            self.premises.append((view, nl))

        # Run ETR to get the ETR conclusion
        c_etr = default_inference_procedure([p[0] for p in self.premises])
        c_nl, self.obj_map = view_to_natural_language(
            self.generator.ontology, c_etr, obj_map=self.obj_map
        )
        self.etr_conclusion = (
            c_etr,
            c_nl,
        )

        self.etr_conclusion_is_categorical = (
            len(c_etr.stage) == 1
            and not c_etr.stage.is_verum
            and c_etr.supposition.is_verum
        )

        premise_views = [p[0] for p in self.premises]
        self.etr_predicts_query_follows = default_procedure_does_it_follow(
            premise_views, self.query[0]
        )
        self.etr_conclusion_is_logically_consistent = check_validity(
            premise_views, [self.etr_conclusion[0]]
        )

    def append_premise(self, premise: View):
        self.update_premises([p[0] for p in self.premises] + [premise])

    def update_query(self, query: View):
        self.query = (
            query,
            view_to_natural_language(self.generator.ontology, query, self.obj_map)[0],
        )

        premise_views = [p[0] for p in self.premises]

        self.etr_predicts_query_follows = default_procedure_does_it_follow(
            premise_views, self.query[0]
        )
        self.query_is_logically_consistent = check_validity(
            premise_views, [self.query[0]]
        )

    def full_prose(self) -> str:
        def punctuate(sentence: str) -> str:
            return sentence[0].upper() + sentence[1:] + "."

        full_prose = "Consider the following premises:\n\n"

        for i, (_, p_nl) in enumerate(self.premises):
            full_prose += f"{i + 1}. {punctuate(p_nl)}\n"

        full_prose += "\n"
        full_prose += f"Does it follow that {self.query[1]}?\n\n"
        full_prose += "Answer using 'YES' or 'NO' ONLY."

        return full_prose
