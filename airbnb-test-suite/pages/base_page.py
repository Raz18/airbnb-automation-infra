import os
from playwright.sync_api import Page
from utils.date_time_helper import DateTimeHelper
from utils.logger import setup_logger

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.logger = setup_logger(self.__class__.__name__)
        self.datetime_helper = DateTimeHelper()


    def navigate_to(self, url):
        self.logger.info(f"Navigating to {url}")
        self.page.goto(url)

    def get_by_role(self, role, name=None, exact=False):
        self.logger.info(f"Getting element by role: {role}, name: {name}, exact: {exact}")
        return self.page.get_by_role(role, name=name, exact=exact)

    def navigate_back(self):
        self.logger.info(f"Navigating to the previous page")
        self.page.go_back()

    def click_element(self, element, retries=3,click_count=1):
        """
           Click an element using either a CSS selector or a Playwright Locator, with retry logic. """
        for attempt in range(1, retries + 1):
            try:
                if isinstance(element, str):
                    # Click using a CSS selector
                    self.logger.info(
                        f"Attempting to click element by selector: {element} (Attempt {attempt}/{retries})")
                    self.page.click(element,click_count=click_count)
                else:
                    # Click using a Locator
                    self.logger.info(f"Attempting to click element by locator: {element} (Attempt {attempt}/{retries})")
                    element.click(click_count=click_count)
                return  # Exit if click is successful
            except Exception as e:
                self.logger.error(f"Click attempt {attempt} failed: {e}")
                if attempt == retries:
                    self.logger.error(f"All {retries} attempts to click element failed. Taking a screenshot.")
                    raise

    def write_on_element(self, element, string_to_write):
        try:
            if isinstance(element, str):
                self.logger.info(f"Writing on element by selector: {element}")
                self.page.fill(element, string_to_write)
            else:
                self.logger.info(f"Writing on Locator: {element}")
                element.fill(string_to_write)
        except Exception as e:
            self.logger.error(f"Failed to write on element: {e}")

    def locate(self, selector):
        self.logger.info(f"Getting locator for selector: {selector}")
        return self.page.locator(selector)

    def wait_for(self, element, timeout=10000):
        self.logger.info(f"Waiting for element to appear: {element}")
        try:
            if isinstance(element, str):
                self.page.wait_for_selector(element, state="visible", timeout=timeout)
            else:
                element.wait_for(state="visible", timeout=timeout)
        except Exception as e:
            self.logger.error(f"Failed to wait for element: {e}")
            raise

    def is_text_visible(self, text):
        self.logger.info(f"Checking if text '{text}' is visible on the page.")
        try:
            locator = self.locate(f"text={text}")
            return locator.is_visible()
        except Exception as e:
            self.logger.error(f"Error while checking text visibility: {e}")
            return False

    def get_text(self, element):
        try:
            if isinstance(element, str):
                self.logger.info(f"Retrieving text from element by selector: {element}")
                return self.page.locator(element).text_content()
            else:
                self.logger.info(f"Retrieving text from element by Locator: {element}")
                return element.text_content()
        except Exception as e:
            self.logger.error(f"Failed to retrieve text: {e}")
            raise

    def take_screenshot(self, filename):
        default_screenshot_dir = "screenshots"
        if not os.path.exists(default_screenshot_dir):
            os.makedirs(default_screenshot_dir)

        path = os.path.join(default_screenshot_dir, filename)
        self.logger.info(f"Taking screenshot: {path}")
        self.page.screenshot(path=path)