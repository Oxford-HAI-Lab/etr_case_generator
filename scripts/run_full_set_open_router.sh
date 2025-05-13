#!/bin/bash
set -o pipefail

# Display usage information
function show_usage {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --dataset DATASET_PATH    Path to the dataset file (.jsonl)"
    echo "  --output OUTPUT_DIR       Output directory name (default: results)"
    echo "  -h, --help                Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 --dataset /path/to/dataset.jsonl --output custom_results"
}

# Parse command line arguments
DATASET=""
OUTPUT_DIR="results"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dataset)
            DATASET="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Error: Unknown option $1"
            show_usage
            exit 1
            ;;
    esac
done

# Source project-specific API keys
source "$(dirname "$0")/source_keys.sh"

# Verify required API keys are available
if [ -z "$OPENROUTER_API_KEY" ] || [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: Required API keys are missing"
    echo "Please ensure both OPENROUTER_API_KEY and OPENAI_API_KEY are set in keys.env"
    exit 1
fi

# Check if dataset was provided
if [ -z "$DATASET" ]; then
    echo "Error: No dataset specified"
    show_usage
    exit 1
fi

# Verify dataset file exists
if [ ! -f "$DATASET" ]; then
    echo "Error: Dataset file does not exist: $DATASET"
    exit 1
fi

# Define OpenRouter model configurations as an ordered list
# Each entry is a string with format "model_id|model_name"
#MODELS=(
#    # Just one, for debugging
#    "anthropic/claude-3.5-sonnet|Claude 3.5 Sonnet"
#)
MODELS=(
    "mistralai/mistral-small-24b-instruct-2501|Mistral Small 24B Instruct"
    "microsoft/phi-4|Phi 4"
    "anthropic/claude-3-haiku|Claude 3 Haiku"
    "01-ai/yi-34b-chat|Yi 34B Chat"
    "meta-llama/llama-3-8b-instruct|Llama 3 8B Instruct"
    "mistralai/mixtral-8x22b-instruct|Mixtral 8x22B Instruct"
    "mistralai/mistral-medium|Mistral Medium"
    "mistralai/mistral-7b-instruct-v0.2|Mistral 7B Instruct v0.2"
    "qwen/qwen-4b-chat|Qwen 4B Chat"
    "openai/gpt-4.5-preview|GPT-4.5 Preview"
    "openai/chatgpt-4o-latest|ChatGPT-4o-latest"
    "google/gemini-2.5-flash-preview|Gemini 2.5 Flash"
    "google/gemma-3-27b-it|Gemma 3 27B"
    "anthropic/claude-3.5-sonnet|Claude 3.5 Sonnet"
    "anthropic/claude-3-opus|Claude 3 Opus"
    "google/gemma-2-9b-it|Gemma 2 9B"
    "openai/gpt-3.5-turbo-1106|GPT-3.5-Turbo-1106"
    "meta-llama/llama-3.2-1b-instruct|Llama-3.2 1B"
    "meta-llama/llama-2-13b-chat|Llama-13B"
    "anthropic/claude-3.7-sonnet|Claude 3.7 Sonnet"
    "deepseek/deepseek-chat-v3-0324|DeepSeek V3 0324"
    "qwen/qwq-32b|QwQ 32B"
    "openai/o1-mini|o1 Mini"
    "deepseek/deepseek-chat|DeepSeek V3"
    "mistralai/mistral-large-2407|Mistral Large 2407"

    # Slow, put them last
    "qwen/qwen-72b-chat|Qwen 72B Chat" # Slow
    "deepseek/deepseek-r1|DeepSeek R1" # Slow
    "nvidia/llama-3.3-nemotron-super-49b-v1|Llama 3.3 Nemotron Super 49B" # Slow
    "x-ai/grok-2-1212|Grok 2 1212" # Slow
    "nvidia/llama-3.1-nemotron-70b-instruct|Llama 3.1 Nemotron 70B" # Slow
    "meta-llama/llama-3.1-70b-instruct|Llama 3.1 70B Instruct" # Slow

    # Models with issues (commented out) (Do not use!)
    # "google/gemini-2.5-pro-preview-03-25|Gemini 2.5 Pro" # Many responses are empty string
    # "openai/gpt-4-0125-preview|GPT-4 (0125)" # DNE
    # "openai/gpt-4-0613|GPT-4-0613" # DNE
    # "thudm/chatglm-6b|ChatGLM 6B" # DNE
)

# Dataset is now provided as a command line argument
# Try /home/keenan/Dev/etr_case_generator/datasets/reverse_largeset_open_ended.jsonl

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
    ./scripts/run_evaluation_open_router.sh \
        --dataset "$dataset" \
        -m "$model" \
        --output "$OUTPUT_DIR" 2>&1 | tee "$log_file"
    
    # Need to check the exit status of the evaluation command, not tee
    # This uses bash's pipefail option to get the first command's status
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo "✓ Evaluation completed successfully for ${model_name} on ${dataset_type}"
    else
        echo "✗ Evaluation failed for ${model_name} on ${dataset_type}. Check ${log_file} for details"
    fi
}

# Iterate through models in order
for model_entry in "${MODELS[@]}"; do
    # Extract model ID and name from the delimited string
    model=$(echo "$model_entry" | cut -d'|' -f1)
    model_name=$(echo "$model_entry" | cut -d'|' -f2)

    # Use the single dataset from command line argument
    run_evaluation "$model" "$model_name" "$DATASET"
done

echo "All evaluations completed. Logs are available in ${LOG_DIR}/"
