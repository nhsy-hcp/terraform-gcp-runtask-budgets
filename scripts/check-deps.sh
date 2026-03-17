#!/bin/bash
set -euo pipefail

echo "Checking required dependencies..."

# Check for required tools
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "ERROR: $1 not found"
        return 1
    fi
}

check_command python3
check_command terraform
check_command gcloud

if ! command -v pre-commit &> /dev/null; then
    echo "WARNING: pre-commit not found, will install via pip"
fi

echo "✓ All required dependencies found"
