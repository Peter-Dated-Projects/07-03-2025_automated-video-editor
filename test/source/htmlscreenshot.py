from playwright.sync_api import sync_playwright


# ------------------------------------------------------------------------ #
# utils
# ------------------------------------------------------------------------ #


def grab_website_screenshot(url: str, dimensions: tuple, filepath: str, full_page: bool = False):
    """
    Create a Playwright context with stealth settings.
    """
    # check type for dimensions
    if not isinstance(dimensions, tuple) or len(dimensions) != 2:
        raise ValueError("Dimensions must be a tuple of (width, height)")

    # start Playwright context
    with sync_playwright() as p:
        browsers = p.chromium.launch(headless=True)

        # create stealth context
        s_context = browsers.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            viewport={"width": dimensions[0], "height": dimensions[1]},
            java_script_enabled=True
        )
        
        # create page
        page = s_context.new_page()
        
        # remove webdriver property, set optional language, set optional plugins
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page.add_init_script("Object.defineProperty(navigator, 'language', {get: () => 'en-US'})")
        page.add_init_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]})")

        # request page
        page.goto(url, wait_until="networkidle")

        # grab screenshot
        page.screenshot(path=filepath, full_page=full_page)

        # close + clean
        browsers.close()






# ------------------------------------------------------------------------ #
# main function
# ------------------------------------------------------------------------ #

if __name__ == "__main__":
    
    _sample_link = "https://www.reddit.com/r/AITAH/comments/1ehlrdd/my_husband_gave_me_a_warning_tap_and_i_called_it/"
    _dimensions = (1280, 720)
    _output_path = "reddit_screenshot.png"

    grab_website_screenshot(_sample_link, _dimensions, _output_path)
