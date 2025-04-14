import os
from dotenv import load_dotenv


class AppSettings:
    """
    Application settings for the test automation framework.
    Loads configuration from .env file and provides access methods.
    """
    # Load environment variables
    load_dotenv()

    # Basic settings
    BASE_URL = os.getenv("BASE_URL", "https://www.airbnb.com")
    HEADLESS = os.getenv("HEADLESS", "True").lower() == "true"
    SLOWMO = int(os.getenv("SLOWMO", "50"))
    TIMEOUT = int(os.getenv("TIMEOUT", "30000"))

    # Browser settings
    BROWSER_VIEWPORT_WIDTH = int(os.getenv("BROWSER_VIEWPORT_WIDTH", "1920"))
    BROWSER_VIEWPORT_HEIGHT = int(os.getenv("BROWSER_VIEWPORT_HEIGHT", "1080"))
    RECORD_VIDEO = os.getenv("RECORD_VIDEO", "false").lower() == "true"
    BROWSER_ARGS = os.getenv("BROWSER_ARGS", "").split(",") if os.getenv("BROWSER_ARGS") else []

    # Test data
    USER_PHONE = os.getenv("PHONE_NUMBER")


    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def get_browser_launch_options(cls):
        """Returns browser launch options for Playwright"""
        return {
            "headless": cls.HEADLESS,
            "slow_mo": cls.SLOWMO,
            "args": cls.BROWSER_ARGS if cls.BROWSER_ARGS else None,
        }

    @classmethod
    def get_context_options(cls):
        """Returns browser context options for Playwright"""
        return {
            "viewport": {
                "width": cls.BROWSER_VIEWPORT_WIDTH,
                "height": cls.BROWSER_VIEWPORT_HEIGHT,
            },
            "record_video_dir": "temp/videos/" if cls.RECORD_VIDEO else None,
        }