#!/bin/bash

# Source project-specific API keys
KEYS_FILE="/home/keenan/Dev/etr_case_generator/keys.env"
if [ -f "$KEYS_FILE" ]; then
    source "$KEYS_FILE"
else
    echo "Error: API keys file not found at $KEYS_FILE"
    echo "Please copy keys.env.template to keys.env and add your API keys"
    exit 1
fi