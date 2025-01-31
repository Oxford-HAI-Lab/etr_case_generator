#!/bin/bash

# Function to handle cleanup on script exit
#cleanup() {
#    rm -f temp_shuffled.jsonl
#    rm -rf batch_files 2>/dev/null
#}
#trap cleanup EXIT

# Check if input file is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <input_jsonl_file>"
    exit 1
fi

INPUT_FILE="$1"
N_BATCHES=20

# Create directory for batch files
mkdir -p batch_files

# Shuffle the input file
shuf "$INPUT_FILE" > temp_shuffled.jsonl

# Count total lines
total_lines=$(wc -l < temp_shuffled.jsonl)
lines_per_batch=$((total_lines / N_BATCHES + 1))

# Get base filename without extension
base_name=$(basename "$INPUT_FILE" .jsonl)

# Split the shuffled file into N batches
split -l "$lines_per_batch" temp_shuffled.jsonl "batch_files/${base_name}_batch_" --additional-suffix=.jsonl

# Process each batch file
for batch_file in batch_files/${base_name}_batch_*.jsonl; do
    echo "----------------------------------------------------------------------------------------"
    echo "Processing $batch_file"
    echo "----------------------------------------------------------------------------------------"
    max_attempts=3
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if "$(dirname "$0")/run_evaluation.sh" --dataset "$batch_file" -m deepseek-r1; then
            echo "Successfully processed $batch_file"
            break
        else
            echo "Attempt $attempt failed for $batch_file"
            if [ $attempt -eq $max_attempts ]; then
                echo "All attempts failed for $batch_file"
            else
                echo "Retrying..."
                sleep 5
            fi
            ((attempt++))
        fi
    done
done

echo "All batches processed"
