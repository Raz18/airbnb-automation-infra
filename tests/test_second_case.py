import pytest
import logging
from datetime import datetime, timedelta

from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage
from pages.listing_page import ListingPage
from config.app_settings import AppSettings

# Setup logger for the test module
logger = logging.getLogger(__name__)

def test_second_case(page):
    """
    Test Case: Search, select highest-rated listing, and attempt reservation
    
    Steps:
    1. Search for listings in Tel Aviv with specific dates and guest count
    2. Validate search results and parameters
    3. Find and navigate to highest-rated listing
    4. Extract and save reservation details
    5. Proceed with reservation and validate details
    6. Enter phone number for verification
    """
    # Test parameters
    LOCATION = "Tel Aviv"
    ADULTS = 2
    CHILDREN = 1

    # Initialize page objects
    home_page = HomePage(page)
    try:
        # Step 1: Perform search
        logger.info("Step 1: Performing search with specified parameters")
        home_page.navigate_to_home()
        home_page.search_for_location(LOCATION)
        check_in, check_out = home_page.select_dates()
        home_page.select_guests(
            adults_num=ADULTS,
            kids_num=CHILDREN
        )
        search_results_page = home_page.search()

        # Step 2: Validate search results
        logger.info("Step 2: Validating search results")
        search_results_page.wait_for_results()
        

        # Validate search parameters
        validation_results = search_results_page.validate_search_results(
            guests_count=ADULTS + CHILDREN,
            check_in=check_in,
            check_out=check_out,
            location=LOCATION
        )
        
        assert all(validation_results.values()), f"Search validation failed: {validation_results}"

        # Step 3: Find highest-rated listing
        logger.info("Step 3: Finding highest-rated listing")
        highest_rated = search_results_page.get_highest_rated_listing()
        assert highest_rated is not None, "Failed to find highest-rated listing"
        #assert "url" in highest_rated, "Highest-rated listing missing URL"
        logger.info(f"Found highest-rated listing: {highest_rated.get('name')}")

        # Step 4: Navigate to listing and extract details
        logger.info("Step 4: Navigating to listing and extracting details")
        listing_page = search_results_page.navigate_to_listing_url(highest_rated["url"])
        listing_page.wait_for_page_load()
        
        reservation_details = listing_page.get_reservation_card_details()
        assert reservation_details, "Failed to extract reservation details"
        
        # Save reservation details
        saved_file = listing_page.save_reservation_details_to_file(reservation_details)
        assert saved_file is not None, "Failed to save reservation details"

        # Step 5: Proceed with reservation
        logger.info("Step 5: Proceeding with reservation")
        listing_page.click_reserve_button()
        listing_page.validate_details_on_confirmation(reservation_details)

        # Step 6: Enter phone number
        logger.info("Step 6: Entering phone number")
        phone_entry_success = listing_page.enter_phone_number()
        assert phone_entry_success, "Failed to enter phone number"

        logger.info("Test completed successfully")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        # Take screenshots on failure
        if search_results_page:
            search_results_page.take_screenshot("error_search_results.png")
        if listing_page:
            listing_page.take_screenshot("error_listing_page.png")
        raise
