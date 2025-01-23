import argparse
import csv
import glob
import json
import os
from pathlib import Path


# TODO: JSON_KEYS needs to have all of these values (just the leaf nodes)
"""
{
    "doc_id": int
    "doc": dict (2 items)
    {
        "question": str (985 characters)
        "scoring_guide": dict (4 items)
        {
            "etr_predicted": str (60 characters)
            "etr_predicted_is_classically_correct": bool
            "generation_details": dict (9 items)
            {
                "atoms_distributed_over_views_SMT_ONLY": int
                "total_num_atoms": int
                "num_disjuncts": int
                "num_conjuncts": int
                "num_predicates_per_problem": int
                "num_objects_per_problem": int
                "premises_etr": list[str] (2 items)
                "premises_fnodes": list[str] (2 items)
                "is_chain_of_thought": bool
            }
            "open_ended": dict (2 items)
            {
                "conclusion_agrees_in_yes_no_case": bool
            }
            "yes_no": dict (4 items)
            {
                "conclusion_etr": str (31 characters)
                "conclusion_is_classically_correct": bool
                "conclusion_english": str (30 characters)
                "conclusion_is_etr_predicted": bool
            }
        }
    }
    "resps": list[list[str]] (1 items)
    "filtered_resps": list[str] (1 items)
    "correct": float
    "is_etr_predicted": float
    "is_etr_predicted_exact": float
    "len_response": int
    "parse_error": int
    "model_answer": str (31 characters)
    "full_model_response": str (79 characters)
    "correct_and_etr": float
    "correct_and_not_etr": float
    "not_correct_and_etr": float
    "not_correct_and_not_etr": float
}
"""



JSON_KEYS = [
    "doc_id",
    "doc/question",
    "doc/scoring_guide/etr_predicted",
    # TODO(andrew): Add more
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert JSONL results files to CSV format"
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="open_ended",
        help="Pattern to match in filenames (default: 'open_ended')",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="lm_eval/tasks/etr_problems/good_results/all_results.csv",
        help="Output CSV file location (default: good_results/all_results.csv)",
    )
    return parser.parse_args()


def load_jsonl_files(pattern: str):
    """Load all JSONL files matching pattern from good_results dir and subdirs."""
    base_dir = "lm_eval/tasks/etr_problems/good_results"
    
    # Get files in base dir and one level deep that contain "samples"
    search_paths = [
        f"{base_dir}/*samples*{pattern}*.jsonl",
        f"{base_dir}/*/*samples*{pattern}*.jsonl"
    ]
    
    files = []
    for path in search_paths:
        files.extend(glob.glob(path))
    
    results = {}
    for file in files:
        with open(file) as f:
            lines = f.readlines()
            results[file] = [json.loads(line) for line in lines]
            
    return results


def write_to_csv(results: dict, output_file: str):
    """Write JSON data to CSV file using specified keys."""
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=JSON_KEYS,
            quoting=csv.QUOTE_MINIMAL,
            quotechar='"',
            doublequote=True
        )
        writer.writeheader()
        
        # Write each JSON entry as a CSV row
        for file_data in results.values():
            for entry in file_data:
                row = {}
                for key in JSON_KEYS:
                    # Handle nested keys (e.g., "doc/question")
                    value = entry
                    for k in key.split('/'):
                        value = value.get(k, '')
                    # Replace newlines with paragraph mark for readability
                    if isinstance(value, str):
                        value = " ¶ ".join(line.strip() for line in value.splitlines())
                    row[key] = value
                writer.writerow(row)


def main():
    args = parse_args()
    
    # Load matching files
    results = load_jsonl_files(args.pattern)
    
    # Print stats
    print(f"\nFound {len(results)} files matching pattern '{args.pattern}':")
    # for file, data in results.items():
    #     print(f"{file}: {len(data)} samples")
    
    # Write results to CSV
    write_to_csv(results, args.output)
    print(f"\nWrote results to: {args.output}")


if __name__ == "__main__":
    main()
