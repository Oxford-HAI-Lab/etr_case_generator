from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json
from etr_case_generator.generator import ETRCaseGenerator
from pyetr import View
from pyetr.inference import default_inference_procedure
from typing import Optional


@dataclass
class Statement:
    view: View
    natural_language: str


class ReasoningProblem:
    def __init__(self, generator: ETRCaseGenerator):
        self._premises: list[Statement] = []
        self.etr_conclusion: Statement = Statement(
            view=View.get_verum(), natural_language=""
        )
        self.generator = generator
        self.obj_map: dict[str, str] = {}

    @property
    def premises(self):
        return self._premises

    @premises.setter
    def premises(self, value: list[Statement]):
        self._premises = value

        # Run ETR to get the ETR conclusion
        conclusion = default_inference_procedure([p.view for p in self._premises])
        self.etr_conclusion = Statement(
            view=conclusion,
            natural_language=self.generator.view_to_natural_language(
                conclusion, obj_map=self.obj_map
            ),
        )

    # premises: list[tuple[str, str]]

    # The actual question
    full_prose: str  # The premises and the question_conclusion
    question_conclusion: tuple[
        str, str
    ]  # Note: this is not necessarily the etr_conclusion

    # The ETR conclusion, which is not necessarily what's being asked about
    etr_conclusion: tuple[str, str]
    etr_conclusion_is_categorical: bool

    # Structured data which makes of the strings. Exclude them because Views aren't serializable.
    premise_views: list[View] = field(metadata=config(exclude=lambda x: True))
    etr_conclusion_view: View = field(metadata=config(exclude=lambda x: True))
    question_conclusion_view: View = field(metadata=config(exclude=lambda x: True))

    # Is the question conclusion ETR? Is it logically correct?
    question_conclusion_is_etr_conclusion: Optional[bool] = (
        None  # The conclusion has one state, no disjunction
    )
    classically_valid_conclusion: Optional[bool] = None

    # More information about the problem
    vocab_size: Optional[int] = None
    max_disjuncts: Optional[int] = None
    num_variables: Optional[int] = None
    num_disjuncts: Optional[int] = None
    num_premises: Optional[int] = None
