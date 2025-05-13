import re
from typing import Dict, List, Optional, Generator
from pages.base_page import BasePage
import os
import json
from datetime import datetime

from pages.listing_page import ListingPage


class SearchResultsPage(BasePage):
    """Page object for the Search Results page"""

    # Extract prices from the search results uss css selector hierarchy
    # prices = page.locator("div.atm_cs_6adqpa > span[aria-hidden='true']").all_inner_texts()

    # Locators
    SEARCH_RESULTS = '[data-testid="card-container"]'
    LISTINGS_PAGE_TITLE = '[data-testid="stays-page-heading"]'
    # search results bar
    SEARCH_RESULTS_DATE = '[data-testid="little-search-anytime"]'
    SEARCH_RESULTS_GUESTS = '[data-testid="little-search-guests"]'
    SEARCH_RESULTS_LOCATION = '[data-testid="little-search-location"]'
    # Specific data locators
    PRICE_ELEMENT = 'div._1qr6aej9 div span[aria-hidden="true"]'
    RATING_ELEMENT = 'div.t1a9j9y7 span[aria-hidden="true"]'
    TITLE_ELEMENT = 'div[data-testid="listing-card-title"]'
    DESCRIPTION_ELEMENT = 'div[data-testid="listing-card-subtitle"] span[data-testid="listing-card-name"]'
    NEXT_PAGE_BUTTON = '[data-testid="pagination-next-button"]'

    def __init__(self, page):
        super().__init__(page)
        self._current_page = 1
        self._processed_listings = set()

    def wait_for_results(self, timeout: int = 30000):
        """Wait for search results to load with configurable timeout"""
        try:
            self.wait_for_element(self.locate(self.SEARCH_RESULTS).first, timeout=timeout)
            self.logger.info("Search results loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load search results: {e}")
            self.take_screenshot(f"error_results_load_{self.datetime_helper.get_filename_timestamp()}.png")
            raise

    def get_results_count(self) -> int:
        """Get the number of search results with error handling"""
        try:
            results = self.locate(self.SEARCH_RESULTS).all()
            count = len(results)
            self.logger.info(f"Found {count} listings")
            return count
        except Exception as e:
            self.logger.error(f"Failed to get results count: {e}")
            return 0

    def get_search_title(self):
        """Get the search results title/heading"""
        return self.get_text(self.LISTINGS_PAGE_TITLE)

    def validate_search_results(self, guests_count: int, check_in: str, check_out: str, location: str = 'Tel Aviv'):
        """Validate search results from the first listing"""
        self.logger.info("Validating search results")
        validation_results = {}
        # Check if the search results page title contains the location and number of listings
        search_title = self.get_text(self.LISTINGS_PAGE_TITLE)
        count_match = re.search(r'(\d+,?\d*)', search_title)
        # Remove commas from the number string and convert to int
        count_str = count_match.group(1).replace(',', '')
        if location in search_title and int(count_str) > 0 or 'Over' in search_title:
            self.logger.info(f"Search results count: {count_str}")
            validation_results["location"] = True
        else:
            self.logger.warning(f"{location} is not in {search_title}")
            validation_results["location"] = False

        # navigate to the first listing and check if it matches the search criteria
        first_listing_page = self.navigate_to_listing(self.locate(self.SEARCH_RESULTS).first)
        first_listing_page.wait_for_page_load()

        # Extract details
        listing_details = first_listing_page.get_reservation_card_details()

        # Check if the listing matches the search criteria
        if str(guests_count) in listing_details['guests']:
            validation_results["guests"] = True
        else:
            self.logger.warning(f"Guest count mismatch: {listing_details['guests']} vs {guests_count}")
            validation_results["guests"] = False
        # Check if the dates matches the search criteria
        if listing_details['check_in'] in check_in and listing_details['check_out'] in check_out:
            validation_results["dates"] = True
        else:
            self.logger.warning(
                f"Date mismatch: {listing_details['check_in']} vs {check_in} and {listing_details['check_out']} vs {check_out}")
            validation_results["dates"] = False

        self.logger.info(f"Validation results: {validation_results}")
        # Close the listing page

        first_listing_page.goback_to_search_results()
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
            # Instantiate the ListingPage and wait for it to load
            listing_page = ListingPage(new_page)
            self.logger.info(f"Opened listing in new tab: {new_page.url}")
            return listing_page

        except Exception as e:
            self.logger.error(f"Failed to click on listing: {e}")
            return None

    def navigate_to_listing_url(self, listing_url):
        """
        Navigate to a specific listing URL.

        Args:
            listing_url: The URL of the listing to navigate to

        Returns:
            The new page object for the listing details
        """
        self.logger.info(f"Navigating to listing URL: {listing_url}")
        self.page.goto(f'https://www.airbnb.com/{listing_url}')
        listing_page = ListingPage(self.page)
        listing_page.wait_for_page_load()
        return listing_page

    def _extract_price(self, price_text: str) -> int:
        """Extract numeric price from text with error handling"""
        try:
            # Remove any currency symbols and commas
            if 'NEW' in price_text:
                self.logger.info("Skipping new listing")
                return 0
            price_text = price_text.replace('$', '').replace(',', '').strip()
            # Extract only digits
            price_value = ''.join(filter(str.isdigit, price_text))
            if not price_value:
                self.logger.warning(f"No digits found in price text: {price_text}")
                return 0
            return int(price_value)

        except Exception as e:
            self.logger.warning(f"Failed to extract price from '{price_text}': {e}")
            return 0

    def _extract_rating_and_reviews(self, rating_text: str) -> tuple[float, int]:
        """Extract rating and review count from text with error handling"""
        try:
            parts = rating_text.split(" ")
            rating = float(parts[0])
            reviews = int(parts[1].strip("()")) if len(parts) > 1 and "(" in parts[1] else 0
            return rating, reviews
        except Exception as e:
            self.logger.warning(f"Failed to extract rating from '{rating_text}': {e}")
            return 0.0, 0

    def _extract_listing_details(self, listing) -> Dict:
        """Extract all details from a listing element with error handling"""
        try:
            name = self._get_element_text(listing, self.TITLE_ELEMENT)
            description = self._get_element_text(listing, self.DESCRIPTION_ELEMENT)
            
            rating_elem = listing.locator(self.RATING_ELEMENT).first
            rating_text = rating_elem.text_content().strip() if rating_elem.is_visible() else "0"
            rating, reviews = self._extract_rating_and_reviews(rating_text)
            
            price_elem = listing.locator(self.PRICE_ELEMENT).first
            price_text = price_elem.text_content().strip() if price_elem.is_visible() else "0"
            price = self._extract_price(price_text)

            return {
                "name": name,
                "description": description,
                "rating": rating,
                "reviews": reviews,
                "price": price,
            }
        except Exception as e:
            self.logger.error(f"Failed to extract listing details: {e}")
            return {
                "name": "N/A",
                "description": "N/A",
                "rating": 0.0,
                "reviews": 0,
                "price": 0,
            }

    def _get_element_text(self, parent, selector: str, timeout: int = 1000) -> str:
        """Safely get text from an element with timeout"""
        try:
            element = parent.locator(selector).first
            if element.is_visible(timeout=timeout):
                return element.text_content().strip()
            return "N/A"
        except Exception:
            return "N/A"

    def _iterate_listings_on_all_pages(self) -> Generator:
        """Generator that yields listing locators from all result pages with improved error handling"""
        self._current_page = 1
        self._processed_listings = set()

        while True:
            try:
                self.logger.info(f"Processing page {self._current_page}")
                self.wait_for_element(self.locate(self.SEARCH_RESULTS).first)
                
                # Get all listings on current page
                page_listings = self.locate(self.SEARCH_RESULTS).all()
                self.logger.info(f"Found {len(page_listings)} listings on page {self._current_page}")

                # Yield each listing that hasn't been processed
                for listing in page_listings:
                    listing_id = listing.get_attribute("id") or str(hash(str(listing)))
                    if listing_id not in self._processed_listings:
                        self._processed_listings.add(listing_id)
                        yield listing

                # Check for next page
                if not self._has_next_page():
                    break

                self._current_page += 1
                self._navigate_to_next_page()

            except Exception as e:
                self.logger.error(f"Error processing page {self._current_page}: {e}")
                break

    def _has_next_page(self) -> bool:
        """Check if there is a next page available"""
        try:
            next_button = self.locate(self.NEXT_PAGE_BUTTON).first
            return next_button.is_visible(timeout=5000)
        except Exception:
            return False

    def _navigate_to_next_page(self):
        """Navigate to the next page of results"""
        try:
            next_button = self.locate(self.NEXT_PAGE_BUTTON).first
            # Wait for navigation to complete after clicking
            with self.page.expect_navigation(wait_until="domcontentloaded"):
                next_button.click()
            # Wait for search results to be visible on the new page
            self.wait_for_element(self.locate(self.SEARCH_RESULTS).first)
        except Exception as e:
            self.logger.error(f"Failed to navigate to next page: {e}")
            raise

    def get_listing_url(self, listing):
        """
        Extract and return the URL from the given listing element.
        Assumes that the listing element contains an <a> tag.
        """
        try:
            anchor = listing.locator("a").first
            url = anchor.get_attribute("href")
            return url
        except Exception as e:
            self.logger.warning(f"Error retrieving listing URL: {e}")
            return None

    def _navigate_to_first_page(self):
        """Navigate to the first page of results"""
        try:
            first_page_link = self.page.get_by_role("link", name="1").first
            if first_page_link.is_visible(timeout=5000):
                with self.page.expect_navigation(wait_until="domcontentloaded"):
                    first_page_link.click()
                self.wait_for_element(self.locate(self.SEARCH_RESULTS).first)
            return True
        except Exception as e:
            self.logger.error(f"Error navigating to first page: {e}")
            return False

    def get_highest_rated_listing(self) -> Optional[Dict]:
        """Find the listing with the highest rating, prioritizing more reviews"""
        self.logger.info("Looking for highest-rated listing")
        highest_rating = -1.0
        most_reviews = -1
        best_details = None
        current_page = 1
        
        def process_listing(listing):
            nonlocal highest_rating, most_reviews, best_details
            rating_elem = listing.locator(self.RATING_ELEMENT).first
            if not rating_elem.is_visible(timeout=5000):
                return None

            rating_text = rating_elem.text_content().strip()
            if 'NEW' in rating_text:
                self.logger.info("Skipping new listing")
                return None

            rating, reviews = self._extract_rating_and_reviews(rating_text)
            if (rating > highest_rating) or (rating == highest_rating and reviews > most_reviews):
                highest_rating = rating
                most_reviews = reviews
                details = self._extract_listing_details(listing)
                details["url"] = self.get_listing_url(listing)
                best_details = details
                self.logger.info(f"New best candidate found: Rating={rating}, Reviews={reviews}")
            return None

        while True:
            self.logger.info(f"Processing page {current_page}")
            self.wait_for_element(self.locate(self.SEARCH_RESULTS).first)
            listings = self._load_page_content()
            self.logger.info(f"Found {len(listings)} listings on page {current_page}")
            
            self._process_page_listings(listings, process_listing)
            
            if not self._navigate_to_page(current_page + 1):
                break
            current_page += 1

        self.logger.info(f"Final highest rated listing: rating={highest_rating}, reviews={most_reviews}")
        return best_details

    def get_cheapest_listing(self) -> Optional[Dict]:
        """Find the listing with the lowest price"""
        self.logger.info("Looking for cheapest listing")
        lowest_price = float('inf')
        cheapest_details = None
        current_page = 1
        self._navigate_to_first_page()
        #show first page url for validation
        self.logger.info('First page url:')
        self.logger.info(self.page.url)
        self.logger.info(f"Processing page {current_page}")

        def process_listing(listing):
            nonlocal lowest_price, cheapest_details
            try:
                self.logger.info("Attempting to process listing price")
                price_elem = listing.locator(self.PRICE_ELEMENT).first
                if not price_elem.is_visible(timeout=10000):
                    self.logger.warning("Price element not visible after 5 seconds")
                    return None

                price_text = price_elem.text_content().strip()
                self.logger.info(f"Raw price text found: '{price_text}'")
                if not price_text:
                    self.logger.warning("Empty price text after stripping")
                    return None

                price = self._extract_price(price_text)
                self.logger.info(f"Extracted price: {price} from text: {price_text}")
                if price <= 0:
                    self.logger.warning(f"Invalid price extracted: {price}")
                    return None

                if price < lowest_price:
                    lowest_price = price
                    details = self._extract_listing_details(listing)
                    details["url"] = self.get_listing_url(listing)
                    cheapest_details = details
                    self.logger.info(f"New lowest price found: {price}")
            except Exception as e:
                self.logger.warning(f"Error processing listing price: {e}")
            return None

        while True:
            self.logger.info(f"Processing page {current_page}")
            self.wait_for_element(self.locate(self.SEARCH_RESULTS).first)
            listings = self._load_page_content()
            self.logger.info(f"Found {len(listings)} listings on page {current_page}")
            
            self._process_page_listings(listings, process_listing)
            
            if not self._navigate_to_page(current_page + 1):
                break
            current_page += 1

        if lowest_price == float('inf'):
            self.logger.warning("No valid prices found in any listing")
            return None

        self.logger.info(f"Final cheapest listing: price={lowest_price}")
        return cheapest_details

    def save_results_to_file(self, highest_rated_listing_details, cheapest_card_listing):
        """Save the highest rated and cheapest listings to a file"""
        # Create temp directory if it doesn't exist
        os.makedirs("temp", exist_ok=True)
        try:
            today_date = self.datetime_helper.get_timestamp().replace(":", "-")
            results = {
            "search_url": self.page.url,
            "search_title": self.get_search_title(),
            "timestamp":today_date,


            "highest_rated": highest_rated_listing_details,
            "cheapest": cheapest_card_listing
            }
            filename = f"temp/cheapest_and_highest_rated_details_{today_date}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved cheapest and highest rated results to {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"Error saving results to file: {e}")
            raise

    def _process_page_listings(self, listings, process_func):
        """Process listings on a page using the provided function"""
        for listing in listings:
            try:
                result = process_func(listing)
                if result:
                    return result
            except Exception as e:
                self.logger.warning(f"Error processing listing: {e}")
                continue
        return None

    def _navigate_to_page(self, page_number):
        """Navigate to a specific page number"""
        try:
            next_page_link = self.page.get_by_role("link", name=str(page_number)).first
            if not next_page_link.is_visible(timeout=5000):
                self.logger.info("No more pages available")
                return False

            with self.page.expect_navigation(wait_until="domcontentloaded"):
                next_page_link.click()
            self.wait_for_element(self.locate(self.SEARCH_RESULTS).first)
            return True
        except Exception as e:
            self.logger.error(f"Error navigating to page {page_number}: {e}")
            return False

    def _load_page_content(self):
        """Load all content on the current page"""
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        self.page.wait_for_timeout(2000)
        return self.locate(self.SEARCH_RESULTS).all()
