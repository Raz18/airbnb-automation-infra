from pages.base_page import BasePage
from config.app_settings import AppSettings
from pages.search_results_page import SearchResultsPage
from datetime import datetime, timedelta

class HomePage(BasePage):
    """Page object for the Airbnb home page"""

    # Locators
    SEARCH_BAR = '[data-testid="structured-search-input-field-query"]'
    LOCATION_INPUT = '[data-testid="structured-search-input-field-query"]'
    CHECK_IN_BUTTON = '[data-testid="structured-search-input-field-split-dates-0"]'
    CHECK_OUT_BUTTON = '[data-testid="structured-search-input-field-split-dates-1"]'
    GUESTS_BUTTON = '[data-testid="structured-search-input-field-guests-button"]'
    SEARCH_BUTTON = '[data-testid="structured-search-input-search-button"]'
    CALENDAR_DAY = 'data-testid^="calendar-day-"'
    ADULTS_INCREASE = '[data-testid="stepper-adults-increase-button"]'
    KIDS_INCREASE = '[data-testid="stepper-children-increase-button"]'

    def __init__(self, page):
        super().__init__(page)

    def navigate_to_home(self):
        """Navigate to Airbnb home page"""
        self.navigate_to(AppSettings.BASE_URL)
        self.logger.info("Navigated to Airbnb home page")

    def wait_for_home_page(self):
        """Wait for the home page to load"""
        self.wait_for(self.SEARCH_BAR)
        self.logger.info("Home page loaded")

    def search_for_location(self, location):
        """Enter location in the search field"""
        self.click_element(self.SEARCH_BAR)
        self.write_on_element(self.LOCATION_INPUT, location)
        self.page.keyboard.press("Enter")
        self.logger.info(f"Entered location: {location}")

    def select_dates(self, check_in_days_offset=30, stay_duration=3):
        """
        Select check-in and check-out dates using button role and accessibility name

        Args:
            check_in_days_offset: Days from today for check-in (default: 30 days/1 month)
            stay_duration: Length of stay in days (default: 3)
        """

        self.logger.info(f"Selecting dates: check-in in {check_in_days_offset} days for {stay_duration} days stay")

        # Calculate target dates
        today = datetime.now()
        check_in_date = today + timedelta(days=check_in_days_offset)
        check_out_date = check_in_date + timedelta(days=stay_duration)

        # Example: "15, Thursday, May 2025."
        check_in_name = f"{check_in_date.day}, {check_in_date.strftime('%A')}, {check_in_date.strftime('%B')} {check_in_date.year}."
        check_out_name = f"{check_out_date.day}, {check_out_date.strftime('%A')}, {check_out_date.strftime('%B')} {check_out_date.year}."

        # Select check-in date using role and name
        self.logger.info(f"Looking for check-in date: {check_in_name}")
        self.page.get_by_role("button", name=check_in_name).click()
        self.logger.info(f"Selected check-in date: {check_in_name}")

        # Wait briefly between selections
        self.page.wait_for_timeout(300)

        # Select check-out date using role and name
        self.logger.info(f"Looking for check-out date: {check_out_name}")
        self.page.get_by_role("button", name=check_out_name).click()
        self.logger.info(f"Selected check-out date: {check_out_name}")

        formatted_check_in = f"{check_in_date.month}/{check_in_date.day}/{check_in_date.year}"
        formatted_check_out = f"{check_out_date.month}/{check_out_date.day}/{check_out_date.year}"

        self.logger.info(f"Returning formatted dates: {formatted_check_in} to {formatted_check_out}")
        return formatted_check_in, formatted_check_out

    def select_guests(self, adults_num=2, kids_num=0):
        """Select number of guests"""
        self.click_element(self.GUESTS_BUTTON)
        # Add adults
        for _ in range(adults_num):
            self.click_element(self.ADULTS_INCREASE)
        # Add kids if needed
        if kids_num > 0:
            for _ in range(kids_num):
                self.click_element(self.KIDS_INCREASE)


    def search(self):
        """Click the search button to initiate search"""
        self.click_element(self.SEARCH_BUTTON)
        self.logger.info("Clicked search button")
        # Create and return SearchResultsPage instance
        results_page = SearchResultsPage(self.page)
        results_page.wait_for_results()
        return results_page

