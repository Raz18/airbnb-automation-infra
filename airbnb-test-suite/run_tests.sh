#!/bin/bash

# Exit on any error
set -e

# Create temp directory if it doesn't exist
mkdir -p temp

# Run the tests in the Docker container with environment variables
docker run --rm \
  -v "$(pwd)/temp:/app/temp" \
  -v "$(pwd)/.env:/app/.env" \
  --ipc=host \
  airbnb-test-suite \
  python -m pytest -v -s tests/

echo "Tests completed! Results saved in temp directory."
