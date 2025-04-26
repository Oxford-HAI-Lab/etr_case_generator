#!/bin/bash
set -o pipefail

# Source project-specific API keys
source "$(dirname "$0")/source_keys.sh"

# Verify required API keys are available
if [ -z "$OPENROUTER_API_KEY" ] || [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: Required API keys are missing"
    echo "Please ensure both OPENROUTER_API_KEY and OPENAI_API_KEY are set in keys.env"
    exit 1
fi

# Define OpenRouter model configurations
declare -A MODELS=(
    ["google/gemini-2.5-pro-preview-03-25"]="Gemini 2.5 Pro"
    ["openai/chatgpt-4o-latest"]="ChatGPT-4o-latest"
    ["google/gemini-2-5-flash-preview"]="Gemini 2.5 Flash"
    ["google/gemma-3-27b-it"]="Gemma 3 27B"
    ["anthropic/claude-3-5-sonnet"]="Claude 3.5 Sonnet"
    ["anthropic/claude-3-opus"]="Claude 3 Opus"
    ["google/gemma-2-9b-it"]="Gemma 2 9B"
#    ["openai/gpt-4-0125-preview"]="GPT-4 (0125)"
#    ["openai/gpt-4-0613"]="GPT-4-0613"
    ["openai/gpt-3.5-turbo-1106"]="GPT-3.5-Turbo-1106"
#    ["thudm/chatglm-6b"]="ChatGLM 6B"
    ["meta-llama/llama-3.2-1b-instruct"]="Llama-3.2 1B"
    ["meta-llama/llama-2-13b-chat"]="Llama-13B"
)

# Dataset paths
DATASETS=(
    "/home/keenan/Dev/etr_case_generator/datasets/smallset_open_ended.jsonl"
#    "/home/keenan/Dev/etr_case_generator/datasets/250302/multiview_open_ended.jsonl"
#    "/home/keenan/Dev/etr_case_generator/datasets/fully_balanced_yes_no.jsonl"
)

# Create a log directory
LOG_DIR="evaluation_logs"
mkdir -p "$LOG_DIR"

# Function to run evaluation for a model
run_evaluation() {
    local model="$1"
    local model_name="$2"
    local dataset="$3"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local dataset_type=$(basename "$dataset" | sed 's/multiview_\(.*\)\.jsonl/\1/')
    local log_file="${LOG_DIR}/openrouter_${model_name}_${dataset_type}_${timestamp}.log"
    
    echo "Running evaluation for OpenRouter model: ${model_name} (${model}) on ${dataset_type}"
    echo "Logging to: ${log_file}"
    
    # Run the evaluation command and tee output to both terminal and log file
    ./lm_eval/tasks/etr_problems/run_evaluation_open_router.sh \
        --dataset "$dataset" \
        -m "$model" \
        --good 2>&1 | tee "$log_file"
    
    # Need to check the exit status of the evaluation command, not tee
    # This uses bash's pipefail option to get the first command's status
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo "✓ Evaluation completed successfully for ${model_name} on ${dataset_type}"
    else
        echo "✗ Evaluation failed for ${model_name} on ${dataset_type}. Check ${log_file} for details"
    fi
}

# Iterate through models
for model in "${!MODELS[@]}"; do
    model_name="${MODELS[$model]}"
    for dataset in "${DATASETS[@]}"; do
        run_evaluation "$model" "$model_name" "$dataset"
    done
done

echo "All evaluations completed. Logs are available in ${LOG_DIR}/"
