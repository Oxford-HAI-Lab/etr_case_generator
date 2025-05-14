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
#  "mistralai/mistral-small-24b-instruct-2501|Mistral Small 24B Instruct" # Not thinking - Mistral models don't expose separate thinking tokens by default
  "microsoft/phi-4|Phi 4" # Not thinking
  "anthropic/claude-3-haiku|Claude 3 Haiku" # Not thinking
#  "01-ai/yi-34b-chat|Yi 34B Chat" # Unsure thinking
  "meta-llama/llama-3-8b-instruct|Llama 3 8B Instruct" # Not thinking
#  "mistralai/mixtral-8x22b-instruct|Mixtral 8x22B Instruct" # Not thinking - Mixtral models don't expose separate thinking tokens by default
#  "mistralai/mistral-medium|Mistral Medium" # Not thinking - Mistral models don't expose separate thinking tokens by default
#  "mistralai/mistral-7b-instruct-v0.2|Mistral 7B Instruct v0.2" # Not thinking - Mistral models don't expose separate thinking tokens by default
#  "qwen/qwen-4b-chat|Qwen 4B Chat" # Thinking - Qwen models have thinking enabled by default with <think> tags
#  "openai/gpt-4.5-preview|GPT-4.5 Preview" # Not thinking
#  "openai/chatgpt-4o-latest|ChatGPT-4o-latest" # Not thinking
#  "google/gemini-2.5-flash-preview|Gemini 2.5 Flash" # Not thinking
#  "google/gemma-3-27b-it|Gemma 3 27B" # Unsure thinking
#  "anthropic/claude-3.5-sonnet|Claude 3.5 Sonnet" # Not thinking
#  "anthropic/claude-3-opus|Claude 3 Opus" # Not thinking
#  "google/gemma-2-9b-it|Gemma 2 9B" # Unsure thinking
#  "openai/gpt-3.5-turbo-1106|GPT-3.5-Turbo-1106" # Not thinking
#  "meta-llama/llama-3.2-1b-instruct|Llama-3.2 1B" # Unsure thinking
#  "meta-llama/llama-2-13b-chat|Llama-13B" # Unsure thinking
#  "anthropic/claude-3.7-sonnet|Claude 3.7 Sonnet" # Not thinking
  "deepseek/deepseek-chat-v3-0324|DeepSeek V3 0324" # Not thinking
#  "qwen/qwq-32b|QwQ 32B" # Thinking - QwQ is Qwen's reasoning model with thinking enabled by default
#  "openai/o1-mini|o1 Mini" # Not thinking
#  "deepseek/deepseek-chat|DeepSeek V3" # Not thinking
#  "mistralai/mistral-large-2407|Mistral Large 2407" # Not thinking - Mistral models don't expose separate thinking tokens by default
#
#  # Not used in the original run
#  "openai/gpt-4o-mini-2024-07-18|GPT-4o-mini-2024-07-18" # Not thinking - OpenAI models don't expose separate thinking tokens by default
#  "anthropic/claude-3-sonnet|Claude 3 Sonnet" # Not thinking
#  "openai/gpt-4-0314|GPT-4-0314" # Not thinking
#  "anthropic/claude-1|Claude-1" # Not thinking
#  "cohere/command-r-plus-04-2024|Command R (04-2024)" # Unsure thinking
#  "anthropic/claude-2.0|Claude-2.0" # Not thinking
#  "qwen/qwen-32b-chat|Qwen1.5-32B-Chat" # Unsure thinking
#  "microsoft/phi-3-medium-4k-instruct|Phi-3-Medium-4k-Instruct" # Unsure thinking
#  "anthropic/claude-2.1|Claude-2.1" # Not thinking
#  "qwen/qwen-14b-chat|Qwen1.5-14B-Chat" # Unsure thinking
#  "anthropic/claude-instant-1|Claude-Instant-1" # Not thinking
#  "openai/gpt-3.5-turbo-0613|GPT-3.5-Turbo-0613" # Not thinking
#  "meta-llama/llama-3.2-3b-instruct|Meta-Llama-3.2-3B-Instruct" # Unsure thinking
#  "snowflake/snowflake-arctic-instruct|Snowflake Arctic Instruct" # Unsure thinking
#  "nousresearch/nous-hermes-2-mixtral-8x7b-dpo|Nous-Hermes-2-Mixtral-8x7B-DPO" # Unsure thinking
#  "teknium/openhermes-2.5-mistral-7b|OpenHermes-2.5-Mistral-7B" # Unsure thinking
#  "qwen/qwen-7b-chat|Qwen1.5-7B-Chat" # Thinking - Qwen models have thinking enabled by default with <think> tags
#  "meta-llama/codellama-34b-instruct|CodeLlama-34B-instruct" # Unsure thinking
#  "meta-llama/codellama-70b-instruct|CodeLlama-70B-instruct" # Unsure thinking
#  "microsoft/phi-3-mini-128k-instruct|Phi-3-Mini-128k-Instruct" # Unsure thinking
#  "google/gemma-7b-it|Gemma-7B-it" # Unsure thinking
#  "togethercomputer/stripedhyena-nous-7b|StripedHyena-Nous-7B" # Unsure thinking
#  "allenai/olmo-7b-instruct|OLMo-7B-instruct" # Unsure thinking
#  "mistralai/mistral-7b-instruct-v0.1|Mistral-7B-Instruct-v0.1" # Not thinking - Mistral models don't expose separate thinking tokens by default
#  "google/gemini-flash-1.5|Gemini-1.5-Flash-002" # Not thinking
#  "openai/gpt-4|GPT-4-0613" # Not thinking
#  "mistralai/mixtral-8x7b-instruct|Mixtral-8x7B-Instruct-v0.1" # Not thinking - Mixtral models don't expose separate thinking tokens by default
#  "openai/gpt-3.5-turbo-0125|GPT-3.5-Turbo-0125" # Not thinking
#  "databricks/dbrx-instruct|DBRX-Instruct-Preview" # Unsure thinking
#  "huggingfaceh4/zephyr-7b-beta|Zephyr-7B-beta" # Unsure thinking
#  "google/palm-2-chat-bison|PaLM-Chat-Bison-001" # Unsure thinking
#  "rwkv/rwkv-5-world-3b|RWKV-4-Raven-14B" # Not thinking - RWKV models don't implement thinking token capabilities
#
#  # Slow, put them last
#  "qwen/qwen-72b-chat|Qwen 72B Chat" # Thinking - Qwen models have thinking enabled by default with <think> tags
#  "deepseek/deepseek-r1|DeepSeek R1" # Unsure thinking - specialized for reasoning but unclear if thinking tokens are exposed by default
#  "nvidia/llama-3.3-nemotron-super-49b-v1|Llama 3.3 Nemotron Super 49B" # Unsure thinking
#  "x-ai/grok-2-1212|Grok 2 1212" # Unsure thinking - may have reasoning capabilities but documentation is unclear
#  "nvidia/llama-3.1-nemotron-70b-instruct|Llama 3.1 Nemotron 70B" # Unsure thinking
#  "meta-llama/llama-3.1-70b-instruct|Llama 3.1 70B Instruct" # Unsure thinking
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
