from typing import Sequence

from modules.helpers import buffer, print_lg, sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from modules.settings import Settings

settings = Settings()


# Helper Functions
def scroll_to_view(driver: WebDriver, element: WebElement, top: bool = False) -> None:
    """Scrolls an element into view."""
    script = "arguments[0].scrollIntoView({'block': 'center', 'behavior': 'instant'});"
    if top:
        script = "arguments[0].scrollIntoView();"
    driver.execute_script(script, element)


def wait_and_click(driver: WebDriver, xpath: str, timeout: float = 5.0) -> bool:
    """Waits for an element by XPath and clicks it."""
    try:
        element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
        element.click()
        buffer(settings.click_gap)
        return True
    except Exception as e:
        print_lg(f"Failed to find or click element by XPath '{xpath}': {e}")
        return False


# Click Functions
def wait_span_click(
    driver: WebDriver,
    text: str,
    timeout: float = 5.0,
    click: bool = True,
    scroll: bool = True,
    scroll_top: bool = False,
) -> WebElement | bool:
    """Waits for a <span> element by text, optionally scrolls and clicks it."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, f'.//span[normalize-space()="{text}"]'))
        )
        if scroll and isinstance(driver, WebDriver):
            scroll_to_view(driver, element, top=scroll_top)
        if click:
            element.click()
            buffer(settings.click_gap)
        return element
    except Exception as e:
        return False


def multi_select(driver: WebDriver, items: Sequence[str], timeout: float = 5.0) -> None:
    """Clicks multiple elements found by <span> text."""
    for text in items:
        wait_span_click(driver, text, timeout)


def multi_select_no_wait(driver: WebDriver, items: Sequence[str], actions: ActionChains | None = None) -> None:
    """Clicks multiple elements without waiting."""
    for text in items:
        if not wait_and_click(driver, f'.//span[normalize-space()="{text}"]'):
            if actions:
                company_search_click(driver, actions, text)
            else:
                print_lg(f"Element with text '{text}' not found.")


def toggle_boolean_button(driver: WebDriver, actions: ActionChains, label_text: str) -> None:
    """Toggles a boolean switch by finding it relative to a label."""
    try:
        fieldset = driver.find_element(By.XPATH, f'.//h3[normalize-space()="{label_text}"]/ancestor::fieldset')
        switch = fieldset.find_element(By.XPATH, './/input[@role="switch"]')
        scroll_to_view(driver, switch)
        actions.move_to_element(switch).click().perform()
        buffer(settings.click_gap)
    except Exception as e:
        print_lg(f"Failed to toggle switch labeled '{label_text}': {e}")


# Find Functions
def try_xp(driver: WebDriver, xpath: str, click: bool = True) -> WebElement | bool:
    try:
        if click:
            driver.find_element(By.XPATH, xpath).click()
            return True
        else:
            return driver.find_element(By.XPATH, xpath)
    except (NoSuchElementException, StaleElementReferenceException):
        return False


def try_linkText(driver: WebDriver, linkText: str) -> WebElement | bool:
    try:
        return driver.find_element(By.LINK_TEXT, linkText)
    except (NoSuchElementException, StaleElementReferenceException):
        return False


def find_by_class(driver: WebDriver, class_name: str, timeout: float = 5.0) -> WebElement:
    """Finds an element by class name, with wait."""
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))


def try_find_by_classes(driver: WebDriver, classes: list[str]) -> WebElement | ValueError:
    for cla in classes:
        try:
            return driver.find_element(By.CLASS_NAME, cla)
        except (NoSuchElementException, StaleElementReferenceException):
            pass
    raise ValueError("Failed to find an element with given classes")


# Text Input Functions
def text_input_by_id(driver: WebDriver, element_id: str, value: str, timeout: float = 5.0) -> None:
    """Inputs text by element ID, selecting existing text first."""
    element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID, element_id)))
    element.send_keys(Keys.CONTROL + "a")
    element.send_keys(value)


def company_search_click(driver: WebDriver, actions: ActionChains, company_name: str) -> None:
    """Searches for and selects a company by name in a dropdown."""
    if wait_and_click(driver, './/input[@placeholder="Add a company"]'):
        search_input = driver.find_element(By.XPATH, "(.//input[@placeholder='Add a company'])[1]")
        search_input.send_keys(Keys.CONTROL + "a")
        search_input.send_keys(company_name)
        buffer(3)
        actions.send_keys(Keys.DOWN).send_keys(Keys.ENTER).perform()
        print_lg(f"Attempted to add company '{company_name}'")


def text_input(actions: ActionChains, element: WebElement | None, value: str, field_name: str = "Text") -> None:
    """Inputs text into a WebElement and confirms with Enter."""
    if element:
        sleep(1)
        element.clear()
        element.send_keys(value.strip())
        sleep(2)
        actions.send_keys(Keys.ENTER).perform()
    else:
        print_lg(f"{field_name} input element not provided.")
