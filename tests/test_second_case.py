from pages.home_page import HomePage


def test_second_case(page):
    """
       Test flow:
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
    home_page.select_dates()
    home_page.select_guests(adults_num=2, kids_num=1)
    user_search = home_page.search()
    user_search.wait_for_results()
    user_params = user_search.validate_search_results()

    # Make sure what we searched for is what's showing
    assert user_search.get_results_count() > 0, "No results found"
    assert "Tel Aviv" in user_params["location"], "Wrong location in search bar"
    highest_rated = user_search.get_highest_rated_listing()
    assert highest_rated, "No listings found"
    highest_rated_page = user_search.navigate_to_listing(highest_rated)
    listing_details=highest_rated_page.get_reservation_details()
    assert listing_details, "Failed to extract reservation details"
    # Save reservation details to file
    results_file = highest_rated_page.save_reservation_details_to_file(listing_details)
    assert results_file, "Failed to save reservation details to file"
    # Attempt reservation
    highest_rated_page.reserve_and_validate_reservation_details(listing_details)
    reservation_confirmation=highest_rated_page.enter_phone_number()
    page.pause()
    assert reservation_confirmation.is_visible(), "Failed to complete reservation"





