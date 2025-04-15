import pytest
from config.app_settings import AppSettings


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
    """Create a page shared across all tests in the session"""
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
    print(f"\n----- Running test: {test_name} -----")
    yield
    print(f"----- Completed test: {test_name} -----\n")