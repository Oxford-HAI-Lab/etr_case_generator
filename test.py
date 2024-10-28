from pyetr import View
from generate_cases import view_to_natural_language

v = View.from_str("{Ten()Two(),Seven()Nine()}^{}")
print(view_to_natural_language(v))
