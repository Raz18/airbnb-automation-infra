import re

from playwright.sync_api import expect
from pages.base_page import BasePage
import os
import json
from datetime import datetime
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
    PRICE_SUMMARY = 'div[class="_1n7cvm7"]'
    CHECKIN_DATE = '[data-testid="change-dates-checkIn"]'
    CHECKOUT_DATE = '[data-testid="change-dates-checkOut"]'
    GUEST_COUNT = "#GuestPicker-book_it-trigger"

    # Reservation confirmation locators
    RESERVATION_CARD_DETAILS = 'div[data-testid="payments-application"]'
    RESERVATION_TOTAL_PRICE = '[data-testid="price-item-total"]'
    RESERVATION_GUEST_COUNT = 'Guests'
    RESERVATION_DATES = 'Dates'

    PHONE_NUMBER_INPUT = '[data-testid="login-signup-phonenumber"]'
    PHONE_NUMBER_CONFIRMATION="Confirm your number"
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

    def get_reservation_details(self):
        """Extracts reservation details, including title, price, dates, and guest count."""
        self.logger.info("Extracting reservation details")
        details = {}

        # Extract the listing title
        listing_name = self.get_text(self.locate(self.LISTING_TITLE))
        details['name'] = listing_name.strip() if listing_name else "N/A"

        # Extract per-night price using our dedicated locator
        per_night_price_element = self.locate(self.PER_NIGHT_PRICE)
        if per_night_price_element:
            raw_price = self.get_text(per_night_price_element)
            # Clean up the price format to match "318 ₪" and ensure only one instance is shown
            cleaned_price = ''.join(filter(str.isdigit, raw_price))
            details['per_night_price'] = f"{cleaned_price[:len(cleaned_price)//2]} ₪" if len(cleaned_price) > 0 else "N/A"
        else:
            details['per_night_price'] = "N/A"

        # Extract total price details
        total_price_raw = self.get_text(self.locate(self.TOTAL_PRICE))
        if total_price_raw:
            total_value = total_price_raw.replace("Total", "").strip()
            # Clean up the total price format
            details['total_price'] = f"{''.join(filter(str.isdigit, total_value))} ₪"
        else:
            details['total_price'] = "N/A"

        # Extract check-in and check-out dates
        checkin = self.get_text(self.locate(self.CHECKIN_DATE))
        details['check_in'] = checkin.strip() if checkin else "N/A"
        checkout = self.get_text(self.locate(self.CHECKOUT_DATE))
        details['check_out'] = checkout.strip() if checkout else "N/A"

        # Extract guest count
        guests = self.get_text(self.locate(self.GUEST_COUNT))
        guests_number = re.search(r'(\d+)', guests).group(1) if guests else "N/A"
        details['guests'] = guests_number.strip()

        self.logger.info(f"Extracted details: {details}")
        print(f"Extracted details: {details}")
        return details

    def save_reservation_details_to_file(self, details):
        """Save reservation details to a JSON file in the 'temp' folder."""
        os.makedirs("temp", exist_ok=True)
        details['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Filename uses the listing title and timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Clean all string fields in the details dictionary to remove non-breaking spaces
        for key, value in details.items():
            if isinstance(value, str):
                details[key] = value.encode("ascii", "ignore").decode("ascii")

        filename = f"temp/reservation_details_{details['title']}_reservation_details_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(details, f, indent=2)
        self.logger.info(f"Saved reservation details to {filename}")
        return filename

    def reserve_and_validate_reservation_details(self, details:dict):
        """Clicks the Reserve button to initiate the reservation process."""
        self.logger.info("Clicking the Reserve button")
        reserve_button = self.get_by_role(role='button', name=self.RESERVE_BUTTON)
        if not reserve_button.is_visible():
            self.logger.warning("Reserve button not visible")
        self.click_element(reserve_button)
        self.logger.info("Clicked Reserve button; now on the reservation confirmation page")
        self.wait_for(self.locate(self.RESERVATION_CARD_DETAILS))
        self.logger.info("Waiting for reservation card details to load")
        for key,item in details.items():
            print(f"Key: {key}, Item: {item}")
        # Validate reservation details

    def enter_phone_number(self):
        """Enter the user's phone number in the input field."""
        self.logger.info("Entering phone number")
        phone_number = AppSettings.USER_PHONE
        self.write_on_element(self.locate(self.PHONE_NUMBER_INPUT), phone_number)
        self.logger.info(f"Entered phone number: {phone_number}")
        self.click_element(self.get_by_role("button", name="Continue"))
        self.logger.info("Clicked Continue button")
        return self.locate(self.PHONE_NUMBER_CONFIRMATION)







