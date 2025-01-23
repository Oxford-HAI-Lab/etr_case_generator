import argparse
import csv
import glob
import json
import os
from pathlib import Path


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
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=JSON_KEYS)
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
                    row[key] = value
                writer.writerow(row)


def main():
    args = parse_args()
    
    # Load matching files
    results = load_jsonl_files(args.pattern)
    
    # Print stats
    print(f"\nFound {len(results)} files matching pattern '{args.pattern}':")
    for file, data in results.items():
        print(f"{file}: {len(data)} samples")
    
    # Write results to CSV
    write_to_csv(results, args.output)
    print(f"\nWrote results to: {args.output}")


if __name__ == "__main__":
    main()
