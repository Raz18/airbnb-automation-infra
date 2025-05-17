# pages/listing_page.py (Refactored)

import re
import os
import json
from typing import Dict, Optional, Any, Union, List
from playwright.sync_api import Page, Locator, expect, Error
from datetime import datetime

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
    TRANSLATION_POPUP = 'translation-announce-modal'  #
    RESERVE_BUTTON_TEXT = 'Reserve'  # Text used for get_by_role

    # Reservation card locators (User-Provided)
    # NOTE: Selectors using specific classes like _1avmy66, _1k1ce2w, u1y3vocb are brittle
    TOTAL_PRICE = 'div[class="_1avmy66"]'  # Container for total price
    PER_NIGHT_PRICE = "._1k1ce2w"  # Container/element for per-night price
    PER_NIGHT_PRICE_SPAN_CLASS = 'u1y3vocb'  # Specific class within per-night price
      # Often contains fee breakdown
    CHECKIN_DATE = '[data-testid="change-dates-checkIn"]'  # Check-in date display
    CHECKOUT_DATE = '[data-testid="change-dates-checkOut"]'  # Check-out date display
    GUEST_COUNT = "#GuestPicker-book_it-trigger"  # Guest count display/trigger

    # Fee breakdown locators (User-Provided)
    # NOTE: Selectors using specific classes like _1n7cvm7, _14omvfj, _18x3iiu, _1k4xcdh are brittle
    PRICE_BREAKDOWN_CONTAINER = 'div._1n7cvm7' 
    PRICE_ROW = 'div._14omvfj'  # Row within fee breakdown
    ROW_DESCRIPTION = 'span._18x3iiu'  # Description part of a fee row
    ROW_AMOUNT = 'span._1k4xcdh, span._1rc8xn5'  # Amount part of a fee row
    TOTAL_PRICE_SPAN = "span._1qs94rc"  # Specific span often holding total price text
    ACCESSIBLE_PRICE = '.a8jt5op'  # Hidden accessibility span for price

    # Reservation confirmation locators (User-Provided)
    RESERVATION_CARD_DETAILS = 'div[data-testid="payments-application"]'  # Container for confirm step
    RESERVATION_TOTAL_PRICE_SPAN_CLASS = 'div[data-testid="price-item-total"] span'  # Specific class for total price on confirm page
    RESERVATION_GUEST_LABEL = 'div[data-section-id="GUEST_PICKER"]'  # Text label near guest info
    RESERVATION_DATES_LABEL = 'div[data-section-id="DATE_PICKER"]'
    EDIT_DATES_BUTTON = 'button[data-testid="checkout_platform.DATE_PICKER.edit"]'
    CHECKIN_INPUT = '#checkIn-book_it'  # Input field for check-in date
    CHECKOUT_INPUT = '#checkOut-book_it'  # Input field for check-out date

    # Phone number input (User-Provided)
    PHONE_NUMBER_INPUT = '[data-testid="login-signup-phonenumber"]'  #
    PHONE_NUMBER_CONFIRMATION_TEXT = "Confirm your number"  # Text for visibility check
    CONTINUE_BUTTON = 'button[data-testid="signup-login-submit-btn"]' # Continue button after phone entry
    POPUP_PHONE_VERIFICATION = 'div[role="dialog"]'  

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

    def _close_translation_popup_if_present(self, timeout_ms: int = 5000):
        """Checks for and closes the translation popup using its locator."""
        self.logger.info("Checking for translation popup...")
        #self.page.wait_for_timeout(3000)
        # Updated selector to match new popup structure
        popup_locator = self.page.get_by_test_id(self.TRANSLATION_POPUP)
        try:
            # Wait longer for the popup to appear
            if popup_locator.is_visible(timeout=timeout_ms):
                self.logger.info("Translation popup detected, attempting to close it...")
                try:
                    # Try to find and click the close button using aria-label
                    close_button = popup_locator.get_by_role("button", name="Close")
                    if close_button.is_visible(timeout=2000):
                        self.click_element(close_button, timeout=2000)
                        self.logger.info("Translation popup closed using close button.")
                        return
                except Error:
                    self.logger.debug("Close button not found, trying alternative methods...")                        
                # Last resort: click on the right side of the page
                try:
                    self.logger.info("Attempting to click on the right side of the page to dismiss popup...")
                    # Click on the right side of the viewport (80% from left edge)
                    self.page.mouse.click(int(self.page.viewport_size["width"] * 0.8), self.page.viewport_size["height"] // 2)
                    self.logger.info("Clicked right side of page to dismiss popup")
                except Exception as e:
                    self.logger.warning(f"Failed to click right side of page: {e}")
                    
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
        """Extracts only digits from a string and handles rounding."""
        if not text:
            return None
        try:
            # Remove currency symbols, commas, and any non-digit characters
            cleaned_text = text.replace('₪', '').replace(',', '').replace(' ', '')
            
            # Handle decimal portion for rounding
            if '.' in cleaned_text:
                whole_part, decimal_part = cleaned_text.split('.')
                # If decimal part is 50 or greater, round up
                if int(decimal_part) >= 50:
                    whole_part = str(int(whole_part) + 1)
                return whole_part
            
            # If no decimal point, just return the digits
            digits = ''.join(filter(str.isdigit, cleaned_text))
            return digits if digits else None
        except Exception as e:
            self.logger.warning(f"Error parsing price from '{text}': {e}")
            return None

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
        guest_text = self._extract_text_safely(self.GUEST_COUNT) 
        self.logger.info(f"Guest count: {guest_text}")
         #
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
        Validates that the reservation details on the confirmation page exactly match
        the details saved from the reservation card.
        
        Args:
            expected_details: Dictionary containing the reservation details saved from the listing page
        """
        self.logger.info("Validating reservation details on confirmation page...")
        validation_passed = True
        validation_messages = []

        # Log the expected details we're validating against
        self.logger.info("Expected reservation details from listing page:")
        for key, value in expected_details.items():
            self.logger.info(f"{key}: {value}")

        # --- Validate Total Price ---
        try:
            confirm_total_locator = self.page.locator('[data-testid="price-item-total"] span').first
            actual_price_text = self._extract_text_safely(confirm_total_locator, timeout=15000)
            actual_price_str = self._parse_price_digits(actual_price_text)
            expected_price_str = self._parse_price_digits(expected_details.get('total_price', 'N/A'))

            self.logger.info(f"Price validation - Expected: {expected_details.get('total_price')} -> {expected_price_str}")
            self.logger.info(f"Price validation - Actual: {actual_price_text} -> {actual_price_str}")

            if actual_price_str == expected_price_str:
                self.logger.info("✓ Total Price matches")
            else:
                msg = f"Total Price mismatch - Expected: '{expected_price_str}', Found: '{actual_price_str}'"
                self.logger.warning(msg)
                validation_messages.append(msg)
                validation_passed = False
        except Exception as e:
            msg = f"Failed to validate total price: {e}"
            self.logger.error(msg)
            validation_messages.append(msg)
            validation_passed = False

        # --- Validate Guests ---
        try:
            guest_section = self.page.locator('[data-section-id="GUEST_PICKER"]').first
            guest_text = guest_section.text_content()
            actual_guests_match = re.search(r'(\d+)', guest_text) if guest_text else None
            actual_guests = actual_guests_match.group(1) if actual_guests_match else "N/A"
            expected_guests = expected_details.get('guests', 'N/A')

            self.logger.info(f"Guest validation - Expected: {expected_guests}")
            self.logger.info(f"Guest validation - Actual: {actual_guests}")

            if actual_guests == expected_guests:
                self.logger.info("✓ Guest count matches")
            else:
                msg = f"Guest count mismatch - Expected: '{expected_guests}', Found: '{actual_guests}'"
                self.logger.warning(msg)
                validation_messages.append(msg)
                validation_passed = False
        except Exception as e:
            msg = f"Failed to validate guest count: {e}"
            self.logger.error(msg)
            validation_messages.append(msg)
            validation_passed = False

        # --- Validate Dates ---
        try:
            # Click edit dates button to show the date picker
            edit_dates_button = self.page.locator(self.EDIT_DATES_BUTTON).first
            self.click_element(edit_dates_button)
            self.logger.info("Clicked edit dates button")

            # Get check-in date from input value
            checkin_input = self.page.locator(self.CHECKIN_INPUT).first
            actual_checkin = checkin_input.get_attribute('value')
            expected_checkin = expected_details.get('check_in', 'N/A')

            # Get check-out date from input value
            checkout_input = self.page.locator(self.CHECKOUT_INPUT).first
            actual_checkout = checkout_input.get_attribute('value')
            expected_checkout = expected_details.get('check_out', 'N/A')

            self.logger.info(f"Date validation - Expected check-in: {expected_checkin}")
            self.logger.info(f"Date validation - Actual check-in: {actual_checkin}")
            self.logger.info(f"Date validation - Expected check-out: {expected_checkout}")
            self.logger.info(f"Date validation - Actual check-out: {actual_checkout}")
            #close the date picker
            close_button = self.page.get_by_role("button", name="Close")
            self.click_element(close_button)

            if actual_checkin == expected_checkin and actual_checkout == expected_checkout:
                self.logger.info("✓ Dates match")
            else:
                msg = f"Dates mismatch - Expected: '{expected_checkin}' - '{expected_checkout}', Found: '{actual_checkin}' - '{actual_checkout}'"
                self.logger.warning(msg)
                validation_messages.append(msg)
                validation_passed = False

        except Exception as e:
            msg = f"Failed to validate dates: {e}"
            self.logger.error(msg)
            validation_messages.append(msg)
            validation_passed = False

        # --- Final Validation Result ---
        if not validation_passed:
            self.take_screenshot(f"error_confirm_validation_{self.datetime_helper.get_filename_timestamp()}.png")
            error_message = "Reservation details validation failed:\n" + "\n".join(validation_messages)
            raise AssertionError(error_message)
        else:
            self.logger.info("✓ All reservation details match between listing and confirmation page")

    def enter_phone_number_and_validate(self, country_code: Optional[str] = None, phone_number: Optional[str] = None) -> bool:
        """
        Enters phone number and handles verification process.
        
        Args:
            country_code (Optional[str]): Country code for the phone number. If not provided, uses default.
            phone_number (Optional[str]): Phone number to enter. If not provided, uses USER_PHONE from AppSettings.
            
        Returns:
            bool: True if phone number entry and verification were successful, False otherwise.
            
        Raises:
            ValueError: If no phone number is provided or configured in AppSettings.
        """
        # Get phone number to use
        phone_number_to_use = phone_number or AppSettings.USER_PHONE
        if not phone_number_to_use:
            self.logger.error("Phone number is not provided or configured in AppSettings.")
            raise ValueError("Phone number is required for enter_phone_number.")

        # Mask phone number for logging
        masked_phone = '*' * (len(phone_number_to_use) - 3) + phone_number_to_use[-3:]
        self.logger.info(f"Attempting to enter phone number: {masked_phone}")

        try:
            # Step 1: Enter phone number
            if not self._enter_phone_number_in_field(phone_number_to_use):
                return False

            # Step 2: Click continue and handle verification
            if not self._handle_phone_verification():
                return False

            self.logger.info("Phone number entry and verification completed successfully.")
            return True

        except Exception as e:
            self.logger.error(f"Unexpected error during phone entry process: {e}")
            self.take_screenshot(f"error_phone_unexpected_{self.datetime_helper.get_filename_timestamp()}.png")
            return False

    def _enter_phone_number_in_field(self, phone_number: str) -> bool:
        """
        Enters the phone number into the input field.
        
        Args:
            phone_number (str): The phone number to enter.
            
        Returns:
            bool: True if phone number was entered successfully, False otherwise.
        """
        try:
            phone_input = self.locate(self.PHONE_NUMBER_INPUT).first
            
            # Wait for input field to be ready
            expect(phone_input, "Phone number input should be visible").to_be_visible(timeout=15000)
            expect(phone_input, "Phone number input should be editable").to_be_editable(timeout=5000)
            
            # Clear and fill the field
            phone_input.clear(timeout=5000)
            self.write_on_element(phone_input, phone_number)
            
            # Verify the value was entered correctly
            expect(phone_input).to_have_value(phone_number, timeout=3000)
            self.logger.info("Phone number entered successfully.")
            return True
            
        except Error as e:
            self.logger.error(f"Failed to enter phone number: {e}")
            self.take_screenshot(f"error_phone_fill_{self.datetime_helper.get_filename_timestamp()}.png")
            return False

    def _handle_phone_verification(self) -> bool:
        """
        Handles the phone verification process after entering the phone number.
        
        Returns:
            bool: True if verification was successful, False otherwise.
        """
        try:
            # Click continue button
            continue_button = self.locate(self.CONTINUE_BUTTON).first
            expect(continue_button, "'Continue' button should be enabled").to_be_enabled(timeout=10000)
            self.click_element(continue_button)
            self.logger.info("Clicked Continue button after entering phone.")

            # Set up mock after clicking continue
            if not self._api_mock_handler.setup_mock(self.page, "phone_verification"):
                self.logger.error("Failed to set up phone verification mock")
                return False

            # Wait for verification popup
            popup_locator = self.page.locator(self.POPUP_PHONE_VERIFICATION)
            self.wait_for_element(popup_locator, timeout=10000)
            self.logger.info("Phone verification popup appeared successfully.")
            
            return True

        except Error as e:
            self.logger.error(f"Error during phone verification: {e}")
            self.take_screenshot(f"error_phone_verification_{self.datetime_helper.get_filename_timestamp()}.png")
            return False
        finally:
            # Always clean up the mock
            self._api_mock_handler.remove_mock(self.page, "phone_verification")
