from pages.home_page import HomePage

def test_first_case(page):
    """
    Test that verifies searching for Tel Aviv apartments for 2 adults and analyzes results.
    
    Steps:
    1. Search for apartments in Tel Aviv with 2 adults and selected dates
    2. Validate search parameters are reflected in results
    3. Find the highest-rated listing and cheapest listing
    4. Save results to file for review
    """
    # 1. Set up search with required parameters
    home_page = HomePage(page)
    home_page.wait_for_home_page()
    
    # Configure search parameters
    home_page.search_for_location("Tel Aviv")
    check_in, check_out = home_page.select_dates()
    home_page.select_guests(adults_num=2)
    
    # Execute search
    search_results_page = home_page.search()
    search_results_page.wait_for_results()
    
    # 2. Verify search returned valid results
    assert search_results_page.get_results_count() > 0, "No results found"
    
    # Validate result filters match our search criteria
    validation_status = search_results_page.validate_search_results(
        adults=2, 
        check_in_date=check_in, 
        check_out_date=check_out
    )
    assert all(validation_status.values()), f"Search validation failed: {validation_status}"
    
    # 3. Analyze results to find best options
    highest_rated_listing = search_results_page.get_highest_rated_listing()
    cheapest_listing = search_results_page.get_cheapest_listing()
    
    # 4. Save results to temp directory for review
    search_results_page.save_results_to_file(highest_rated_listing, cheapest_listing)







