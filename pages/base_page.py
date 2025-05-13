import os
from playwright.sync_api import Page, Locator, Error
from typing import Union, Optional
from utils.date_time_helper import DateTimeHelper
from utils.logger import setup_logger


class BasePage:
    """
    Base class for all Page Objects.
    Provides common browser interaction methods, logging, and helper utilities.
    """

    def __init__(self, page: Page):
        self.page = page
        # Initialize logger using the setup function from utils
        # The logger name will be the name of the subclass (e.g., "HomePage")
        self.logger = setup_logger(self.__class__.__name__)
        self.datetime_helper = DateTimeHelper()
        self.logger.info(f"{self.__class__.__name__} initialized.")

    def navigate_to(self, url: str):
        """Navigates the browser to the specified URL."""
        self.logger.info(f"Navigating to: {url}")
        try:
            self.page.goto(url, wait_until="domcontentloaded")
        except Error as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
            self.take_screenshot(f"error_navigate_{self.datetime_helper.get_filename_timestamp()}.png")
            raise

    def navigate_back(self):
        """Navigates to the previous page in the browser history."""
        self.logger.info("Navigating back to the previous page.")
        try:
            self.page.go_back(wait_until="domcontentloaded")
        except Error as e:
            self.logger.error(f"Failed to navigate back: {e}")
            self.take_screenshot(f"error_navigate_back_{self.datetime_helper.get_filename_timestamp()}.png")
            raise

    def locate(self, selector: str) -> Locator:
        """Returns a Playwright Locator for the given selector."""
        # Reduced logging verbosity here as it's called very frequently
        # self.logger.debug(f"Getting locator for selector: {selector}")
        return self.page.locator(selector)

    def get_by_role(self, role: str, name: Optional[str] = None, exact: bool = False) -> Locator:
        """Returns a Playwright Locator finding elements by ARIA role, name, and exact match."""
        self.logger.info(f"Getting element by role: '{role}', name: '{name}', exact: {exact}")
        return self.page.get_by_role(role, name=name, exact=exact)

    def click_element(self, element: Union[str, Locator], retries: int = 3, click_count: int = 1, timeout: int = 10000):
        """
        Clicks an element specified by a selector string or a Locator object, with retry logic.

        Args:
            element: CSS selector string or Playwright Locator.
            retries: Number of times to retry clicking on failure.
            click_count: Number of times to click the element (e.g., 2 for double-click).
            timeout: Maximum time in ms to wait for the element before each click attempt.
        """
        locator: Locator
        if isinstance(element, str):
            locator_description = f"selector '{element}'"
            locator = self.locate(element)
        else:
            locator_description = f"locator '{element}'"  # Note: Locator object repr might be long
            locator = element

        for attempt in range(1, retries + 1):
            try:
                self.logger.info(f"Attempting to click {locator_description} (Attempt {attempt}/{retries})")
                locator.click(click_count=click_count, timeout=timeout)
                self.logger.info(f"Successfully clicked {locator_description}")
                return  # Exit loop on success
            except Error as e:
                self.logger.warning(f"Click attempt {attempt} failed for {locator_description}: {e}")
                if attempt == retries:
                    self.logger.error(f"All {retries} click attempts failed for {locator_description}.")
                    self.take_screenshot(f"error_click_{self.datetime_helper.get_filename_timestamp()}.png")
                    raise  # Re-raise the exception after final attempt
                self.page.wait_for_timeout(500)  # Brief pause before retry

    def write_on_element(self, element: Union[str, Locator], text_to_write: str, timeout: int = 10000):
        """Fills an input element specified by selector or Locator with the given text."""
        locator: Locator
        if isinstance(element, str):
            locator_description = f"selector '{element}'"
            locator = self.locate(element)
        else:
            locator_description = f"locator '{element}'"
            locator = element

        try:
            self.logger.info(f"Filling {locator_description} with text.")
            locator.fill(text_to_write, timeout=timeout)
            self.logger.info(f"Successfully filled {locator_description}.")
        except Error as e:
            self.logger.error(f"Failed to fill {locator_description}: {e}")
            self.take_screenshot(f"error_fill_{self.datetime_helper.get_filename_timestamp()}.png")
            raise

    def wait_for_element(self, element: Union[str, Locator], state: str = "visible", timeout: int = 10000):
        """Waits for an element specified by selector or Locator to reach a specific state."""
        locator: Locator
        if isinstance(element, str):
            locator_description = f"selector '{element}'"
            locator = self.locate(element)
        else:
            locator_description = f"locator '{element}'"
            locator = element

        self.logger.info(f"Waiting for {locator_description} to be {state} (timeout: {timeout}ms)")
        try:
            locator.wait_for(state=state, timeout=timeout)
            self.logger.info(f"Element {locator_description} is now {state}.")
        except Error as e:
            self.logger.error(f"Timeout waiting for {locator_description} to be {state}: {e}")
            self.take_screenshot(f"error_wait_{state}_{self.datetime_helper.get_filename_timestamp()}.png")
            raise

    def get_text(self, element: Union[str, Locator], timeout: int = 5000) -> Optional[str]:
        """Retrieves the text content of an element specified by selector or Locator."""
        locator: Locator
        if isinstance(element, str):
            locator_description = f"selector '{element}'"
            locator = self.locate(element)
        else:
            locator_description = f"locator '{element}'"
            locator = element

        try:
            # Ensure element is visible before getting text to avoid stale element issues
            self.wait_for_element(locator, state="visible", timeout=timeout)
            text = locator.text_content(timeout=timeout)
            self.logger.debug(f"Retrieved text from {locator_description}: '{text}'")
            return text.strip() if text else None
        except Error as e:
            self.logger.error(f"Failed to retrieve text from {locator_description}: {e}")
            # Optionally take screenshot on failure
            # self.take_screenshot(f"error_get_text_{self.datetime_helper.get_filename_timestamp()}.png")
            # Decide whether to raise or return None based on expected behavior
            return None  # Return None if text cannot be retrieved

    def is_text_visible(self, text: str, timeout: int = 5000) -> bool:
        """Checks if the specific text is visible on the page."""
        self.logger.info(f"Checking visibility for text: '{text}'")
        try:
            # Use Playwright's text locator which auto-waits
            self.page.locator(f"text='{text}'").wait_for(state="visible", timeout=timeout)
            self.logger.info(f"Text '{text}' is visible.")
            return True
        except Error:
            self.logger.info(f"Text '{text}' is NOT visible within {timeout}ms.")
            return False

    def take_screenshot(self, filename: str):
        """Takes a screenshot and saves it to the configured screenshots directory."""
        # Consider moving screenshot dir path to AppSettings
        screenshot_dir = os.path.join("temp", "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        path = os.path.join(screenshot_dir, filename)
        try:
            self.page.screenshot(path=path, full_page=True)
            self.logger.info(f"Screenshot saved: {path}")
        except Error as e:
            self.logger.error(f"Failed to take screenshot {path}: {e}")
