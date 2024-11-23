from etr_case_generator.generator import ETRCaseGenerator
from etr_case_generator.reasoning_problem import ReasoningProblem
from etr_case_generator.ontology import ELEMENTS

from pyetr import View, State, SetOfStates
from pyetr.inference import (
    default_inference_procedure,
    default_procedure_does_it_follow,
)

r = ReasoningProblem(generator=ETRCaseGenerator(ELEMENTS))
r.update_premises(premises=[View.from_str("Ax {C(x)}")])

r.update_query(query=View.from_str("{C(B())}"))

print(r.full_prose())
