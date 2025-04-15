#!/bin/bash

# Exit on any error
set -e

# Create temp directory if it doesn't exist
mkdir -p temp

# Run the tests in the Docker container
docker run --rm -v $(pwd)/temp:/app/temp airbnb-test-suite pytest tests/ "$@"

echo "Tests completed! Results saved in temp directory."