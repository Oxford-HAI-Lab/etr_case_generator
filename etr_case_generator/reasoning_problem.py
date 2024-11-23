from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json


@dataclass_json
@dataclass
class ReasoningProblem:
    premises: list[tuple[str, str]]

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
