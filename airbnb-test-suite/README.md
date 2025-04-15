# Airbnb Test Suite

## Overview

The Airbnb Test Suite is a comprehensive automated testing framework designed to validate key functionality of the Airbnb platform. It uses Playwright with Python to simulate real user interactions and verify that critical user journeys work as expected. The suite includes tests for searching properties, filtering results, viewing listings, and attempting bookings.

## Technical Implementation

### Architecture

The test suite follows the Page Object Model (POM) design pattern, separating UI interactions from test logic:

- **Pages**: Encapsulate page-specific selectors and actions (e.g., `HomePage`, `SearchResultsPage`)
- **Tests**: Focus on business scenarios and assertions
- **Utils**: Provide shared functionality like logging and data handling
- **Config**: Manage environment variables and test settings

### Technologies Used

- **Playwright**: Browser automation framework for cross-browser testing
- **pytest**: Test runner and assertion library
- **Python**: Primary programming language
- **Docker**: Containerization for consistent test environments

### Key Features

#### Finding Highest-Rated Listings

The suite includes sophisticated algorithms to identify premium listings:

- Sorts listings by review score (highest rating first)
- Considers listings with more reviews to be more reliable 
- Extracts listing details including price, location, and amenities
- Compares listing attributes to find the optimal choice

#### Detailed Test Flows

The framework includes several detailed test flows:

1. **Search Validation**: Verifies search functionality with various parameters
2. **Highest-Rated Selection**: Identifies and selects listings with the best reviews
3. **Booking Flow Validation**: Tests the reservation process and validates details

#### Example Test Flow

The `test_second_case` demonstrates a complete user journey:
- Search for apartments for 2 adults and 1 child in Tel Aviv
- Validate search parameters in the results
- Select the highest-rated result based on review scores
- Transition to the listing page and extract details
- Save reservation information for reporting
- Validate booking flow and details

## Prerequisites

...existing content...

## Running the Tests on Linux

To run the test suite on a Linux system, follow these steps:

1. **Ensure Prerequisites Are Installed**:
   Make sure Python, Node.js, and Playwright are installed as described in the [Prerequisites](#prerequisites) section.

2. **Set Up the Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   playwright install
   mkdir -p temp/test_runs
   ```

3. **Run the Tests**:
   ```bash
   pytest tests/
   ```

4. **View Logs**:
   Logs will be saved in the `temp/test_runs` directory.

## Running the Tests Using Docker

To run the test suite in a Dockerized environment, follow these steps:

1. **Build the Docker Image**:
   ```bash
   ./install.sh
   ```

2. **Run the Tests**:
   Use the provided `run_tests.sh` script to execute the tests inside the Docker container:
   ```bash
   ./run_tests.sh
   ```

3. **Pass Additional Arguments**:
   To pass additional arguments to `pytest`, append them to the `run_tests.sh` command. For example:
   ```bash
   ./run_tests.sh -k "test_second_case"
   ```

4. **View Results**:
   Test results, including logs and reports, will be saved in the `temp` directory on your host machine.

## Configuration

The test suite is highly configurable through environment variables or the `.env` file:

- `BASE_URL`: Target Airbnb environment (default: https://www.airbnb.com)
- `HEADLESS`: Run browsers in headless mode (default: true)
- `SLOWMO`: Slow down execution for debugging (in ms)
- `TIMEOUT`: Maximum wait time for elements (in ms)
- `RECORD_VIDEO`: Enable video recording of test runs

## Test Reports

After test execution, detailed reports are available in:
- HTML report: `temp/report.html`
- Log files: `temp/test_runs/test_run_[timestamp].log`
- Videos (if enabled): `temp/videos/`

## Extending the Test Suite

To add new test cases:
1. Create page objects for any new pages in the `pages` directory
2. Add test methods in the `tests` directory
3. Follow the existing patterns for maintainability

...existing content...
