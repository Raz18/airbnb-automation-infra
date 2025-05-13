#!/bin/bash

# Exit on any error
set -e

echo "Installing Airbnb Test Suite..."

# Build the Docker image
echo "Building Docker image..."
docker build -t airbnb-test-suite .

echo "Installation complete!"
echo ""
echo "To run tests:"
echo "  ./run_tests.sh"
echo ""
echo "This will execute tests inside the Docker container and save results to the temp directory."