import json
from etr_case_generator import ETRCaseGenerator

g = ETRCaseGenerator()

dataset = []

# First generate 100 matching conclusions
while len(dataset) <= 10:
    for p in g.generate_reasoning_problems(
        n_views=20,
        require_categorical_etr=True,
        require_conclusion_match=True,
        n_trials_timeout=1000,
        verbose=True,
    ):
        dataset.append(p.to_dict())
        if len(dataset) == 10:
            break
    print("Retrying... Dataset so far: ", len(dataset))

# Then generate 100 non-matching conclusions
while len(dataset) <= 20:
    for p in g.generate_reasoning_problems(
        n_views=20,
        require_categorical_etr=True,
        require_conclusion_match=False,
        n_trials_timeout=1000,
        verbose=True,
    ):
        dataset.append(p.to_dict())
        if len(dataset) == 20:
            break
    print("Retrying... Dataset so far: ", len(dataset))

json.dump(dataset, open("etr_dataset.json", "w"))
