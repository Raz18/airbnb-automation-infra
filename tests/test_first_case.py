from pages.home_page import HomePage
import os
import pytest

def test_first_case(page):
    """
    Test that verifies searching for Tel Aviv apartments for 2 adults and analyzes results.

    Steps:
    1. Search for apartments in Tel Aviv with 2 adults and selected dates
    2. Validate search parameters are reflected in results
    3. Find the highest-rated listing and cheapest listing
    4. Save results to file for review

    Expected Outcomes:
    - Search should return valid results
    - Search parameters should match the input criteria
    - Should successfully identify highest rated and cheapest listings
    - Results should be saved to a file

    Assumptions:
    - Internet connection is available
    - Airbnb website is accessible
    - Test user has necessary permissions
    """
    # Test parameters
    LOCATION = "Tel Aviv"
    ADULTS = 2  
    try:
        # 1. Set up search with required parameters
        home_page = HomePage(page)
        home_page.wait_for_home_page()

        # Configure search parameters
        home_page.search_for_location(LOCATION)
        check_in, check_out = home_page.select_dates()
        home_page.select_guests(adults_num=ADULTS)

        # Execute search
        search_results_page = home_page.search()
        search_results_page.wait_for_results()

        # 2. Verify search returned valid results
        results_count = search_results_page.get_results_count()
        assert results_count > 0, f"No results found. Expected at least 1 result, got {results_count}"

        # Validate result filters match our search criteria
        validation_status = search_results_page.validate_search_results(
            guests_count=ADULTS,
            check_in=check_in,
            check_out=check_out,
            location="Tel Aviv"
        )
        assert all(validation_status.values()), f"Search validation failed: {validation_status}"

        # 3. Analyze results to find best options
        highest_rated_listing = search_results_page.get_highest_rated_listing()
        assert highest_rated_listing is not None, "Failed to find highest rated listing"
        print(f"Highest Rated Listing: {highest_rated_listing}")

        cheapest_listing = search_results_page.get_cheapest_listing()
        assert cheapest_listing is not None, "Failed to find cheapest listing"
        print(f"Cheapest Listing: {cheapest_listing}")

        # 4. Save results to temp directory for review
        temp_file = search_results_page.save_results_to_file(highest_rated_listing, cheapest_listing)
        assert os.path.exists(temp_file), f"Failed to save results to file: {temp_file}"

    except Exception as e:
        pytest.fail(f"Test failed with error: {str(e)}")
