import json
from etr_case_generator import ETRCaseGenerator

g = ETRCaseGenerator()

dataset = []

N_PER_CLASS = 100

# First generate N_PER_CLASS matching conclusions
while True:
    if len(dataset) >= N_PER_CLASS:
        break
    for p in g.generate_reasoning_problems(
        n_views=20,
        require_categorical_etr=True,
        require_conclusion_match=True,
        n_trials_timeout=1000,
        verbose=True,
    ):
        if len(dataset) >= N_PER_CLASS:
            break
        dataset.append(p.to_dict())
    print("===> Retrying... Dataset so far: ", len(dataset))

# Then generate N_PER_CLASS non-matching conclusions
while True:
    if len(dataset) >= 2 * N_PER_CLASS:
        break
    for p in g.generate_reasoning_problems(
        n_views=20,
        require_categorical_etr=True,
        require_conclusion_match=False,
        n_trials_timeout=1000,
        verbose=True,
    ):
        if len(dataset) >= 2 * N_PER_CLASS:
            break
        dataset.append(p.to_dict())
    print("===> Retrying... Dataset so far: ", len(dataset))


json.dump(dataset, open("etr_v0__2024_10_29.json", "w"))
