from pyetr import View
from pyetr.inference import default_inference_procedure

from etr_case_generator.generator2.reified_problem import FullProblem, ReifiedView


def get_etr_conclusion(views: list[ReifiedView]) -> ReifiedView:
    view_strings = [view.logical_form_etr for view in views]
    view_objects = [View.from_str(view_string) for view_string in view_strings]
    etr_predicted_conclusion = default_inference_procedure(tuple(view_objects))
    view = ReifiedView(logical_form_etr=etr_predicted_conclusion.__str__())
    return view

