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
- **API Mocks**: Handle API interception and mocking for controlled testing

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
    ├── logger.py              # Logging setup
    └── api_mocks.py           # API mocking utilities
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
         │                      │                       │
         ▼                      ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  API Mocks      │     │    Logging      │     │    Reports      │
│  (api_mocks.py) │     │  (logger.py)    │     │  (temp/*.json)  │
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
| `utils/api_mocks.py` | Manages API request interception and mocking for controlled testing scenarios |
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
- **dotenv**: Environment variable management
- **Playwright API Mocking**: Request interception and response mocking

### Design Patterns

The framework employs several design patterns:

1. **Page Object Model (POM)**: Separates UI interaction code from test logic for better maintainability
2. **Chain of Responsibility**: Page methods return page objects to enable fluent test flows
3. **Factory Pattern**: Page initialization and creation
4. **Singleton**: Configuration management through AppSettings class
5. **Mock Pattern**: API request interception and response mocking for controlled testing

### Key Features

#### 1. API Mocking System

The framework includes a sophisticated API mocking system for controlled testing:

```python
class APIMockHandler:
    """Handles API request interception and mocking"""
    
    def setup_mock(self, page, mock_type):
        """Sets up mock responses for specific API endpoints"""
        # Configures request interception
        # Sets up mock responses
        # Handles different mock scenarios (e.g., phone verification)
```

Key features:
- Request interception for specific endpoints
- Dynamic response mocking
- Support for different mock scenarios
- Automatic cleanup after tests

#### 2. Finding Highest-Rated Listings

The suite includes sophisticated algorithms to identify premium listings:

- Sorts listings by review score (highest rating first)
- Considers listings with more reviews to be more reliable 
- Extracts listing details including price, location, and amenities
- Compares listing attributes to find the optimal choice

Implementation highlights from `search_results_page.py`:
```python
def get_highest_rated_listing(self):
    """
    Algorithm for finding highest-rated listing:
    1. Iterate through all pages of results
    2. For each listing:
       - Extract rating and review count
       - Compare with current best
       - Update if better rating or same rating with more reviews
    3. Return best listing details
    """
    highest_rating = -1.0
    most_reviews = -1
    best_details = None
    
    for listing in self._iterate_listings_on_all_pages():
        rating, reviews = self._extract_rating_and_reviews(listing)
        if (rating > highest_rating) or (rating == highest_rating and reviews > most_reviews):
            highest_rating = rating
            most_reviews = reviews
            best_details = self._extract_listing_details(listing)
```

#### 3. Multi-Page Navigation

The framework can scan through multiple pages of search results:

```python
def iterate_over_all_pages(self):
    """Iterates over search results pages up to max_pages."""
    # Collects listings from each page
    # Handles pagination navigation
    # Returns complete collection of listings across pages
```

#### 4. Detailed Test Flows

The framework includes several detailed test flows:

1. **Search Validation**: Verifies search functionality with various parameters
2. **Highest-Rated Selection**: Identifies and selects listings with the best reviews
3. **Booking Flow Validation**: Tests the reservation process and validates details
4. **Phone Verification**: Tests phone number validation with API mocking

#### 5. Result Validation

The framework includes comprehensive validation of search results and reservation details:

```python
def validate_search_results(self, guests_count, check_in, check_out, location):
    """
    Comprehensive validation system:
    1. Validate search parameters
    2. Check listing details
    3. Verify dates and guest count
    4. Cross-reference with search criteria
    """
    validation_results = {}
    
    # Validate location
    search_title = self.get_text(self.LISTINGS_PAGE_TITLE)
    validation_results["location"] = location in search_title
    
    # Validate listing details
    first_listing = self.navigate_to_listing(self.SEARCH_RESULTS.first)
    listing_details = first_listing.get_reservation_card_details()
    
    # Cross-reference with search criteria
    validation_results["guests"] = str(guests_count) in listing_details['guests']
    validation_results["dates"] = (
        listing_details['check_in'] in check_in and 
        listing_details['check_out'] in check_out
    )
    
    return validation_results
```

```python
def reserve_and_validate_reservation_details(self, details):
    """
    Reservation validation system:
    1. Compare total price
    2. Validate guest count
    3. Check dates
    4. Verify all fee breakdowns
    """
    validation_passed = True
    validation_messages = []

    # Price validation
    actual_price = self._extract_total_price()
    if actual_price != details['total_price']:
        validation_passed = False
        validation_messages.append(f"Price mismatch: {actual_price} vs {details['total_price']}")

    # Guest validation
    actual_guests = self._extract_guest_count()
    if actual_guests != details['guests']:
        validation_passed = False
        validation_messages.append(f"Guest count mismatch: {actual_guests} vs {details['guests']}")

    # Date validation
    actual_dates = self._extract_dates()
    if actual_dates != (details['check_in'], details['check_out']):
        validation_passed = False
        validation_messages.append("Date mismatch")

    return validation_passed, validation_messages
```

#### 6. Result Persistence

Search and reservation results are saved to JSON files for analysis:

```python
def save_results_to_file(self, highest_rated_listing_details, cheapest_card_listing):
    """Structured data persistence"""
    results = {
        "search_url": self.page.url,
        "search_title": self.get_search_title(),
        "timestamp": self.datetime_helper.get_timestamp(),
        "highest_rated": highest_rated_listing_details,
        "cheapest": cheapest_card_listing
    }
    
    filename = f"temp/cheapest_and_highest_rated_details_{self.datetime_helper.get_filename_timestamp()}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
```

## Environment Setup

### Required Environment Variables

Create a `.env` file in your project root with the following variables:

```env
BASE_URL=https://www.airbnb.com
HEADLESS=True
SLOWMO=50
TIMEOUT=30000
BROWSER_VIEWPORT_WIDTH=1920
BROWSER_VIEWPORT_HEIGHT=1080
RECORD_VIDEO=False
BROWSER_ARGS=
PHONE_NUMBER=your_phone_number_here
LOG_LEVEL=INFO
```

Note: Never commit the actual `.env` file to version control. Use `.env.example` as a template.

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
   Test results, including highest rated listing, cheapest, logs and reports, will be saved in the `temp` directory on your host machine.

## Configuration

The test suite is highly configurable through environment variables or the `.env` file:

- `BASE_URL`: Target Airbnb environment (default: https://www.airbnb.com)
- `HEADLESS`: Run browsers in headless mode (default: true)
- `SLOWMO`: Slow down execution for debugging (in ms)
- `TIMEOUT`: Maximum wait time for elements (in ms)
- `RECORD_VIDEO`: Enable video recording of test runs
- `PHONE_NUMBER`: user phone number to use in the tests
- `BROWSER_VIEWPORT_WIDTH`: Browser viewport width (default: 1920)
- `BROWSER_VIEWPORT_HEIGHT`: Browser viewport height (default: 1080)
- `LOG_LEVEL`: Logging level (default: INFO)

## Test Reports

After test execution, detailed reports are available in:
- Log files: `temp/test_runs/test_run_[timestamp].log`
- Videos (if enabled): `temp/videos/`
- HTML Reports: `temp/report.html`
- Result JSONs: `temp/cheapest_and_highest_rated_details_[timestamp].json`
- API Mock Logs: `temp/api_mocks_[timestamp].log`

## Extending the Test Suite

To add new test cases:
1. Create page objects for any new pages in the `pages` directory
2. Add test methods in the `tests` directory
3. Follow the existing patterns for maintainability
4. Add API mocks if needed in `utils/api_mocks.py`

### Example: Adding a New Test Case

```python
def test_new_feature(page):
    """Test a new feature on Airbnb"""
    # Initialize page objects
    home_page = HomePage(page)
    home_page.wait_for_home_page()
    
    # Set up API mocks if needed
    api_mock = APIMockHandler()
    api_mock.setup_mock(page, "new_feature_mock")
    
    # Implement test steps
    # ...
    
    # Add assertions
    assert some_condition, "Failure message"
```

## Troubleshooting

- **Element not found**: Ensure selectors are up to date as Airbnb's UI changes frequently
- **Test timeouts**: Adjust the TIMEOUT setting in app_settings.py
- **Docker issues**: Check Docker logs and ensure proper volume mounting
- **API Mock failures**: Check the API mock logs in temp directory
- **Environment issues**: Verify .env file is properly configured

### Technical Architecture

The framework implements sophisticated algorithms for data analysis and navigation:

#### 1. Search Results Analysis

The framework uses advanced algorithms to analyze search results across multiple pages:

```python
def get_highest_rated_listing(self):
    """
    Algorithm for finding highest-rated listing:
    1. Iterate through all pages of results
    2. For each listing:
       - Extract rating and review count
       - Compare with current best
       - Update if better rating or same rating with more reviews
    3. Return best listing details
    """
    highest_rating = -1.0
    most_reviews = -1
    best_details = None
    
    for listing in self._iterate_listings_on_all_pages():
        rating, reviews = self._extract_rating_and_reviews(listing)
        if (rating > highest_rating) or (rating == highest_rating and reviews > most_reviews):
            highest_rating = rating
            most_reviews = reviews
            best_details = self._extract_listing_details(listing)
```

#### 2. Price Analysis Algorithm

```python
def get_cheapest_listing(self):
    """
    Algorithm for finding cheapest listing:
    1. Initialize with infinity as lowest price
    2. Iterate through all pages
    3. For each listing:
       - Extract and parse price
       - Handle currency conversion
       - Compare with current lowest
       - Update if cheaper
    4. Return cheapest listing details
    """
    lowest_price = float('inf')
    cheapest_details = None
    
    for listing in self._iterate_listings_on_all_pages():
        price = self._extract_price(listing)
        if price < lowest_price:
            lowest_price = price
            cheapest_details = self._extract_listing_details(listing)
```

#### 3. Multi-Page Navigation System

```python
def _iterate_listings_on_all_pages(self):
    """
    Advanced pagination system:
    1. Track processed listings to avoid duplicates
    2. Handle dynamic loading
    3. Implement retry mechanism
    4. Support infinite scroll
    """
    self._current_page = 1
    self._processed_listings = set()

    while True:
        try:
            self.wait_for_element(self.SEARCH_RESULTS)
            page_listings = self.locate(self.SEARCH_RESULTS).all()
            
            for listing in page_listings:
                listing_id = listing.get_attribute("id")
                if listing_id not in self._processed_listings:
                    self._processed_listings.add(listing_id)
                    yield listing

            if not self._has_next_page():
                break

            self._current_page += 1
            self._navigate_to_next_page()
        except Exception as e:
            self.logger.error(f"Error processing page {self._current_page}: {e}")
            break
```

#### 4. Data Extraction and Validation

```python
def validate_search_results(self, guests_count, check_in, check_out, location):
    """
    Comprehensive validation system:
    1. Validate search parameters
    2. Check listing details
    3. Verify dates and guest count
    4. Cross-reference with search criteria
    """
    validation_results = {}
    
    # Validate location
    search_title = self.get_text(self.LISTINGS_PAGE_TITLE)
    validation_results["location"] = location in search_title
    
    # Validate listing details
    first_listing = self.navigate_to_listing(self.SEARCH_RESULTS.first)
    listing_details = first_listing.get_reservation_card_details()
    
    # Cross-reference with search criteria
    validation_results["guests"] = str(guests_count) in listing_details['guests']
    validation_results["dates"] = (
        listing_details['check_in'] in check_in and 
        listing_details['check_out'] in check_out
    )
    
    return validation_results
```

#### 5. Reservation Flow Validation

```python
def validate_details_on_confirmation(self, expected_details):
    """
    Reservation validation system:
    1. Compare total price
    2. Validate guest count
    3. Check dates
    4. Verify all fee breakdowns
    """
    validation_passed = True
    validation_messages = []

    # Price validation
    actual_price = self._extract_total_price()
    if actual_price != expected_details['total_price']:
        validation_passed = False
        validation_messages.append(f"Price mismatch: {actual_price} vs {expected_details['total_price']}")

    # Guest validation
    actual_guests = self._extract_guest_count()
    if actual_guests != expected_details['guests']:
        validation_passed = False
        validation_messages.append(f"Guest count mismatch: {actual_guests} vs {expected_details['guests']}")

    # Date validation
    actual_dates = self._extract_dates()
    if actual_dates != (expected_details['check_in'], expected_details['check_out']):
        validation_passed = False
        validation_messages.append("Date mismatch")

    return validation_passed, validation_messages
```

### Performance Optimizations

The framework implements several performance optimizations:

1. **Lazy Loading**: Elements are loaded only when needed
2. **Caching**: Frequently accessed data is cached
3. **Parallel Processing**: Multiple listings are processed concurrently
4. **Smart Retries**: Intelligent retry mechanism for flaky operations
5. **Resource Management**: Proper cleanup of browser resources

### Error Handling

Comprehensive error handling is implemented throughout:

```python
def _extract_price(self, price_text: str) -> int:
    """Robust price extraction with error handling"""
    try:
        if 'NEW' in price_text:
            return 0
        price_text = price_text.replace('$', '').replace(',', '').strip()
        price_value = ''.join(filter(str.isdigit, price_text))
        return int(price_value) if price_value else 0
    except Exception as e:
        self.logger.warning(f"Failed to extract price: {e}")
        return 0
```

### Data Persistence

Results are saved in structured JSON format:

```python
def save_results_to_file(self, highest_rated_listing_details, cheapest_card_listing):
    """Structured data persistence"""
    results = {
        "search_url": self.page.url,
        "search_title": self.get_search_title(),
        "timestamp": self.datetime_helper.get_timestamp(),
        "highest_rated": highest_rated_listing_details,
        "cheapest": cheapest_card_listing
    }
    
    filename = f"temp/cheapest_and_highest_rated_details_{self.datetime_helper.get_filename_timestamp()}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
```
