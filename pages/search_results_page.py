import re

from pages.base_page import BasePage
import os
import json
from datetime import datetime

from pages.listing_page import ListingPage


class SearchResultsPage(BasePage):
    """Page object for the Search Results page"""

    # Locators
    SEARCH_RESULTS = '[data-testid="card-container"]'
    LISTINGS_PAGE_TITLE = '[data-testid="stays-page-heading"]'
    # search results bar
    SEARCH_RESULTS_DATE = '[data-testid="little-search-anytime"]'
    SEARCH_RESULTS_GUESTS = '[data-testid="little-search-guests"]'
    SEARCH_RESULTS_LOCATION = '[data-testid="little-search-location"]'
    # Specific data locators
    PRICE_ELEMENT = 'div._tt122m span[aria-hidden="true"]'
    RATING_ELEMENT = 'div.t1a9j9y7 span[aria-hidden="true"]'
    TITLE_ELEMENT = 'div[data-testid="listing-card-title"]'
    DESCRIPTION_ELEMENT = 'div[data-testid="listing-card-subtitle"]'

    def __init__(self, page):
        super().__init__(page)

    def wait_for_results(self):
        """Wait for search results to load"""
        self.wait_for(self.SEARCH_RESULTS)
        self.logger.info("Search results loaded")

    def get_results_count(self):
        """Get the number of search results"""
        results = self.locate(self.SEARCH_RESULTS).all()
        count = len(results)
        self.logger.info(f"Found {count} listings")
        return count

    def get_search_title(self):
        """Get the search results title/heading"""
        return self.get_text(self.LISTINGS_PAGE_TITLE)

    def validate_search_results(self, guests_count, check_in: str, check_out: str, location: str = 'razsa'):
        """Validate search results"""
        self.logger.info("Validating search results")
        validation_results = {}

        search_title = self.get_text(self.LISTINGS_PAGE_TITLE)
        count_match = re.search(r'(\d+,?\d*)', search_title)
        # Remove commas from the number string and convert to int
        count_str = count_match.group(1).replace(',', '')
        print(search_title)
        if location in search_title and int(count_str) > 0 or 'Over' in search_title:
            self.logger.info(f"Search results count: {count_str}")
            validation_results["location"] = True
        else:
            self.logger.warning(f"{location} is not in {search_title}")
            validation_results["location"] = False

        # Check if the first listing matches the search criteria
        first_listing_page = self.navigate_to_listing(self.locate(self.SEARCH_RESULTS).first)
        first_listing_page.wait_for_page_load()
        # Extract  details
        listing_details = first_listing_page.get_reservation_details()
        # Check if the listing matches the search criteria
        if str(guests_count) in listing_details['guests']:
            validation_results["guests"] = True
        else:
            self.logger.warning(f"Guest count mismatch: {listing_details['guests']} vs {guests_count}")
            validation_results["guests"] = False
        # Check if the dates matches the search criteria
        if check_in in listing_details['check_in'] and check_out in listing_details['check_out']:
            validation_results["dates"] = True
        else:
            self.logger.warning(
                f"Date mismatch: {listing_details['check_in']} vs {check_in} and {listing_details['check_out']} vs {check_out}")
            validation_results["dates"] = False

        self.logger.info(f"Validation results: {validation_results}")
        return validation_results

    def navigate_to_listing(self, listing_element):
        """
        Click on a specific listing card and handle the new page that opens.

        Args:
            listing_element: The Playwright locator for the listing card

        Returns:
            The new page object for the listing details
        """
        self.logger.info("Clicking on a listing")

        try:
            # Click on the listing and handle new page/tab
            with self.page.context.expect_page() as new_page_info:
                listing_element.click()

            # Get the new page
            new_page = new_page_info.value
            new_page.wait_for_load_state("networkidle")
            # Instantiate the ListingPage and wait for it to load
            listing_page = ListingPage(new_page)
            listing_page.wait_for_page_load()

            self.logger.info(f"Opened listing in new tab: {new_page.url}")
            return listing_page

        except Exception as e:
            self.logger.error(f"Failed to click on listing: {e}")
            return None

    def iterate_over_all_pages(self, max_pages: int = 5) -> list:
        """
        Iterates over search results pages up to max_pages.
        On each page, it collects all listings and then navigates to the next page.

        Returns:
            list: A list of all listings found across the pages.
        """
        self.logger.info("Starting iteration over all pages of search results")
        current_page = 1
        all_listings = []  # To store listings from all pages

        while True:
            self.logger.info(f"Processing page {current_page}")
            # Wait for the search results to load
            self.wait_for(self.SEARCH_RESULTS)
            # Collect listings from the current page.
            page_listings = self.page.locator(self.SEARCH_RESULTS).all()
            all_listings.extend(page_listings)
            self.logger.info(f"Collected {len(page_listings)} listings from page {current_page}")
            # Scroll to bottom to ensure pagination is loaded.
            self.page.mouse.wheel(0, 1000)

            # Calculate the next page number and attempt to click its link.
            next_page_number = current_page + 1
            self.logger.info(f"Attempting to navigate to page number {next_page_number}")

            # Use get_by_role to locate the next page link by its accessible name.
            next_page_link = self.page.get_by_role("link", name=str(next_page_number)).first
            if not next_page_link.is_visible():
                self.logger.info(f"Next page link for page {next_page_number} not visible. Assuming last page reached.")
                break

            next_page_link.click()
            current_page = next_page_number

        self.logger.info(f"Finished iterating {current_page} pages and collected {len(all_listings)} listings in total")
        return all_listings

    def _extract_listing_details(self, listing):
        """Helper method to extract details from a listing element.
        """
        title_elem = listing.locator(self.TITLE_ELEMENT).first
        title = title_elem.text_content().strip() if title_elem.is_visible() else "N/A"

        # Get subtitle
        name_elem = listing.locator(self.DESCRIPTION_ELEMENT).first
        subtitle = name_elem.text_content().strip() if name_elem.is_visible() else "N/A"

        # Get rating: expect a value like "4.95" possibly followed by review count in text.
        rating_elem = listing.locator(self.RATING_ELEMENT).first
        rating_text = rating_elem.text_content().strip() if rating_elem.is_visible() else "0"

        try:
            parts = rating_text.split(" ")
            rating = float(parts[0])

            # Extract review count if available
            reviews = 0
            if len(parts) > 1 and "(" in parts[1] and ")" in parts[1]:
                reviews = int(parts[1].strip("()"))
        except Exception as e:
            self.logger.warning(f"Error parsing rating: {rating_text} – {e}")
            rating = 0
            reviews = 0

        listing_price = listing.locator(self.PRICE_ELEMENT).first
        price_text = listing_price.text_content().strip() if listing_price.is_visible() else "0"
        # Remove any non-digit characters;
        price_value = ''.join(filter(str.isdigit, price_text))
        price = int(price_value) if price_value else 0

        return {
            "name": title,
            "subtitle": subtitle,
            "rating": rating,
            "reviews": reviews,
            "price": price,
        }

    def get_highest_rated_listing(self):
        """Find the listing with the highest rating, prioritizing more reviews"""
        self.logger.info("Looking for highest-rated listing")

        highest_rating = 0
        most_reviews = 0
        highest_rated = None
        current_page = 1
        page_listings = []

        while True:
            self.logger.info("Starting iteration over all pages of search results")
            self.logger.info(f"Processing page {current_page}")
            # Wait for the search results to load
            self.wait_for(self.SEARCH_RESULTS)
            # Collect listings from the current page.
            page_listings = self.page.locator(self.SEARCH_RESULTS).all()
            self.logger.info(f"Collected {len(page_listings)} listings from page {current_page}")
            for listing in page_listings:
                # Get the rating element using the correct locator
                self.logger.info("Looking for highest-rated listing in the current page")
                rating_element = listing.locator(self.RATING_ELEMENT).first

                # Check if rating element is visible before getting text
                if not rating_element.is_visible():
                    continue

                try:
                    rating_text = rating_element.text_content().strip()
                    self.logger.info(f"Rating text found: {rating_text}")

                    # Extract rating and review count
                    # Format expected: "4.95 (117)"
                    parts = rating_text.split(" ")
                    rating = float(parts[0])

                    # Extract review count from the format
                    reviews = int(parts[1].strip("()"))

                    # First prioritize higher ratings
                    if rating > highest_rating:
                        highest_rating = rating
                        most_reviews = reviews
                        highest_rated = listing
                        self.logger.info(f"New highest rating found: {rating} with {reviews} reviews")
                    # If ratings are EXACTLY equal, prioritize more reviews
                    elif rating == highest_rating and reviews > most_reviews:
                        most_reviews = reviews
                        highest_rated = listing
                        self.logger.info(f"Same rating but more reviews: {rating} with {reviews} reviews")

                except Exception as e:
                    self.logger.warning(f"Couldn't parse rating from listing: {e}")
                    continue

            if highest_rated:
                self.logger.info(f"Found highest rated listing with rating {highest_rating} and {most_reviews} reviews")
            else:
                self.logger.warning("No listing with highest rating found")

            # Scroll to bottom to ensure pagination is loaded.
            self.page.mouse.wheel(0, 2000)
            # Calculate the next page number and attempt to click its link.
            next_page_number = current_page + 1
            self.logger.info(f"Attempting to navigate to page number {next_page_number}")

            # Use get_by_role to locate the next page link by its accessible name.
            next_page_link = self.page.get_by_role("link", name=str(next_page_number)).first

            try:
                is_visible = next_page_link.is_visible(timeout=5000)  # Use a shorter timeout
                if not is_visible:
                    self.logger.info(
                        f"Next page link for page {next_page_number} not visible. Assuming last page reached.")
                    break
            except Exception as e:
                self.logger.warning(f"Error checking if next page link is visible: {e}")
                break

            try:
                next_page_link.click()
                current_page = next_page_number
            except Exception as e:
                self.logger.error(f"Error navigating to next page: {e}")
                break

        return highest_rated

    def get_cheapest_listing(self):
        """Find the listing with the lowest price"""
        self.logger.info("Looking for cheapest listing")

        lowest_price = float('inf')
        cheapest_listing = None
        listings= self.page.locator(self.SEARCH_RESULTS).all()


        for listing in listings:
            # Get the price element using the correct locator
            price_elem = listing.locator(self.PRICE_ELEMENT).first

            if not price_elem.is_visible():
                continue

            price_text = price_elem.text_content().strip()

            # Extract just the price number
            try:
                # Remove any non-digit characters
                price_value = ''.join(filter(str.isdigit, price_text))
                price = int(price_value) if price_value else float('inf')

                # If this is the lowest price we've found so far
                if price < lowest_price:
                    lowest_price = price
                    cheapest_listing = listing
                    self.logger.info(f"New lowest price found: {price}")
            except Exception as e:
                self.logger.warning(f"Couldn't parse price from '{price_text}': {e}")

        if cheapest_listing:
            self.logger.info(f"Found cheapest listing with price {lowest_price}")
        else:
            self.logger.warning("No listings with prices found")

        # Return the actual listing element, not the extracted details
        return cheapest_listing

    def save_results_to_file(self, highest_rated_listing, cheapest_card_listing):
        """Save the highest rated and cheapest listings to a file"""
        # Create temp directory if it doesn't exist
        os.makedirs("temp", exist_ok=True)

        # Extract details from the cards
        highest_rated = self._extract_listing_details(highest_rated_listing) if highest_rated_listing else None
        cheapest = self._extract_listing_details(cheapest_card_listing) if cheapest_card_listing else None

        # Create results data
        results = {
            "search_url": self.page.url,
            "search_title": self.get_search_title(),
            "timestamp": datetime.now().strftime("%d-%m-%Y_%H-%M-%S"),
            "highest_rated": highest_rated,
            "cheapest": cheapest
        }

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        filename = f"temp/cheapest_and_highest_rated_details_{timestamp}.json"
        # Save to file as JSON
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

        self.logger.info(f"Saved results to {filename}")
