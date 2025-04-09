#!/bin/bash
set -e  # Exit on error

# Format code with ruff (includes isort functionality)
echo "Formatting code with Ruff..."
ruff format src/

# Run ruff linter on src directory
echo "Running Ruff linter on src directory..."
ruff check src/ --fix

echo "Lint completed successfully!"
