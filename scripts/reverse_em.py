# TODO, this should take a file like datasets/smallset_open_ended.jsonl and, for each problem, reverse the set of premises
# Here's an example:
example = {
        "question": "I'm a researcher studying newly discovered psychic abilities. I need to understand their interactions through logical reasoning. Here's what we know:\n\n* Either precognition is not object-reading, or precognition is object-reading and precognition is space-bending.\n* Either precognition is object-reading and precognition is space-bending, or precognition is not space-bending.\n\nFor the purpose of this question, I want you to write what follows in English. Please be succinct, precise and clear in your answer. Write a logical statement of the form \"Answer: From the premises, we can conclude that ...\" and then clearly write your conclusion. Please be succinct, precise, and clear.\n\nWhat if anything follows? I do not have an intended answer in mind, and it is possible that nothing follows. Please be succinct and precise.\n\nI want you to answer immediately. Read the question and provide your answer in the format given.\n\nWhat follows? Answer in the format that I showed you. Write \"Answer: {logical statement}\".",
        "scoring_guide": {
            "etr_predicted": "{spaceBending(precognition())objectReading(precognition())}",
            "etr_predicted_english": "Precognition is object-reading and precognition is space-bending.",
            "etr_predicted_is_classically_correct": False,
            "etr_predicted_conclusion_is_categorical": None,
            "generation_details": {
                "seed_id": "no_seed",
                "atoms_distributed_over_views_SMT_ONLY": 3,
                "total_num_atoms": 6,
                "num_disjuncts": 2,
                "num_conjuncts": 2,
                "num_predicates_per_problem": 3,
                "num_objects_per_problem": 3,
                "premises_etr": ["{spaceBending(precognition())objectReading(precognition()),~objectReading(precognition()*)}", "{spaceBending(precognition())objectReading(precognition()),~spaceBending(precognition()*)}"],
                "premises_english": ["Either precognition is not object-reading, or precognition is object-reading and precognition is space-bending.", "Either precognition is object-reading and precognition is space-bending, or precognition is not space-bending."],
                "premises_fnodes": ["((! objectReading(precognition)) | (spaceBending(precognition) & objectReading(precognition)))", "((! spaceBending(precognition)) | (spaceBending(precognition) & objectReading(precognition)))"],
                "is_chain_of_thought": False
            },
            "open_ended": {
                "conclusion_agrees_in_yes_no_case": True,
                "short_name_to_full_name": {"telepathy": "telepathy", "precognition": "precognition", "psychokinesis": "psychokinesis", "clairvoyance": "clairvoyance", "empathy": "empathy", "astralProjection": "astral projection", "mindControl": "mind control", "psychometry": "psychometry", "teleportation": "teleportation", "realityWarping": "reality warping", "mindreading": "mindreading", "futureSeeing": "future-seeing", "matterMoving": "matter-moving", "prescient": "prescient", "emotionallySensitive": "emotionally sensitive", "soulTraveling": "soul-traveling", "imposing": "imposing", "objectReading": "object-reading", "spaceBending": "space-bending", "realityChanging": "reality-changing"}
            }}}
# For each problem, reverse the set of premises. Here's what that means:
# TODO Reverse the lists scoring_guide/generation_details/premises_etr, scoring_guide/generation_details/premises_fnodes, and scoring_guide/generation_details/premises_english. Each list should be reversed.
# TODO The question needs to be edited. This is going to be a little hacky, so here are some facts we can use to do it.
# # 1. The premises_english are contained in the question string, and each one is prepended with a "* ".
# # 2. The string `\n* ` is unlikely to appear elsewhere in the question, but it might, so make sure it's followed by one of the premises_english.
# # 3. Those can be excised, and the regenerated (and reversed) list can be inserted

# TODO Take in the name of a jsonl as an argument to the script
# TODO Iterate over each line in the jsonl, and apply the reversal as described above
# TODO Emit a new jsonl, which should be named `reverse_{old_name}`
