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

```
airbnb-test-suite/
├── Dockerfile                 # Container definition
├── README.md                  # Project documentation
├── config/                    # Configuration settings
│   ├── __init__.py
│   └── app_settings.py        # Environment & test settings
├── install.sh                 # Docker installation script
├── pages/                     # Page Object Model implementation
│   ├── __init__.py
│   ├── base_page.py           # Common page functionality
│   ├── home_page.py           # Airbnb homepage interactions
│   ├── listing_page.py        # Listing details page
│   └── search_results_page.py # Search results interactions
├── requirements.txt           # Python dependencies
├── run_tests.sh               # Test execution script
├── tests/                     # Test scenarios
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── test_first_case.py     # Search validation test
│   └── test_second_case.py    # Reservation flow test
└── utils/                     # Shared utilities
    ├── __init__.py
    ├── date_time_helper.py    # Date/time functions
    └── logger.py              # Logging setup
```

### Component Interactions

The framework components interact in the following way:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Test Scripts   │────▶│   Page Objects  │────▶│    Playwright   │
│  (test_*.py)    │◀────│  (pages/*.py)   │◀────│    Browser      │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                      │                       │
         ▼                      ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Configuration  │     │    Utilities    │     │    Results      │
│  (app_settings) │     │  (utils/*.py)   │     │  (temp folder)  │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Key Files and Their Functionality

#### Core Framework

| File | Purpose |
|------|---------|
| `pages/base_page.py` | Provides core functionality for all page objects, including element location, interaction methods, and common utilities |
| `config/app_settings.py` | Manages environment variables and configuration settings for the test framework |
| `utils/logger.py` | Configures logging for all components with console and file outputs |
| `utils/date_time_helper.py` | Handles date/time formatting and operations |
| `tests/conftest.py` | Sets up Playwright browser instances and test fixtures |

#### Page Objects

| Page Object | Functionality |
|-------------|--------------|
| `pages/home_page.py` | Handles interactions with the Airbnb homepage, including search form inputs and navigation |
| `pages/search_results_page.py` | Manages search results functionality, including listing analysis (highest-rated, cheapest) and pagination |
| `pages/listing_page.py` | Controls interaction with individual property listings, reservation flow, and detail validation |

#### Test Cases

| Test | Description |
|------|-------------|
| `tests/test_first_case.py` | Validates the search functionality with basic parameters and results analysis |
| `tests/test_second_case.py` | Tests the end-to-end reservation flow, including validation of listing details |

#### Infrastructure

| File | Purpose |
|------|---------|
| `Dockerfile` | Defines the container environment with Python, Playwright dependencies |
| `install.sh` | Builds the Docker image for the test environment |
| `run_tests.sh` | Executes tests in the Docker container with volume mounting for results |
| `requirements.txt` | Lists Python package dependencies |

### Technologies Used

- **Playwright**: Browser automation framework for cross-browser testing
- **pytest**: Test runner and assertion library
- **Python**: Primary programming language
- **Docker**: Containerization for consistent test environments

### Design Patterns

The framework employs several design patterns:

1. **Page Object Model (POM)**: Separates UI interaction code from test logic for better maintainability
2. **Chain of Responsibility**: Page methods return page objects to enable fluent test flows
3. **Factory Pattern**: Page initialization and creation
4. **Singleton**: Configuration management through AppSettings class

### Key Features

#### 1. Finding Highest-Rated Listings

The suite includes sophisticated algorithms to identify premium listings:

- Sorts listings by review score (highest rating first)
- Considers listings with more reviews to be more reliable 
- Extracts listing details including price, location, and amenities
- Compares listing attributes to find the optimal choice

Implementation highlights from `search_results_page.py`:
```python
def get_highest_rated_listing(self):
    """Find the listing with the highest rating, prioritizing more reviews"""
    # Algorithm that iterates through multiple pages of results
    # Compares ratings and review counts to find best listing
    # Returns detailed listing information including URL
```

#### 2. Multi-Page Navigation

The framework can scan through multiple pages of search results:

```python
def iterate_over_all_pages(self):
    """Iterates over search results pages up to max_pages."""
    # Collects listings from each page
    # Handles pagination navigation
    # Returns complete collection of listings across pages
```

#### 3. Detailed Test Flows

The framework includes several detailed test flows:

1. **Search Validation**: Verifies search functionality with various parameters
2. **Highest-Rated Selection**: Identifies and selects listings with the best reviews
3. **Booking Flow Validation**: Tests the reservation process and validates details

#### 4. Result Validation

The framework includes comprehensive validation of search results and reservation details:

```python
def validate_search_results(self, guests_count, check_in, check_out, location):
    """Validates that search results match the specified criteria"""
    # Checks location in search title
    # Validates guest count and dates in listing details
    # Returns validation results dictionary
```

```python
def reserve_and_validate_reservation_details(self, details):
    """Validates reservation details after clicking Reserve button"""
    # Compares expected vs. actual total price
    # Validates cleaning fee amounts
    # Checks listing title consistency
    # Returns detailed validation results
```

#### 5. Result Persistence

Search and reservation results are saved to JSON files for analysis:

```python
def save_results_to_file(self, highest_rated_listing_details, cheapest_card_listing):
    """Save the highest rated and cheapest listings to a file"""
    # Creates structured data including timestamp, search parameters
    # Writes to JSON file in temp directory
    # Returns filename for reference
```

## Running the Tests using pure python

To run the test suite on a Linux system, follow these steps:

1. **Ensure Prerequisites Are Installed**:
   Make sure Python, Node.js, and Playwright are installed as described in the [Prerequisites](#prerequisites) section.

2. **Set Up the Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   playwright install
   ```

3. **Run the Tests**:
   ```bash
   pytest tests/
   ```

4. **View Logs**:
   the cheapest/highly rated will be saved in a json format under temp folder
    detailed Logs will be saved in the `temp/test_runs` directory.

## Running the Tests Using Docker

To run the test suite in a Dockerized environment, follow these steps:

1. **Clone the repository to your machine using the command**:
    ```bash
    git clone https://github.com/Raz18/airbnb-automation-infra.git
     ```

2. **Navigate to the relevant airbnb-test-suite root directory under the cloned repository**:
   ```bash
   cd /airbnb-automation-infra/airbnb-test-suite
   ```
   
3. **Enable permissions to relevant install.sh and run_tests.sh**:
   ```bash
   chmod 775 install.sh
   chmod 775 run_tests.sh
   ```
   
4. **Build the Docker Image**:
   ```bash
   ./install.sh
   ```

5. **Run the Tests**:
   Use the provided `run_tests.sh` script to execute the tests inside the Docker container:
   ```bash
   ./run_tests.sh
   ```

6. **Pass Additional Arguments**:
   To pass additional arguments to `pytest`, append them to the `run_tests.sh` command. For example:
   ```bash
   ./run_tests.sh  --headed
   ```

7. **View Results**:
   the cheapest/highly rated will be saved in a json format under temp folder
   Test results, including logs and reports, will be saved in the `temp` directory on your host machine.

## Configuration

The test suite is highly configurable through environment variables or the `.env` file:

- `BASE_URL`: Target Airbnb environment (default: https://www.airbnb.com)
- `HEADLESS`: Run browsers in headless mode (default: true)
- `SLOWMO`: Slow down execution for debugging (in ms)
- `TIMEOUT`: Maximum wait time for elements (in ms)
- `RECORD_VIDEO`: Enable video recording of test runs
- `PHONE_NUMBER`: user phone number to use in the tests

## Test Reports

After test execution, detailed reports are available in:
- Log files: `temp/test_runs/test_run_[timestamp].log`
- Videos (if enabled): `temp/videos/`
- HTML Reports: `temp/report.html`
- Result JSONs: `temp/cheapest_and_highest_rated_details_[timestamp].json`

## Extending the Test Suite

To add new test cases:
1. Create page objects for any new pages in the `pages` directory
2. Add test methods in the `tests` directory
3. Follow the existing patterns for maintainability

### Example: Adding a New Test Case

```python
def test_new_feature(page):
    """Test a new feature on Airbnb"""
    # Initialize page objects
    home_page = HomePage(page)
    home_page.wait_for_home_page()
    
    # Implement test steps
    # ...
    
    # Add assertions
    assert some_condition, "Failure message"
```

## Troubleshooting

- **Element not found**: Ensure selectors are up to date as Airbnb's UI changes frequently
- **Test timeouts**: Adjust the TIMEOUT setting in app_settings.py
- **Docker issues**: Check Docker logs and ensure proper volume mounting
