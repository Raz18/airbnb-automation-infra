#!/bin/bash

# Exit on any error
set -e

# Create temp directory if it doesn't exist
mkdir -p temp

# Run the tests in the Docker container with environment variables
docker run --rm \
  -v $(pwd):/app \
  -v $(pwd)/temp:/app/temp \
  --env-file .env \
  mcr.microsoft.com/playwright/python:v1.51.0-jammy \
  python -m pytest tests/ "$@"

echo "Tests completed! Results saved in temp directory."
