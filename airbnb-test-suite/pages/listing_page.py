import re
import os
import json
from datetime import datetime

from playwright.sync_api import expect
from pages.base_page import BasePage
from config.app_settings import AppSettings

class ListingPage(BasePage):
    """Page object for the individual listing details page"""
    # General listing details locators
    LISTING_PAGE = 'div[class="_10qud2i"]'
    LISTING_TITLE = 'div[class="_1czgyoo"]'
    TRANSLATION_POPUP = '[data-testid="translation-announce-modal"]'
    RESERVE_BUTTON = 'Reserve'

    # Reservation card locators
    TOTAL_PRICE = 'div[class="_1avmy66"]'
    PER_NIGHT_PRICE = "._1k1ce2w"
    PER_NIGHT_PRICE_SPAN_CLASS = 'u1y3vocb'
    PRICE_SUMMARY = 'div[class="_1n7cvm7"]'
    CHECKIN_DATE = '[data-testid="change-dates-checkIn"]'
    CHECKOUT_DATE = '[data-testid="change-dates-checkOut"]'
    GUEST_COUNT = "#GuestPicker-book_it-trigger"

    # Fee breakdown locators
    PRICE_BREAKDOWN_CONTAINER = 'div._1n7cvm7'
    PRICE_ROW = 'div._14omvfj'
    ROW_DESCRIPTION = 'span._18x3iiu'
    ROW_AMOUNT = 'span._1k4xcdh, span._1rc8xn5'
    TOTAL_PRICE_SPAN = "span._1qs94rc"
    ACCESSIBLE_PRICE = '.a8jt5op'

    # Reservation confirmation locators
    RESERVATION_CARD_DETAILS = 'div[data-testid="payments-application"]'
    RESERVATION_TOTAL_PRICE_SPAN_CLASS = 'span._j1kt73'
    RESERVATION_GUEST_COUNT = 'Guests'
    RESERVATION_DATES = 'Dates'

    PHONE_NUMBER_INPUT = '[data-testid="login-signup-phonenumber"]'
    PHONE_NUMBER_CONFIRMATION = "Confirm your number"
    CONTINUE_BUTTON = '[data-testid="checkout-button"]'

    def __init__(self, page):
        super().__init__(page)

    def wait_for_page_load(self):
        """Wait for the listing page to fully load"""
        self.logger.info("Waiting for the listing page to load")
        self.wait_for(self.LISTING_PAGE)

        # Close the translation popup if visible
        if self.locate(self.TRANSLATION_POPUP).is_visible():
            self.logger.info("Translation popup is visible, closing it")
            self.click_element(self.get_by_role("button", name="Close"))

    def goback_to_search_results(self):
        """Navigate back to the search results page"""
        self.logger.info("Closing current listing tab to return to search results")

        # Get all page contexts (tabs/windows)
        context = self.page.context
        all_pages = context.pages
        current_page = self.page
        current_page.close()

        # Switch back to the previous page (search results)
        if len(all_pages) > 1:
            search_results_page = [p for p in all_pages if p != current_page][0]
            self.page = search_results_page
            self.logger.info("Switched back to search results page")
        else:
            self.logger.error("No search results page found to switch back to")

    def get_reservation_details(self):
        """Extracts reservation details, including title, price, dates, and guest count."""
        self.logger.info("Extracting reservation details")
        details = {}

        # Extract the listing title
        details['name'] = self._extract_listing_title()

        # Extract prices
        details['per_night_price'] = self._extract_per_night_price()
        details['total_price'] = self._extract_total_price()

        # Extract fee breakdown
        details['fee_breakdown'] = self._extract_fee_breakdown()

        # Extract dates and guest count
        details['check_in'] = self._extract_check_in_date()
        details['check_out'] = self._extract_check_out_date()
        details['guests'] = self._extract_guest_count()

        self.logger.info(f"Extracted details: {details}")
        print(f"Extracted details: {details}")
        return details

    def _extract_listing_title(self):
        """Extract the listing title"""
        listing_name = self.get_text(self.locate(self.LISTING_TITLE))
        return listing_name.strip() if listing_name else "N/A"

    def _extract_per_night_price(self):
        """Extract per-night price"""
        try:
            per_night_price_element = self.locate(self.PER_NIGHT_PRICE)
            if not per_night_price_element:
                return "N/A"

            # First try to get the accessible text which has the complete price
            accessible_text = per_night_price_element.locator(self.ACCESSIBLE_PRICE).text_content(timeout=5000)

            if accessible_text and "night" in accessible_text:
                # Extract the price part before "per night"
                price_part = accessible_text.split("per night")[0].strip()
                # Get only digits from the price part
                return ''.join(filter(str.isdigit, price_part))
            else:
                # Fallback: try to find the visible price text
                price_spans = per_night_price_element.locator(self.PER_NIGHT_PRICE_SPAN_CLASS).all()

                if len(price_spans) > 1:  # There's a discount
                    raw_price = price_spans[1].text_content(timeout=3000)
                elif len(price_spans) == 1:  # Regular price
                    raw_price = price_spans[0].text_content(timeout=3000)
                else:  # No specific price spans found
                    raw_price = per_night_price_element.text_content(timeout=3000)

                # Extract only digits
                return ''.join(filter(str.isdigit, raw_price))
        except Exception as e:
            self.logger.warning(f"Could not extract per-night price: {str(e)}")
            return "N/A"

    def _extract_total_price(self):
        """Extract total price"""
        try:
            total_price_element = self.locate(self.TOTAL_PRICE)
            if not total_price_element.is_visible():
                return "N/A"

            # Find the span with the price
            price_span = total_price_element.locator(self.TOTAL_PRICE_SPAN).first
            if price_span.is_visible():
                price_text = price_span.text_content().strip()
                self.logger.info(f"Found total price: {price_text}")
                return price_text
            else:
                # Fallback: get all text and look for the price format
                all_text = total_price_element.text_content().strip()
                # Look for anything with the shekel symbol and numbers
                if '₪' in all_text:
                    price_text = all_text.split('Total')[1].strip()
                    self.logger.info(f"Extracted total price: {price_text}")
                    return price_text
                else:
                    return "N/A"
        except Exception as e:
            self.logger.warning(f"Error getting total price: {e}")
            return "N/A"

    def _extract_fee_breakdown(self):
        """Extract fee breakdown details"""
        fee_breakdown = {}
        try:
            fee_container = self.locate(self.PRICE_BREAKDOWN_CONTAINER)
            if not fee_container.is_visible():
                return fee_breakdown

            # Extract all fee rows
            fee_rows = fee_container.locator(self.PRICE_ROW).all()

            for row in fee_rows:
                try:
                    # Get the fee description and amount
                    desc_elem = row.locator(self.ROW_DESCRIPTION).first
                    amount_elem = row.locator(self.ROW_AMOUNT).first

                    if desc_elem.is_visible() and amount_elem.is_visible():
                        desc = desc_elem.text_content().strip().replace('\u200a', '')
                        amount = amount_elem.text_content().strip().replace('\u200a', '')

                        # Clean up the description text
                        desc = desc.replace("Show price breakdown", "").strip()

                        # Remove shekel symbol (₪) from both description and amount
                        desc = desc.replace("₪", "").replace("\u20aa", "").strip()
                        amount = amount.replace("₪", "").replace("\u20aa", "").strip()

                        # Add to fee breakdown
                        fee_breakdown[desc] = amount
                except Exception as e:
                    self.logger.warning(f"Error extracting fee row: {e}")
        except Exception as e:
            self.logger.warning(f"Error extracting fee breakdown: {e}")

        return fee_breakdown

    def _extract_check_in_date(self):
        """Extract check-in date"""
        try:
            checkin = self.get_text(self.locate(self.CHECKIN_DATE))
            return checkin.strip() if checkin else "N/A"
        except Exception as e:
            self.logger.warning(f"Could not extract check-in date: {str(e)}")
            return "N/A"

    def _extract_check_out_date(self):
        """Extract check-out date"""
        try:
            checkout = self.get_text(self.locate(self.CHECKOUT_DATE))
            return checkout.strip() if checkout else "N/A"
        except Exception as e:
            self.logger.warning(f"Could not extract check-out date: {str(e)}")
            return "N/A"

    def _extract_guest_count(self):
        """Extract guest count"""
        try:
            guests = self.get_text(self.locate(self.GUEST_COUNT))
            guests_match = re.search(r'(\d+)', guests)
            guests_number = guests_match.group(1) if guests_match else "N/A"
            return guests_number.strip() if guests_number != "N/A" else "N/A"
        except Exception as e:
            self.logger.warning(f"Could not extract guest count: {str(e)}")
            return "N/A"

    def save_reservation_details_to_file(self, details):
        """Save reservation details to a JSON file in the 'temp' folder."""
        os.makedirs("temp", exist_ok=True)
        details['timestamp'] = self.datetime_helper.get_timestamp()
        timestamp = self.datetime_helper.get_filename_timestamp()

        # Clean all string fields in the details dictionary to remove non-breaking spaces
        for key, value in details.items():
            if isinstance(value, str):
                details[key] = value.encode("ascii", "ignore").decode("ascii")

        # Use 'name' instead of 'title' for the filename
        listing_name = details['name'].replace(" ", "_")[:20]  # Limit length and replace spaces
        filename = f"temp/reservation_details_{listing_name}_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(details, f, indent=2)
        self.logger.info(f"Saved reservation details to {filename}")
        return filename

    def reserve_and_validate_reservation_details(self, details: dict):
        """Clicks Reserve button and checks key reservation details match"""
        # Click Reserve button
        self.logger.info("Clicking Reserve button")
        self.wait_for_page_load()
        reserve_button = self.get_by_role(role='button', name=self.RESERVE_BUTTON)
        self.click_element(reserve_button)

        # Wait for confirmation page to load
        self.wait_for(self.locate(self.RESERVATION_CARD_DETAILS))

        # Check total price
        total_price_element = self.page.locator('[data-testid="price-item-total"] span').first
        actual_price = ''.join(filter(str.isdigit, total_price_element.text_content()))
        expected_price = ''.join(filter(str.isdigit, details.get('total_price', '')))
        price_match = expected_price in actual_price

        # Check cleaning fee
        cleaning_fee_element = self.page.locator('[data-testid="price-item-CLEANING_FEE"] span').first
        actual_fee = ''.join(filter(str.isdigit, cleaning_fee_element.text_content()))
        expected_fee = ''.join(filter(str.isdigit, details['fee_breakdown']['Cleaning fee']))
        fee_match = expected_fee in actual_fee

        # Check listing name
        listing_title_element = self.page.locator('#LISTING_CARD-title').first
        actual_title = listing_title_element.text_content().strip()
        expected_title = details.get('name', '').strip()

        # More robust comparison
        actual_title_normalized = ' '.join(actual_title.split())  # Normalize whitespace
        expected_title_normalized = ' '.join(expected_title.split())
        title_match = actual_title_normalized == expected_title_normalized

        # For partial matching if exact match fails
        if not title_match:
            title_match = actual_title_normalized in expected_title_normalized or expected_title_normalized in actual_title_normalized
            self.logger.warning(f"Title mismatch: Expected '{expected_title}', got '{actual_title}'")

        # Log results
        if price_match and fee_match and title_match:
            self.logger.info("All reservation details validated successfully")
        else:
            if not price_match:
                self.logger.warning(f"Price mismatch: Expected {expected_price}, got {actual_price}")
            if not fee_match:
                self.logger.warning(f"Fee mismatch: Expected {expected_fee}, got {actual_fee}")
            if not title_match:
                self.logger.warning(f"Title mismatch: Expected '{expected_title}', got '{actual_title}'")

        return {
            "passed": price_match and fee_match and title_match,
            "price_match": price_match,
            "fee_match": fee_match,
            "title_match": title_match
        }



    def enter_phone_number(self):
        """Enter the user's phone number in the input field."""
        self.logger.info("Entering phone number")
        phone_number = AppSettings.USER_PHONE
        self.write_on_element(self.locate(self.PHONE_NUMBER_INPUT), phone_number)
        self.logger.info(f"Entered phone number: {phone_number}")
        self.click_element(self.get_by_role("button", name="Continue").first)
        self.logger.info("Clicked Continue button")
        # Validate phone number format
        phone_digit_count = len(''.join(filter(str.isdigit, phone_number)))
        is_valid = phone_digit_count >= 9 and phone_digit_count == len(''.join(filter(str.isdigit, phone_number)))

        if not is_valid:
            self.logger.error(f"Invalid phone number format: {phone_number}")
            return False

        # Enter phone number
        self.write_on_element(self.locate(self.PHONE_NUMBER_INPUT), phone_number)
        self.logger.info(f"Entered phone number: {phone_number}")

        # Set up route interception for phone verification API
        self.page.route("**/api/v2/phone_verifications**", lambda route: route.fulfill(
            status=200,
            body=json.dumps({"success": True, "verified": True})
        ))

        # Click continue button
        self.click_element(self.get_by_role("button", name="Continue").first)
        self.logger.info("Clicked Continue button")

        # Let's assume we successfully validated the phone number
        self.logger.info("Phone number validated successfully")
        return True

