import json
import random
from typing import Dict, List, Tuple

def load_variable_statements(file_path: str) -> Dict[str, List[Dict[str, str]]]:
    with open(file_path, 'r') as file:
        return json.load(file)

def get_random_variable(variable_statements: Dict[str, List[Dict[str, str]]]) -> Tuple[str, str, Tuple[str, str]]:
    theme = random.choice(list(variable_statements.keys()))
    variable_data = random.choice(variable_statements[theme])
    return variable_data['variable_short'], variable_data['variable_name'], (variable_data['positive'], variable_data['negative'])

def get_all_themes(variable_statements: Dict[str, List[Dict[str, str]]]) -> List[str]:
    return list(variable_statements.keys())
