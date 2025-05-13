# pages/listing_page.py (Refactored)

import re
import os
import json
from typing import Dict, Optional, Any, Union, List
from playwright.sync_api import Page, Locator, expect, Error

# Assuming BasePage is correctly imported and provides helpers
from pages.base_page import BasePage  #
# Assuming AppSettings provides USER_PHONE etc.
from config.app_settings import AppSettings  #
from utils.api_mocks import APIMockHandler


class ListingPage(BasePage):
    """
    Page Object for the individual Airbnb Listing Details page.

    Handles extracting details from the reservation card, initiating reservation,
    and validating details on the confirmation step, using only user-defined locators.
    """
    # --- Locators (User-Provided) ---
    LISTING_PAGE = 'div[class="_88xxct"]'  # Main page container check
    LISTING_TITLE = 'div[class="_1czgyoo"]'  # Specific class for title
    TRANSLATION_POPUP = '[data-testid="translation-announce-modal"]'  #
    RESERVE_BUTTON_TEXT = 'Reserve'  # Text used for get_by_role

    # Reservation card locators (User-Provided)
    # NOTE: Selectors using specific classes like _1avmy66, _1k1ce2w, u1y3vocb are brittle
    TOTAL_PRICE = 'div[class="_1avmy66"]'  # Container for total price
    PER_NIGHT_PRICE = "._1k1ce2w"  # Container/element for per-night price
    PER_NIGHT_PRICE_SPAN_CLASS = 'u1y3vocb'  # Specific class within per-night price
    PRICE_SUMMARY = 'div[class="_1n7cvm7"]'  # Often contains fee breakdown
    CHECKIN_DATE = '[data-testid="change-dates-checkIn"]'  # Check-in date display
    CHECKOUT_DATE = '[data-testid="change-dates-checkOut"]'  # Check-out date display
    GUEST_COUNT = "#GuestPicker-book_it-trigger"  # Guest count display/trigger

    # Fee breakdown locators (User-Provided)
    # NOTE: Selectors using specific classes like _1n7cvm7, _14omvfj, _18x3iiu, _1k4xcdh are brittle
    PRICE_BREAKDOWN_CONTAINER = 'div._1n7cvm7'  # Same as PRICE_SUMMARY?
    PRICE_ROW = 'div._14omvfj'  # Row within fee breakdown
    ROW_DESCRIPTION = 'span._18x3iiu'  # Description part of a fee row
    ROW_AMOUNT = 'span._1k4xcdh, span._1rc8xn5'  # Amount part of a fee row
    TOTAL_PRICE_SPAN = "span._1qs94rc"  # Specific span often holding total price text
    ACCESSIBLE_PRICE = '.a8jt5op'  # Hidden accessibility span for price

    # Reservation confirmation locators (User-Provided)
    RESERVATION_CARD_DETAILS = 'div[data-testid="payments-application"]'  # Container for confirm step
    RESERVATION_TOTAL_PRICE_SPAN_CLASS = 'span._j1kt73'  # Specific class for total price on confirm page
    RESERVATION_GUEST_LABEL = 'Guests'  # Text label near guest info
    RESERVATION_DATES_LABEL = 'Dates'  # Text label near date info

    # Phone number input (User-Provided)
    PHONE_NUMBER_INPUT = '[data-testid="login-signup-phonenumber"]'  #
    PHONE_NUMBER_CONFIRMATION_TEXT = "Confirm your number"  # Text for visibility check
    CONTINUE_BUTTON = '[data-testid="checkout-button"]'  # Continue button after phone entry

    def __init__(self, page: Page):
        super().__init__(page)
        self._current_details: Optional[Dict[str, Any]] = None
        self._api_mock_handler = APIMockHandler()
        # Logger is initialized in BasePage

    def wait_for_page_load(self, timeout: int = 20000):
        """Waits for the main listing page container (LISTING_PAGE) to be visible."""
        self.logger.info("Waiting for Listing Details Page to load...")
        try:
            self._close_translation_popup_if_present()
            listing_page_locator = self.locate(self.LISTING_PAGE).first  #
            self.wait_for_element(listing_page_locator, timeout=timeout)  # Wait for the main container
            self.logger.info("Listing Details Page loaded.")
              #
        except Exception as e:
            self.logger.error(f"Error waiting for Listing Details page: {e}")
            self.take_screenshot(f"error_listing_load_{self.datetime_helper.get_filename_timestamp()}.png")  #
            raise

    def _close_translation_popup_if_present(self, timeout_ms: int = 3000):
        """Checks for and closes the translation popup using its locator."""
        popup_locator = self.locate(self.TRANSLATION_POPUP)
        try:
            if popup_locator.is_visible(timeout=timeout_ms):
                self.logger.info("Translation popup detected, closing it...")
                # Assume close button is standard within this data-testid modal
                close_button = popup_locator.get_by_role("button", name="Close")
                self.click_element(close_button, timeout=timeout_ms)  #
                self.logger.info("Translation popup closed.")
        except Error:
            self.logger.debug("Translation popup not found or already closed.")
        except Exception as e:
            self.logger.warning(f"Non-timeout error trying to close translation popup: {e}")

    def goback_to_search_results(self):
        """Navigate back to the search results page by closing the current tab."""
        # Note: This approach relies on the test context having exactly two pages.
        self.logger.info("Closing current listing tab to return to search results")
        try:
            context = self.page.context
            all_pages = context.pages
            current_page = self.page
            current_page.close()

            if len(all_pages) > 1:
                search_results_page = [p for p in all_pages if p != current_page][0]
                self.page = search_results_page
                self.logger.info("Switched back to search results page")
            else:
                self.logger.error("No search results page found to switch back to")

        except Exception as e:
            self.logger.error(f"Error during goback_to_search_results: {e}")
            self.take_screenshot(f"error_goback_{self.datetime_helper.get_filename_timestamp()}.png")  #
            raise

    # --- Detail Extraction Helpers ---

    def _extract_text_safely(self, element: Union[str, Locator], timeout: int = 3000) -> Optional[str]:
        """Safely extracts text content from the first matching element/locator."""
        try:
            locator = self.locate(element) if isinstance(element, str) else element
            # Use wait_for_element for consistent logging and error handling
            self.wait_for_element(locator, state="visible", timeout=timeout)  #
            text = locator.first.text_content(timeout=timeout)
            return text.strip() if text else None
        except Error as e:
            # Logged within wait_for_element or text_content failure
            self.logger.warning(f"Could not get text for element '{element}' within {timeout}ms. Error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error extracting text from '{element}': {e}")
            return None

    def _parse_price_digits(self, text: Optional[str]) -> Optional[str]:
        """Extracts only digits from a string."""
        if not text: return None
        digits = ''.join(filter(str.isdigit, text))
        return digits if digits else None

    def _extract_listing_title(self) -> str:
        """Extract the listing title using LISTING_TITLE locator."""
        return self._extract_text_safely(self.LISTING_TITLE) or "N/A"  #

    def _extract_per_night_price(self) -> str:
        """Extract per-night price using user-provided locators."""
        # Locate the main container once
        try:
            per_night_price_element = self.locate(self.PER_NIGHT_PRICE)
            if not per_night_price_element:
                return "N/A"

            # First try to get the accessible text which has the complete price
            accessible_text = self.get_text(per_night_price_element.locator(self.ACCESSIBLE_PRICE))

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

    def _extract_total_price(self) -> str:
        """Extract total price using user-provided locators."""
        # Locate the main container once
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

    def _extract_fee_breakdown(self) -> Dict[str, str]:
        """Extract fee breakdown details using user-provided locators."""
        # Assumes fees are directly visible within PRICE_BREAKDOWN_CONTAINER
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

    def _extract_check_in_date(self) -> str:
        """Extract check-in date using CHECKIN_DATE locator."""
        return self._extract_text_safely(self.CHECKIN_DATE) or "N/A"  #

    def _extract_check_out_date(self) -> str:
        """Extract check-out date using CHECKOUT_DATE locator."""
        return self._extract_text_safely(self.CHECKOUT_DATE) or "N/A"  #

    def _extract_guest_count(self) -> str:
        """Extract guest count using GUEST_COUNT locator."""
        # Using the specific ID provided
        guest_text = self._extract_text_safely(self.GUEST_COUNT)  #
        if guest_text:
            # Extract the first number found
            guests_match = re.search(r'(\d+)', guest_text)
            if guests_match:
                return guests_match.group(1)
            self.logger.warning(f"Could not find number in guest text: '{guest_text}'")
        return "N/A"

    # --- Main Action Methods ---

    def get_reservation_card_details(self) -> Dict[str, Any]:
        """
        Extracts all details displayed on the reservation card using defined helpers.
        """
        self.logger.info("Extracting all reservation card details...")
        self.wait_for_page_load()  # Ensure page is ready

        details = {
            'name': self._extract_listing_title(),
            'per_night_price': self._extract_per_night_price(),
            'total_price': self._extract_total_price(),
            'fee_breakdown': self._extract_fee_breakdown(),
            'check_in': self._extract_check_in_date(),
            'check_out': self._extract_check_out_date(),
            'guests': self._extract_guest_count()
        }

        self.logger.info(f"Finished extracting card details: {details}")
        return details

    def save_reservation_details_to_file(self, details: Dict[str, Any]):
        """Saves extracted reservation details to a timestamped JSON file."""
        temp_dir = os.path.join("temp", "reservation_details")  # Subdirectory
        os.makedirs(temp_dir, exist_ok=True)

        # Add timestamp using helper
        details['fetch_timestamp'] = self.datetime_helper.get_timestamp("%Y-%m-%dT%H:%M:%S")  #
        file_timestamp = self.datetime_helper.get_filename_timestamp()  #

        # Sanitize listing name for filename
        listing_name = details.get('name', 'UnknownListing')
        safe_listing_name = re.sub(r'[^\w\-]+', '_', listing_name)[:50]  # Limit length and invalid chars

        filename = os.path.join(temp_dir, f"reservation_{safe_listing_name}_{file_timestamp}.json")

        try:
            # Use utf-8 encoding, ensure_ascii=False to preserve characters like currency symbols if needed
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(details, f, indent=4, ensure_ascii=False)
            self.logger.info(f"Saved reservation details to {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"Failed to save reservation details to {filename}: {e}")
            return None

    def click_reserve_button(self):
        """Clicks the main 'Reserve' button identified by its text."""
        self.logger.info(f"Attempting to click the '{self.RESERVE_BUTTON_TEXT}' button...")  # [cite: 3]
        self.wait_for_page_load()
        try:
            # Use get_by_role with the defined text constant
            reserve_button = self.get_by_role("button", name=self.RESERVE_BUTTON_TEXT).first  # [cite: 3]
            self.click_element(reserve_button)  # Uses BasePage click with retry [cite: 1]
            self.logger.info(f"Clicked '{self.RESERVE_BUTTON_TEXT}'. Waiting for confirmation step...")  # [cite: 3]
            # Wait for the confirmation container using its locator [cite: 3]
            self.wait_for_element(self.RESERVATION_CARD_DETAILS, timeout=30000)  # [cite: 3]
            self.logger.info("Confirmation/Payment step container loaded.")
        except Error as e:
            self.logger.error(f"Error clicking reserve or waiting for confirmation step: {e}")
            self.take_screenshot(
                f"error_post_reserve_load_{self.datetime_helper.get_filename_timestamp()}.png")  # [cite: 1]
            raise

    def validate_details_on_confirmation(self, expected_details: Dict[str, Any]):
        """
        Validates key details on the 'Confirm and pay' step using user-provided locators.
        Note: Validation scope is limited by the available defined locators.
        Raises AssertionError on failure.
        """
        self.logger.info("Validating details on the confirmation step...")
        validation_passed = True
        validation_messages = []

        # --- Validate Total Price ---
        try:
            # Use the specific class defined by user for total price on confirm page [cite: 3]
            # NOTE: Class _j1kt73 is likely unstable [cite: 3]
            confirm_total_locator = self.locate(f"span.{self.RESERVATION_TOTAL_PRICE_SPAN_CLASS}").first  # [cite: 3]
            actual_price_text = self._extract_text_safely(confirm_total_locator, timeout=15000)
            actual_price_str = self._parse_price_digits(actual_price_text)
            expected_price_str = expected_details.get('total_price')  # Should be digits

            if actual_price_str == expected_price_str:
                self.logger.info(
                    f"Confirmation Total Price: MATCH (Expected: {expected_price_str}, Found: {actual_price_str})")
            else:
                msg = f"Confirmation Total Price MISMATCH. Expected: '{expected_price_str}', Found: '{actual_price_str}'"
                self.logger.warning(msg)
                validation_messages.append(msg)
                validation_passed = False
        except Exception as e:
            msg = f"Could not validate confirmation total price using locator '{self.RESERVATION_TOTAL_PRICE_SPAN_CLASS}': {e}"  # [cite: 3]
            self.logger.error(msg)
            validation_messages.append(msg)
            validation_passed = False

        # --- Validate Guests (Attempt using Label) ---
        # NOTE: This validation relies on finding the value near the label text.
        # The structure is assumed and may not be reliable without specific locators.
        try:
            guest_value = self._find_value_near_label(self.RESERVATION_GUEST_LABEL)  # [cite: 3]
            actual_guests_match = re.search(r'(\d+)', guest_value) if guest_value else None
            actual_guests = actual_guests_match.group(1) if actual_guests_match else "N/A"
            expected_guests = expected_details.get('guests', 'N/A')

            if actual_guests == expected_guests:
                self.logger.info(f"Confirmation Guests: MATCH (Expected: {expected_guests}, Found: {actual_guests})")
            else:
                msg = f"Confirmation Guests MISMATCH. Expected: '{expected_guests}', Found: '{actual_guests}' (from text near label)"
                self.logger.warning(msg)
                validation_messages.append(msg)
                validation_passed = False
        except Exception as e:
            msg = f"Could not validate confirmation guests near label '{self.RESERVATION_GUEST_LABEL}': {e}"  # [cite: 3]
            self.logger.error(msg)
            validation_messages.append(msg)
            validation_passed = False  # Mark as fail if check couldn't be done reliably

        # --- Validate Dates (Attempt using Label) ---
        # Similar challenge as Guests.
        try:
            date_value = self._find_value_near_label(self.RESERVATION_DATES_LABEL)  # [cite: 3]
            expected_check_in = expected_details.get('check_in', 'N/A')
            expected_check_out = expected_details.get('check_out', 'N/A')

            # Simple check if expected dates are substrings of the displayed text
            if date_value and expected_check_in in date_value and expected_check_out in date_value:
                self.logger.info(
                    f"Confirmation Dates: MATCH (Found '{expected_check_in}' and '{expected_check_out}' in '{date_value}')")
            else:
                msg = f"Confirmation Dates MISMATCH. Expected: '{expected_check_in}' - '{expected_check_out}', Found: '{date_value}'"
                self.logger.warning(msg)
                validation_messages.append(msg)
                validation_passed = False
        except Exception as e:
            msg = f"Could not validate confirmation dates near label '{self.RESERVATION_DATES_LABEL}': {e}"  # [cite: 3]
            self.logger.error(msg)
            validation_messages.append(msg)
            validation_passed = False

        # --- Add other validations if locators were provided (e.g., for Title, Cleaning Fee) ---
        # Example placeholder:
        # if self.CONFIRM_LISTING_TITLE: # Check if locator constant exists
        #     try:
        #         # ... validation logic using self.CONFIRM_LISTING_TITLE ...
        #     except Exception as e: ...

        # --- Final Assertion ---
        if not validation_passed:
            self.take_screenshot(
                f"error_confirm_validation_{self.datetime_helper.get_filename_timestamp()}.png")  # [cite: 1]
            error_message = "Validation failed on confirmation page:\n" + "\n".join(validation_messages)
            raise AssertionError(error_message)
        else:
            self.logger.info("All attempted confirmation details validated successfully.")

    def _find_value_near_label(self, label_text: str, timeout: int = 5000) -> Optional[str]:
        """Helper to find text content presumably following a text label."""
        # This is brittle and depends heavily on DOM structure.
        self.logger.debug(f"Attempting to find value near label: '{label_text}'")
        try:
            # Find the label text itself
            label_locator = self.page.locator(f"text='{label_text}'").first
            expect(label_locator).to_be_visible(timeout=timeout)
            # Attempt to find the value in common sibling/parent patterns using XPath
            # This looks for a div sibling OR a div sibling of the parent that contains text
            value_locator = label_locator.locator(
                "xpath=./following-sibling::div | ../div[string-length(normalize-space(.))>0 and not(self::*[contains(text(),'" + label_text + "')]) ]").first
            if value_locator.is_visible(timeout=1000):
                return value_locator.text_content(timeout=1000).strip()
            self.logger.warning(f"Could not find value element near label '{label_text}' using common patterns.")
            return None
        except Exception as e:
            self.logger.warning(f"Error finding value near label '{label_text}': {e}")
            return None

    def enter_phone_number(self, country_code: Optional[str] = None, phone_number: Optional[str] = None) -> bool:
        """
        Enters phone number using user-provided locators and AppSettings.
        Includes route interception logic from original code.
        Returns True if successful up to clicking Continue (if enabled).
        """
        phone_number_to_use = phone_number or AppSettings.USER_PHONE
        if not phone_number_to_use:
            self.logger.error("Phone number is not provided or configured in AppSettings.")
            raise ValueError("Phone number is required for enter_phone_number.")

        # Mask phone number in logs
        masked_phone = '*' * (len(phone_number_to_use) - 3) + phone_number_to_use[-3:]
        self.logger.info(f"Attempting to enter phone number: {masked_phone}")

        phone_input = self.locate(self.PHONE_NUMBER_INPUT).first
        try:
            # Wait for the input field to be visible and editable
            expect(phone_input, "Phone number input should be visible").to_be_visible(timeout=15000)
            expect(phone_input, "Phone number input should be editable").to_be_editable(timeout=5000)
        except Error as e:
            self.logger.error(f"Phone number input '{self.PHONE_NUMBER_INPUT}' not visible/editable: {e}")
            self.take_screenshot(f"error_phone_input_visibility_{self.datetime_helper.get_filename_timestamp()}.png")
            return False

        # Fill the phone number
        try:
            # Clear the field first in case there's pre-filled data
            phone_input.clear(timeout=5000)
            self.write_on_element(phone_input, phone_number_to_use)
            self.logger.info("Phone number entered.")
            # Optional: Verify the value entered
            expect(phone_input).to_have_value(phone_number_to_use, timeout=3000)
        except Error as e:
            self.logger.error(f"Failed to write or verify phone number: {e}")
            self.take_screenshot(f"error_phone_fill_{self.datetime_helper.get_filename_timestamp()}.png")
            return False

        try:
            # Set up phone verification mock
            if not self._api_mock_handler.setup_mock(self.page, "phone_verification"):
                self.logger.error("Failed to set up phone verification mock")
                return False

            # Click continue button using its data-testid locator
            continue_button = self.locate(self.CONTINUE_BUTTON).first
            expect(continue_button, "'Continue' button should be enabled").to_be_enabled(timeout=10000)
            self.click_element(continue_button)
            self.logger.info("Clicked Continue button after entering phone.")

            self.logger.info("Phone number entry and continue click successful.")
            return True

        except Error as e:
            self.logger.error(f"Error during phone continue/validation step: {e}")
            self.take_screenshot(f"error_phone_continue_{self.datetime_helper.get_filename_timestamp()}.png")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during phone continue step: {e}")
            self.take_screenshot(f"error_phone_unexpected_{self.datetime_helper.get_filename_timestamp()}.png")
            return False
        finally:
            # Clean up the mock
            self._api_mock_handler.remove_mock(self.page, "phone_verification")
