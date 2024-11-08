import os

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from undetected_chromedriver import ChromeOptions, Chrome as UCChrome
from pyautogui import alert

from modules.helpers import (
    critical_error_log,
    print_lg,
)
from modules.settings import Settings


def find_default_profile_directory() -> str | None:
    """
    Function to search for Chrome Profiles within default locations
    """
    default_locations = ["%LOCALAPPDATA%/Google/Chrome/User Data"]
    for location in default_locations:
        profile_dir = os.path.expandvars(location)
        if os.path.exists(profile_dir):
            return profile_dir
    return None


try:
    settings = Settings()

    # Function to set up WebDriver options
    def setup_webdriver_options() -> ChromeOptions:
        options = ChromeOptions() if settings.stealth_mode else Options()
        return options

    # Function to configure user profile
    def configure_user_profile(options: ChromeOptions):
        if settings.safe_mode:
            print_lg("SAFE MODE: Will login with a guest profile; browsing history will not be saved.")
            return

        profile_dir = find_default_profile_directory()
        if profile_dir:
            options.add_argument(f"--user-data-dir={profile_dir}")
        else:
            print_lg("Default profile directory not found. Logging in with a guest profile.")

    # Function to initialize the WebDriver
    def initialize_webdriver(options: ChromeOptions):
        # driver_executable_path="C:/Users/Ewerton/Downloads/chromedriver.exe"
        return UCChrome(options=options) if settings.stealth_mode else Chrome(options=options)

    # Main logic
    options = setup_webdriver_options()
    configure_user_profile(options)

    driver = initialize_webdriver(options)
    driver.maximize_window()

    # Additional WebDriver setup
    wait = WebDriverWait(driver, 5)
    actions = ActionChains(driver)

except Exception as e:
    # Enhanced error handling
    error_message = "An error occurred while initializing the browser."
    if isinstance(e, TimeoutError):
        error_message = "Couldn't download Chrome Driver. Set stealth_mode = False in config!"

    print_lg(error_message)
    critical_error_log("In Opening Chrome", e)
    alert(error_message, "Error in opening Chrome")

    try:
        driver.quit()
    except NameError:
        exit()
