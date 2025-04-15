from pages.home_page import HomePage
from pages.listing_page import ListingPage


def test_first_case(page):
    """
    Test flow:
         .	Search for Apartments: Search apartments for 2 adults in Tel Aviv with arbitrary check-in and check-out dates.
         .	Validate your search parameters in the results
         .	Analyze Results:
         .	Identify the highest-rated result.
         .	Identify the cheapest result.
         .	Log the above results details and save them to file in a “temp” folder

    """
    home_page = HomePage(page)
    home_page.wait_for_home_page()
    home_page.search_for_location("Tel Aviv")
    check_in,check_out=home_page.select_dates()
    home_page.select_guests(adults_num=2)
    user_search=home_page.search()
    user_search.wait_for_results()
    assert user_search.get_results_count() > 0, "No results found"
    validation_status=user_search.validate_search_results(2, check_in, check_out)
    assert all(validation_status.values()), f"Validation failed: {validation_status}"
    #listings_list=user_search.iterate_over_all_pages()
    highest_rated = user_search.get_highest_rated_listing()
    cheapest = user_search.get_cheapest_listing()
    user_search.save_results_to_file(highest_rated, cheapest)







