import os
import pytest
from config.app_settings import AppSettings
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture(scope="session")
def browser_type_launch_args():
    """Return browser launch arguments from settings"""
    return AppSettings.get_browser_launch_options()


@pytest.fixture(scope="session")
def browser_context_args():
    """Return browser context arguments from settings"""
    return AppSettings.get_context_options()


@pytest.fixture(scope="function")
def page(browser, browser_context_args):
    """Create a page shared across all tests. function scoped"""
    context = browser.new_context(**browser_context_args)
    page = context.new_page()
    page.set_default_timeout(AppSettings.TIMEOUT)
    page.goto(AppSettings.BASE_URL)

    yield page
    # Close context after all tests in the session
    context.close()


@pytest.fixture(scope="function", autouse=True)
def test_info(request):
    """Log test information"""
    test_name = request.node.name
    print("\n" + "="*50)
    print("TEST STARTED - RAZSA DEBUG PRINT")
    print(f'RAW_HEADLESS: {os.getenv("HEADLESS")}')
    print(f"HEADLESS: {AppSettings.HEADLESS}")
    print("="*50 + "\n", flush=True)
    yield
    print("\n" + "="*50)
    print(f"TEST COMPLETED: {test_name}")
    print("="*50 + "\n", flush=True)



    
    # rest of your test...