
# return the main link and related routes
def get_urls():
    base_url = "https://bankofmaharashtra.in"



    urls_to_scrape = [
        "/personal-banking/loans/home-loan",
        "/personal-banking/loans/personal-loan", 
        "/educational-loans",
        "/retail-loans",
        "/online-loans",
        "/mahabank-personalloan-scheme-for-all",
        "/personal-loan-for-professionals",
        "/personal-loan-for-businessclass-having-home-loan-with-us",
        "/personal-banking/loans/car-loan",
        "/personal-banking/loans/education-loan",
        "/maha-super-housing-loan-scheme-for-construction-acquiring",
        "/maha-super-flexi-housing-loan-scheme"
    ]

    return base_url,urls_to_scrape


