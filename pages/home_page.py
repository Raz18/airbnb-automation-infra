import logging
from datetime import datetime, timedelta
from typing import Tuple
from playwright.sync_api import Page, Error, expect  # Added expect

# Assuming BasePage is correctly imported
from pages.base_page import BasePage
# Assuming SearchResultsPage is correctly imported for type hinting/return value
from pages.search_results_page import SearchResultsPage
# Assuming AppSettings provides BASE_URL
from config.app_settings import AppSettings


class HomePage(BasePage):
    """
    Page object for the Airbnb home page.
    Handles navigation, searching location, selecting dates and guests.
    Refactored to use user-provided locators and date selection logic.
    """

    # --- Locators (Using User-Provided Locators) ---
    SEARCH_BAR = '[data-testid="structured-search-input-field-query"]'
    # Note: LOCATION_INPUT is same as SEARCH_BAR in the provided file.
    # If they are distinct after clicking, separate locators might be needed.
    LOCATION_INPUT = '[data-testid="structured-search-input-field-query"]'
    # Note: Date buttons are not defined here as selection uses get_by_role with dynamic names.
    # CHECK_IN_BUTTON = '[data-testid="structured-search-input-field-split-dates-0"]' # Original, unused by new date logic
    # CHECK_OUT_BUTTON = '[data-testid="structured-search-input-field-split-dates-1"]' # Original, unused by new date logic
    GUESTS_BUTTON = '[data-testid="structured-search-input-field-guests-button"]'
    SEARCH_BUTTON = '[data-testid="structured-search-input-search-button"]'
    # CALENDAR_DAY = 'data-testid^="calendar-day-"' # Original, unused by new date logic
    ADULTS_INCREASE = '[data-testid="stepper-adults-increase-button"]'
    KIDS_INCREASE = '[data-testid="stepper-children-increase-button"]'

    def __init__(self, page: Page):
        super().__init__(page)
        # Logger is initialized in BasePage

    def navigate_to_home(self):
        """Navigate to Airbnb home page defined in AppSettings."""
        self.navigate_to(AppSettings.BASE_URL)
        self.wait_for_home_page()

    def wait_for_home_page(self, timeout: int = 15000):
        """Wait for the home page search bar to be visible."""
        self.logger.info("Waiting for Home Page to load...")
        self.wait_for_element(self.SEARCH_BAR, timeout=timeout)  # Use user's SEARCH_BAR locator
        self.logger.info("Home Page loaded.")
        # Consider adding cookie banner handling here if necessary

    def search_for_location(self, location: str):
        """Enter location in the search field using user's locators."""
        self.logger.info(f"Entering location: '{location}'")
        # Click the main search bar/input area first
        self.click_element(self.SEARCH_BAR)
        # Fill the location into the input field (using the same locator as per user file)
        self.write_on_element(self.LOCATION_INPUT, location)
        # Press Enter to select the location (as per user file logic)
        # This assumes pressing Enter selects the first suggestion or confirms the input.
        self.page.keyboard.press("Enter")
        self.logger.info(f"Entered location '{location}' and pressed Enter.")

    def select_dates(self, check_in_days_offset: int = 30, stay_duration_days: int = 3) -> Tuple[str, str]:
        """
        Select check-in and check-out dates using button role and the specific
        accessibility name format requested by the user.

        Args:
            check_in_days_offset: Days from today for check-in (default: 30).
            stay_duration_days: Length of stay in days (default: 3).

        Returns:
            A tuple containing formatted check-in and check-out date strings ("MM/DD/YYYY").
        """
        self.logger.info(
            f"Selecting dates using role/name: check-in in {check_in_days_offset} days for {stay_duration_days} days stay")

        # Calculate target dates
        today = datetime.now()
        check_in_date = today + timedelta(days=check_in_days_offset)
        check_out_date = check_in_date + timedelta(days=stay_duration_days)

        # Format date according to the required accessibility name pattern
        # Example: "17, Saturday, May 2025."
        check_in_name = f"{check_in_date.day}, {check_in_date.strftime('%A')}, {check_in_date.strftime('%B')} {check_in_date.year}."
        check_out_name = f"{check_out_date.day}, {check_out_date.strftime('%A')}, {check_out_date.strftime('%B')} {check_out_date.year}."

        # --- Select Check-in Date ---
        self.logger.info(f"Looking for check-in date button with name: '{check_in_name}'")
        try:
            check_in_button = self.get_by_role("button", name=check_in_name)
            # Optional: Add a wait for the button to be enabled/visible if needed
            expect(check_in_button).to_be_enabled(timeout=15000)
            self.click_element(check_in_button)
            self.logger.info(f"Selected check-in date: {check_in_name}")
        except Error as e:
            self.logger.error(f"Could not find or click check-in date button with name '{check_in_name}': {e}")
            self.take_screenshot(f"error_checkin_date_{self.datetime_helper.get_filename_timestamp()}.png")
            raise

        # Wait briefly between selections as per user's code
        self.page.wait_for_timeout(300)

        # --- Select Check-out Date ---
        self.logger.info(f"Looking for check-out date button with name: '{check_out_name}'")
        try:
            check_out_button = self.get_by_role("button", name=check_out_name)
            # Optional: Add a wait for the button to be enabled/visible
            expect(check_out_button).to_be_enabled(timeout=15000)
            self.click_element(check_out_button)
            self.logger.info(f"Selected check-out date: {check_out_name}")
        except Error as e:
            self.logger.error(f"Could not find or click check-out date button with name '{check_out_name}': {e}")
            self.take_screenshot(f"error_checkout_date_{self.datetime_helper.get_filename_timestamp()}.png")
            raise

        # Format dates for return value (consistent with test expectations)
        # Using standard formatting, adjust if tests expect non-padded day/month
        formatted_check_in = check_in_date.strftime("%m/%d/%Y")
        formatted_check_out = check_out_date.strftime("%m/%d/%Y")

        self.logger.info(f"Returning formatted dates: {formatted_check_in} to {formatted_check_out}")
        return formatted_check_in, formatted_check_out

    def select_guests(self, adults_num: int = 1, kids_num: int = 0):
        """Select number of guests using user's locators."""
        self.logger.info(f"Selecting guests: Adults={adults_num}, Kids={kids_num}")
        self.click_element(self.GUESTS_BUTTON)
        # Optional: Wait for the guest selection panel to appear if needed
        # self.wait_for_element('[data-testid="structured-search-input-field-guests-panel"]') # Example panel locator

        # Add adults
        # Note: Assumes clicking N times works from default state.
        # A more robust approach would check current value first.
        adult_increment_button = self.locate(self.ADULTS_INCREASE)
        self.logger.info(f"Clicking adult increment {adults_num} times...")
        for i in range(adults_num):
            try:
                # Use a slightly longer timeout per click if UI is slow
                self.click_element(adult_increment_button, timeout=5000)
                self.page.wait_for_timeout(50)  # Tiny pause
            except Error as e:
                self.logger.error(f"Failed to click adult increment button on iteration {i + 1}: {e}")
                self.take_screenshot(f"error_adult_increment_{self.datetime_helper.get_filename_timestamp()}.png")
                raise

        # Add kids if needed
        if kids_num > 0:
            kids_increment_button = self.locate(self.KIDS_INCREASE)
            self.logger.info(f"Clicking kids increment {kids_num} times...")
            for i in range(kids_num):
                try:
                    self.click_element(kids_increment_button, timeout=5000)
                    self.page.wait_for_timeout(50)  # Tiny pause
                except Error as e:
                    self.logger.error(f"Failed to click child increment button on iteration {i + 1}: {e}")
                    self.take_screenshot(f"error_child_increment_{self.datetime_helper.get_filename_timestamp()}.png")
                    raise

        self.logger.info("Guest selection complete.")

    def search(self) -> SearchResultsPage:
        """Click the search button to initiate search using user's locator."""
        self.logger.info("Initiating search...")
        self.click_element(self.SEARCH_BUTTON)
        self.logger.info("Search submitted.")
        # Initialize and return the next page object
        results_page = SearchResultsPage(self.page)
        # It's generally better to wait explicitly in the test or the results page methods
        # results_page.wait_for_results_load() # Removed from here
        return results_page
