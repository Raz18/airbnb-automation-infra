from pages.home_page import HomePage


def test_second_case(page):
    """
       Test Flow:
         - Search for apartments for 2 adults and 1 child in Tel Aviv.
         - Validate search parameters in the results.
         - Select the highest-rated result.
         - Seamlessly transition to the listing page.
         - Extract and save reservation details.
         - Attempt reservation and validate details.
       """

    home_page = HomePage(page)
    home_page.wait_for_home_page()
    home_page.search_for_location("Tel Aviv")
    check_in,check_out=home_page.select_dates()
    home_page.select_guests(adults_num=2, kids_num=1)
    user_search = home_page.search()
    user_search.wait_for_results()
    assert user_search.get_results_count() > 0, "No results found"
    # Validate search parameters
    user_params = user_search.validate_search_results(3, check_in, check_out)

    # Make sure what we searched for is what's showing
    assert all(user_params.values()), f"Validation failed: {user_params}"
    highest_rated = user_search.get_highest_rated_listing()

    highest_rated_page=user_search.navigate_to_listing_url(highest_rated['url'])
    highest_rated_page.wait_for_page_load()

    # Extract reservation details
    highest_rated_page_reservation_details=highest_rated_page.get_reservation_details()
    highest_rated_page.save_reservation_details_to_file(highest_rated_page_reservation_details)

    # Attempt reservation
    validation_resutls=highest_rated_page.reserve_and_validate_reservation_details(highest_rated_page_reservation_details)
    assert all(validation_resutls.values()), f"Validation failed: {validation_resutls}"
    #enter phone number
    assert highest_rated_page.enter_phone_number(), "Failed to validate phone number"









