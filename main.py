# TODO : Remove date_listed
import os
import csv
import re
import time
from random import randint
from datetime import datetime
import pyautogui

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.remote.webdriver import WebDriver

from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    NoSuchWindowException,
    ElementNotInteractableException,
)

from modules.open_chrome import driver, wait, actions
from modules.helpers import (
    make_directories,
    critical_error_log,
    print_lg,
    buffer,
    manual_login_retry,
    calculate_date_posted,
    get_inspirational_quote,
)
from modules.clickers_and_finders import (
    scroll_to_view,
    wait_span_click,
    find_by_class,
    text_input,
    try_linkText,
    try_xp,
    text_input_by_id,
    multi_select,
    multi_select_no_wait,
    toggle_boolean_button,
    try_find_by_classes,
)
from typing import Literal

from modules.settings import Settings

pyautogui.FAILSAFE = False
settings = Settings()

first_name = settings.first_name.strip()
middle_name = settings.middle_name.strip()
last_name = settings.last_name.strip()
full_name = f"{first_name} {middle_name} {last_name}"

easy_applied_count = 0
blacklisted_companies = set()

re_experience = re.compile(r"[(]?\s*(\d+)\s*[)]?\s*[-to]*\s*\d*[+]*\s*year[s]?", re.IGNORECASE)

desired_salary_monthly = str(round(settings.desired_salary / 12, 2))
desired_salary = str(settings.desired_salary)

notice_period_months = str(settings.notice_period_in_days // 30)
notice_period_weeks = str(settings.notice_period_in_days // 7)
notice_period = str(settings.notice_period_in_days)


# Login Functions
def is_logged_in_LN() -> bool:
    """
    Function to check if user is logged-in in LinkedIn
    * Returns: `True` if user is logged-in or `False` if not
    """
    if driver.current_url == "https://www.linkedin.com/feed/":
        return True

    if (
        try_linkText(driver, "Sign in")
        or try_xp(driver, '//button[@type="submit" and contains(text(), "Sign in")]')
        or try_linkText(driver, "Join now")
    ):
        return False

    print_lg("Didn't find Sign in link, so assuming user is logged in!")
    return True


def login_LN() -> None:
    """
    Function to login for LinkedIn
    * Tries to login using given `username` and `password` from `secrets.py`
    * If failed, tries to login using saved LinkedIn profile button if available
    * If both failed, asks user to login manually
    """
    # Find the username and password fields and fill them with user credentials
    driver.get("https://www.linkedin.com/login")
    try:
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Forgot password?")))
        try:
            text_input_by_id(driver, "username", settings.username, 1)
        except Exception:
            print_lg("Couldn't find username field.")

        try:
            text_input_by_id(driver, "password", settings.password, 1)
        except Exception:
            print_lg("Couldn't find password field.")

        # Find the login submit button and click it
        driver.find_element(By.XPATH, '//button[@type="submit" and contains(text(), "Sign in")]').click()
    except Exception:
        try:
            profile_button = find_by_class(driver, "profile__details")
            profile_button.click()
        except Exception:
            print_lg("Couldn't Login!")

    try:
        # Wait until successful redirect, indicating successful login
        wait.until(EC.url_to_be("https://www.linkedin.com/feed/"))
        return print_lg("Login successful!")
    except Exception:
        print_lg(
            "Seems like login attempt failed! Possibly due to wrong credentials or already logged in! Try manually!"
        )

        manual_login_retry(is_logged_in_LN, 2)


def set_search_location() -> None:
    """
    Function to set search location
    """
    if settings.search_location.strip():
        try:
            print_lg(f'Setting location to: "{settings.search_location.strip()}"...')
            search_location_ele = try_xp(
                driver,
                ".//input[@aria-label='City, state, or zip code'and not(@disabled)]",
                False,
            )
            text_input(actions, search_location_ele, settings.search_location, "Search Location")
        except ElementNotInteractableException:
            try_xp(
                driver,
                ".//label[@class='jobs-search-box__input-icon jobs-search-box__keywords-label']",
            )
            actions.send_keys(Keys.TAB, Keys.TAB).perform()
            actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
            actions.send_keys(settings.search_location.strip()).perform()
            time.sleep(2)
            actions.send_keys(Keys.ENTER).perform()
            try_xp(driver, ".//button[@aria-label='Cancel']")
        except Exception as e:
            try_xp(driver, ".//button[@aria-label='Cancel']")
            print_lg("Failed to update search location, continuing with default location!", e)


def apply_filters() -> None:
    """
    Function to apply job search filters
    """
    set_search_location()

    try:
        recommended_wait = 2

        wait.until(EC.presence_of_element_located((By.XPATH, '//button[normalize-space()="All filters"]'))).click()
        buffer(recommended_wait)

        wait_span_click(driver, settings.sort_by)
        print_lg(f"Sorting by: {settings.sort_by}")

        wait_span_click(driver, settings.date_posted)
        print_lg(f"Date posted: {settings.date_posted}")

        buffer(recommended_wait)

        multi_select(driver, settings.experience_level)
        multi_select_no_wait(driver, settings.companies, actions)
        if settings.experience_level or settings.companies:
            buffer(recommended_wait)

        multi_select(driver, settings.job_type)
        multi_select(driver, settings.on_site)
        if settings.job_type or settings.on_site:
            buffer(recommended_wait)

        toggle_boolean_button(driver, actions, "Easy Apply")

        multi_select_no_wait(driver, settings.location)
        multi_select_no_wait(driver, settings.industry)
        if settings.location or settings.industry:
            buffer(recommended_wait)

        multi_select_no_wait(driver, settings.job_function)
        multi_select_no_wait(driver, settings.job_titles)
        if settings.job_function or settings.job_titles:
            buffer(recommended_wait)

        if settings.under_10_applicants:
            toggle_boolean_button(driver, actions, "Under 10 applicants")
        if settings.in_your_network:
            toggle_boolean_button(driver, actions, "In your network")
        if settings.fair_chance_employer:
            toggle_boolean_button(driver, actions, "Fair Chance Employer")

        wait_span_click(driver, settings.salary)
        buffer(recommended_wait)

        multi_select_no_wait(driver, settings.benefits)
        multi_select_no_wait(driver, settings.commitments)
        if settings.benefits or settings.commitments:
            buffer(recommended_wait)

        show_results_button: WebElement = driver.find_element(
            By.XPATH, '//button[contains(@aria-label, "Apply current filters to show")]'
        )
        show_results_button.click()

    except Exception:
        print_lg("Setting the preferences failed!")


def get_page_info() -> tuple[WebElement | None, int | None]:
    """
    Function to get pagination element and current page number
    """
    try:
        pagination_element = try_find_by_classes(driver, ["jobs-search-pagination__pages"])
        scroll_to_view(driver, pagination_element)
        current_page = int(
            pagination_element.find_element(By.CLASS_NAME, "jobs-search-pagination__indicator-button--active").text
        )
    except Exception as e:
        print_lg("Failed to find Pagination element, hence couldn't scroll till end!")
        pagination_element = None
        current_page = None
        print_lg(e)
    return pagination_element, current_page


def get_job_main_details(
    job: WebElement, blacklisted_companies: set, driver: WebDriver
) -> tuple[str, str, str, str, str, bool, str]:
    """
    # Function to get job main details.
    Returns a tuple of (job_id, title, company, work_location, work_style, skip)
    * job_id: Job ID
    * title: Job title
    * company: Company name
    * work_location: Work location of this job
    * work_style: Work style of this job (Remote, On-site, Hybrid)
    * skip: A boolean flag to skip this job
    """
    try:
        job_details_button = job.find_element(By.CLASS_NAME, "job-card-list__title")
    except NoSuchElementException as e:
        critical_error_log("Not sure what is going on, so just skipping this job...", e)
        screenshot(driver, "Unknown", "Job Details Button")
        raise e

    scroll_to_view(driver, job_details_button, True)
    title = job_details_button.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']").text
    # title = job_details_button.text
    company = job.find_element(By.CLASS_NAME, "job-card-container__primary-description").text
    job_id = job.get_dom_attribute("data-occludable-job-id")
    work_location = job.find_element(By.CLASS_NAME, "job-card-container__metadata-item").text
    work_style = work_location[work_location.rfind("(") + 1 : work_location.rfind(")")]
    work_location = work_location[: work_location.rfind("(")].strip()
    # Skip if previously rejected due to blacklist or already applied
    reason = ""
    skip = False
    if company in blacklisted_companies:
        reason = "Blacklisted Company"
        skip = True

    try:
        if job.find_element(By.CLASS_NAME, "job-card-container__footer-job-state").text == "Applied":
            reason = "Already Applied"
            skip = True
    except Exception:
        pass

    try:
        if not skip:
            buffer(settings.click_gap)
            job_details_button.click()
    except Exception:
        reason = "Failed to click"
        skip = True
        discard_job()
        job_details_button.click()  # To pass the error outside

    buffer(settings.click_gap)
    return (job_id, title, company, work_location, work_style, skip, reason)


# Function to check for Blacklisted words in About Company
def check_blacklist(job_id: str, company: str, blacklisted_companies: set) -> tuple[set, set, WebElement] | ValueError:
    jobs_top_card = try_find_by_classes(
        driver,
        [
            "job-details-jobs-unified-top-card__primary-description-container",
            "job-details-jobs-unified-top-card__primary-description",
            "jobs-unified-top-card__primary-description",
            "jobs-details__main-content",
        ],
    )
    about_company_org = find_by_class(driver, "jobs-company__box")
    scroll_to_view(driver, about_company_org)
    about_company_org = about_company_org.text
    about_company = about_company_org.lower()
    skip_checking = False
    for word in settings.about_company_good_words:
        if word.lower() in about_company:
            print_lg(f'Found the word "{word}". So, skipped checking for blacklist words.')
            skip_checking = True
            break
    if not skip_checking:
        for word in settings.about_company_bad_words:
            if word.lower() in about_company:
                blacklisted_companies.add(company)
                raise ValueError(f'\n"{about_company_org}"\n\nContains "{word}".')
    buffer(settings.click_gap)
    scroll_to_view(driver, jobs_top_card)
    return blacklisted_companies, jobs_top_card


# Function to extract years of experience required from About Job
def extract_years_of_experience(text: str) -> int:
    # Extract all patterns like '10+ years', '5 years', '3-5 years', etc.
    matches = re.findall(re_experience, text)
    if len(matches) == 0:
        print_lg(f"\n{text}\n\nCouldn't find experience requirement in About the Job!")
        return 0
    return max([int(match) for match in matches if int(match) <= 12])


# Function to answer common questions for Easy Apply
def answer_common_questions(label: str, answer: str) -> str:
    if "sponsorship" in label or "visa" in label:
        answer = settings.require_visa
    return answer


# Function to answer the questions for Easy Apply
def answer_questions(work_location: str):
    # Get all questions from the page
    all_questions = driver.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-element")

    for Question in all_questions:
        # Check if it's a select Question
        select = try_xp(Question, ".//select", False)
        if select:
            label_org = "Unknown"
            try:
                label = Question.find_element(By.TAG_NAME, "label")
                label_org = label.find_element(By.TAG_NAME, "span").text
            except Exception:
                pass
            answer = "Yes"
            label = label_org.lower()
            select = Select(select)
            selected_option = select.first_selected_option.text
            optionsText = []
            options = '"List of phone country codes"'
            if label != "phone country code":
                optionsText = [option.text for option in select.options]
                options = "".join([f' "{option}",' for option in optionsText])
            prev_answer = selected_option
            if settings.overwrite_previous_answers or selected_option == "Select an option":
                if "email" in label or "phone" in label:
                    answer = prev_answer
                elif "gender" in label or "sex" in label:
                    answer = settings.gender
                elif "disability" in label:
                    answer = settings.disability_status
                elif "proficiency" in label:
                    answer = "Professional"
                else:
                    answer = answer_common_questions(label, answer)
                try:
                    select.select_by_visible_text(answer)
                except NoSuchElementException:
                    possible_answer_phrases = (
                        ["Decline", "not wish", "don't wish", "Prefer not", "not want"]
                        if answer == "Decline"
                        else [answer]
                    )
                    foundOption = False
                    for phrase in possible_answer_phrases:
                        for option in optionsText:
                            if phrase in option:
                                select.select_by_visible_text(option)
                                answer = f"Decline ({option})" if len(possible_answer_phrases) > 1 else option
                                foundOption = True
                                break
                        if foundOption:
                            break
                    if not foundOption:
                        print_lg(
                            f'No option with text "{answer}" for question labelled "{label_org}", answering randomly!'
                        )
                        select.select_by_index(randint(1, len(select.options) - 1))
                        answer = select.first_selected_option.text
            continue

        # Check if it's a radio Question
        radio = try_xp(
            Question,
            './/fieldset[@data-test-form-builder-radio-button-form-component="true"]',
            False,
        )
        if radio:
            prev_answer = None
            label = try_xp(
                radio,
                ".//span[@data-test-form-builder-radio-button-form-component__title]",
                False,
            )
            try:
                label = find_by_class(label, "visually-hidden", 2.0)
            except Exception:
                pass
            label_org = label.text if label else "Unknown"
            answer = "Yes"
            label = label_org.lower()

            label_org += " [ "
            options = radio.find_elements(By.TAG_NAME, "input")
            options_labels = []

            for option in options:
                id = option.get_attribute("id")
                option_label = try_xp(radio, f'.//label[@for="{id}"]', False)
                options_labels.append(
                    f'"{option_label.text if option_label else "Unknown"}"<{option.get_attribute("value")}>'
                )  # Saving option as "label <value>"
                if option.is_selected():
                    prev_answer = options_labels[-1]
                label_org += f" {options_labels[-1]},"

            if settings.overwrite_previous_answers or prev_answer is None:
                if "citizenship" in label or "employment eligibility" in label:
                    answer = settings.us_citizenship
                elif "veteran" in label or "protected" in label:
                    answer = settings.veteran_status
                elif "disability" in label or "handicapped" in label:
                    answer = settings.disability_status
                else:
                    answer = answer_common_questions(label, answer)
                foundOption = try_xp(radio, f".//label[normalize-space()='{answer}']", False)
                if foundOption:
                    actions.move_to_element(foundOption).click().perform()
                else:
                    possible_answer_phrases = (
                        ["Decline", "not wish", "don't wish", "Prefer not", "not want"]
                        if answer == "Decline"
                        else [answer]
                    )
                    ele = options[0]
                    answer = options_labels[0]
                    for phrase in possible_answer_phrases:
                        for i, option_label in enumerate(options_labels):
                            if phrase in option_label:
                                foundOption = options[i]
                                ele = foundOption
                                answer = (
                                    f"Decline ({option_label})" if len(possible_answer_phrases) > 1 else option_label
                                )
                                break
                        if foundOption:
                            break

                    actions.move_to_element(ele).click().perform()
            else:
                answer = prev_answer
            continue

        # Check if it's a text question
        text = try_xp(Question, ".//input[@type='text']", False)
        if text:
            do_actions = False
            label = try_xp(Question, ".//label[@for]", False)
            try:
                label = label.find_element(By.CLASS_NAME, "visually-hidden")
            except Exception:
                pass
            label_org = label.text if label else "Unknown"
            answer = ""  # years_of_experience
            label = label_org.lower()

            prev_answer = text.get_attribute("value")
            if not prev_answer or settings.overwrite_previous_answers:
                if "experience" in label or "years" in label:
                    answer = settings.years_of_experience
                elif "phone" in label or "mobile" in label:
                    answer = settings.phone_number
                elif "street" in label:
                    answer = settings.street
                elif "city" in label or "location" in label or "address" in label:
                    answer = settings.current_city.strip() if settings.current_city else work_location
                    do_actions = True
                elif "signature" in label:
                    answer = full_name
                elif "name" in label:
                    if "full" in label:
                        answer = full_name
                    elif "first" in label and "last" not in label:
                        answer = first_name
                    elif "middle" in label and "last" not in label:
                        answer = middle_name
                    elif "last" in label and "first" not in label:
                        answer = last_name
                    elif "employer" in label:
                        answer = settings.recent_employer
                    else:
                        answer = full_name
                elif "notice" in label:
                    if "month" in label:
                        answer = notice_period_months
                    elif "week" in label:
                        answer = notice_period_weeks
                    else:
                        answer = notice_period
                elif "salary" in label or "compensation" in label or "ctc" in label or "pay" in label:
                    if "month" in label:
                        answer = desired_salary_monthly
                    else:
                        answer = desired_salary
                elif "linkedin" in label:
                    answer = settings.linkedin
                elif "website" in label or "blog" in label or "portfolio" in label or "link" in label:
                    answer = settings.website
                elif "scale of 1-10" in label:
                    answer = settings.confidence_level
                elif "headline" in label:
                    answer = settings.headline
                elif "state" in label or "province" in label:
                    answer = settings.state
                elif "zip" in label or "postal" in label or "code" in label:
                    answer = settings.zipcode
                elif "country" in label:
                    answer = settings.country
                else:
                    answer = answer_common_questions(label, answer)
                if answer == "":
                    answer = str(settings.years_of_experience)
                text.clear()
                text.send_keys(answer)
                if do_actions:
                    time.sleep(2)
                    actions.send_keys(Keys.ARROW_DOWN)
                    actions.send_keys(Keys.ENTER).perform()
            continue

        # Check if it's a textarea question
        text_area = try_xp(Question, ".//textarea", False)
        if text_area:
            label = try_xp(Question, ".//label[@for]", False)
            label_org = label.text if label else "Unknown"
            label = label_org.lower()
            answer = str(settings.years_of_experience)  # TODO: ask ChatGPT to generate a random answer
            prev_answer = text_area.get_attribute("value")
            if not prev_answer or settings.overwrite_previous_answers:
                if "summary" in label:
                    answer = settings.summary
                elif "cover" in label:
                    answer = settings.cover_letter
                text_area.clear()
                text_area.send_keys(answer)
            continue

        # Check if it's a checkbox question
        checkbox = try_xp(Question, ".//input[@type='checkbox']", False)
        if checkbox:
            label = try_xp(Question, ".//span[@class='visually-hidden']", False)
            label_org = label.text if label else "Unknown"
            label = label_org.lower()
            answer = try_xp(
                Question, ".//label[@for]", False
            )  # Sometimes multiple checkboxes are given for 1 question, Not accounted for that yet
            answer = answer.text if answer else "Unknown"
            prev_answer = checkbox.is_selected()
            if not prev_answer:
                try:
                    actions.move_to_element(checkbox).click().perform()
                except Exception as e:
                    print_lg("Checkbox click failed!", e)
                    pass
            continue

    # Select todays date
    try_xp(driver, "//button[contains(@aria-label, 'This is today')]")


def screenshot(driver: WebDriver, job_id: str, failedAt: str) -> str:
    """
    Function to to take screenshot for debugging
    - Returns screenshot name as String
    """
    now = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    screenshot_name = f"{now} - {job_id} - {failedAt}.png"
    path = settings.logs_folder_path + "/screenshots/" + screenshot_name
    driver.save_screenshot(path.replace("//", "/"))
    return screenshot_name


def log_job(file_path: str, data: dict, fields: list[str]) -> None:
    """
    Function to log job details in a file
    """
    try:
        with open(file_path, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(data)
    except Exception as e:
        print_lg(f"Failed to update {file_path}: {e}")


def failed_job(
    job_id: str,
    job_link: str,
    date_listed,
    error: str,
    exception: Exception,
    screenshot_name: str,
) -> None:
    """
    Function to update failed jobs list in excel
    """
    fields = ["Job ID", "Job Link", "Date listed", "Date Tried", "Assumed Reason", "Stack Trace", "Screenshot Name"]
    data = {
        "Job ID": job_id,
        "Job Link": job_link,
        "Date listed": date_listed,
        "Date Tried": datetime.now(),
        "Assumed Reason": error.replace("\n", " "),
        "Stack Trace": exception.replace("\n", " "),
        "Screenshot Name": screenshot_name,
    }
    log_job(settings.failed_file_name, data, fields)


def submitted_jobs(
    job_id: str,
    job_link: str,
    date_listed: datetime | Literal["Unknown"],
    date_applied: datetime | Literal["Pending"],
    company: str,
    work_location: str,
    title: str,
    work_style: str,
    experience_required: int | Literal["Unknown", "Error in extraction"],
    description: str,
) -> None:
    """
    Function to create or update the Applied jobs CSV file, once the application is submitted successfully
    """
    fields = [
        "Job ID",
        "Job Link",
        "Date Listed",
        "Date Applied",
        "Company",
        "Work Location",
        "Title",
        "Work Style",
        "Experience required",
        "About Job",
    ]
    data = {
        "Job ID": job_id,
        "Job Link": job_link,
        "Date Listed": date_listed,
        "Date Applied": date_applied,
        "Company": company,
        "Work Location": work_location,
        "Title": title,
        "Work Style": work_style,
        "Experience required": experience_required,
        "About Job": description.replace("\r\n", " ").replace("\n", " "),
    }
    log_job(settings.file_name, data, fields)


# Function to discard the job application
def discard_job() -> None:
    print_lg("Discarding job...")
    actions.send_keys(Keys.ESCAPE).perform()
    try:
        wait_span_click(driver, "Discard", 2)
    except Exception:
        actions.send_keys(Keys.ESCAPE).perform()
        wait_span_click(driver, "Discard", 2)


# Function to apply to jobs
def apply_to_jobs(search_term: str) -> None:
    global easy_applied_count, blacklisted_companies

    driver.get(f"https://www.linkedin.com/jobs/search/?keywords={search_term}")
    print_lg(f"{"_" * 120}")

    print_lg(f"Searching for '{search_term}' jobs...")
    apply_filters()

    print_lg(f"{"_" * 120}")

    try:
        while True:
            # Wait until job listings are loaded
            wait.until(
                EC.presence_of_all_elements_located(
                    (
                        By.XPATH,
                        "//li[contains(@class, 'jobs-search-results__list-item')]",
                    )
                )
            )

            pagination_element, current_page = get_page_info()

            # Find all job listings in current page
            buffer(3)
            job_listings = driver.find_elements(By.CLASS_NAME, "jobs-search-results__list-item")

            for job in job_listings:
                print_lg()
                pyautogui.press("shiftright")  # Keep screen awake

                try:
                    job_id, title, company, work_location, work_style, skip, reason = get_job_main_details(
                        job, blacklisted_companies, driver
                    )
                except NoSuchElementException:
                    continue

                if not skip:
                    # Redundant fail safe check for applied jobs!
                    try:
                        try:
                            if (
                                "Easy Apply application limit"
                                in find_by_class(driver, "artdeco-inline-feedback__message", 2).text
                            ):
                                print_lg("Daily limit achieved! Stopping program...")
                                return
                        except Exception:
                            if find_by_class(driver, "jobs-s-apply__application-link", 2):
                                skip = True
                                reason = "Already Applied"
                    except Exception:
                        pass

                print_lg(
                    f"Job ID: {job_id} | Title: {title.replace('\n', ' ')} | Company: {company.replace('\n', ' ')}"
                )
                if skip:
                    print_lg(f"Skipping it... Reason: {reason}.")
                    continue
                else:
                    print_lg("Trying to apply...")

                job_link = "https://www.linkedin.com/jobs/view/" + job_id
                date_applied = "Pending"
                date_listed = "Unknown"
                description = "Unknown"
                experience_required = "Unknown"
                screenshot_name = "N/A"

                try:
                    blacklisted_companies, jobs_top_card = check_blacklist(job_id, company, blacklisted_companies)
                except ValueError as e:
                    print_lg("Skipping it... Reason: Blacklist")
                    failed_job(
                        job_id,
                        job_link,
                        date_listed,
                        "Found Blacklisted words in About Company",
                        str(e),
                        screenshot_name,
                    )
                    continue
                except Exception:
                    print_lg("Failed to scroll to About Company!")

                # Calculation of date posted
                try:
                    time_posted_text = jobs_top_card.find_element(
                        By.XPATH, './/span[contains(normalize-space(), " ago")]'
                    ).text
                    date_listed = calculate_date_posted(time_posted_text)
                except Exception as e:
                    print_lg("Failed to calculate the date posted!", e)

                # Get job description
                try:
                    description = find_by_class(driver, "jobs-box__html-content").text
                    descriptionLow = description.lower()
                    skip = False
                    for word in settings.bad_words:
                        if word.lower() in descriptionLow:
                            reason = f"Found a Bad Word ({word}) in About Job"
                            skip = True
                            break
                    if (
                        not skip
                        and settings.security_clearance is False
                        and (
                            "polygraph" in descriptionLow or "clearance" in descriptionLow or "secret" in descriptionLow
                        )
                    ):
                        reason = "Asking for Security clearance"
                        skip = True
                    if not skip:
                        if (
                            settings.current_experience > -1
                            and extract_years_of_experience(description) > settings.current_experience
                        ):
                            reason = "Experience required > Current Experience"
                            skip = True
                    if skip:
                        print_lg(f"Skipping it... Reason: {reason}.")
                        failed_job(
                            job_id,
                            job_link,
                            date_listed,
                            reason,
                            "Skipped",
                            screenshot_name,
                        )
                        continue
                except Exception:
                    if description == "Unknown":
                        print_lg("Unable to extract job description!")
                    else:
                        experience_required = "Error in extraction"
                        print_lg("Unable to extract years of experience required!")

                # Case 1: Easy Apply Button
                if try_xp(
                    driver,
                    ".//button[contains(@class,'jobs-apply-button') and"
                    " contains(@class, 'artdeco-button--3') and contains(@aria-label, 'Easy')]",
                ):
                    try:
                        try:
                            errored = ""
                            modal = find_by_class(driver, "jobs-easy-apply-modal")
                            wait_span_click(modal, "Next", 1)
                            next_button = True
                            next_counter = 0
                            while next_button:
                                next_counter += 1
                                if next_counter >= 30:
                                    screenshot_name = screenshot(driver, job_id, "Failed at questions")
                                    errored = "stuck"
                                    raise Exception(
                                        "Seems stuck in continuous loop of next, probably because of new questions."
                                    )
                                answer_questions(work_location)

                                try:
                                    next_button = modal.find_element(
                                        By.XPATH,
                                        './/span[normalize-space()="Review"]',
                                    )
                                except NoSuchElementException:
                                    next_button = modal.find_element(
                                        By.XPATH,
                                        './/button[contains(span, "Next")]',
                                    )
                                try:
                                    next_button.click()
                                except ElementClickInterceptedException:
                                    break
                                buffer(settings.click_gap)

                        except NoSuchElementException:
                            errored = "nose"
                        finally:
                            date_applied = datetime.now()
                            try:
                                wait_span_click(driver, "Review", 1, scroll_top=True)
                            except Exception:
                                pass

                            try:
                                wait_span_click(driver, "Submit application", 2, scroll_top=True)
                            except Exception:
                                pass

                            try:
                                wait_span_click(driver, "Done", 2)
                            except Exception:
                                print_lg("Since, Submit Application failed, discarding the job application...")
                                if errored == "nose":
                                    raise Exception("Failed to click Submit application 😑")

                    except Exception as e:
                        print_lg("Failed to Easy apply!")
                        critical_error_log("Somewhere in Easy Apply process", e)
                        failed_job(
                            job_id,
                            job_link,
                            date_listed,
                            "Problem in Easy Applying",
                            str(e),
                            screenshot_name,
                        )
                        discard_job()
                        continue

                submitted_jobs(
                    job_id,
                    job_link,
                    date_listed,
                    date_applied,
                    company,
                    work_location,
                    title,
                    work_style,
                    experience_required,
                    description,
                )

                easy_applied_count += 1
                print_lg(f"Successfully applied. Current count: {easy_applied_count}")
                actions.send_keys(Keys.ESCAPE).perform()

            # Switching to next page
            print_lg()
            if pagination_element is None:
                print_lg("Couldn't find pagination element, probably at the end page of results!")
                break
            try:
                pagination_element.find_element(By.XPATH, f"//button[@aria-label='Page {current_page + 1}']").click()
                print_lg(f"-> Now on Page {current_page + 1}")
            except NoSuchElementException:
                print_lg(f"\n>-> Didn't find Page {current_page + 1}. Probably at the end page of results!\n")
                break

    except Exception as e:
        print_lg("Failed to find Job listings!")
        critical_error_log("In Applier", e)


def main() -> None:
    try:
        # Create necessary directories
        make_directories(
            [
                settings.logs_folder_path,
                os.path.join(settings.logs_folder_path, "screenshots"),
            ]
        )

        # Login to LinkedIn
        driver.get("https://www.linkedin.com/login")
        if not is_logged_in_LN():
            login_LN()

        linkedIn_tab = driver.current_window_handle

        # Start applying to jobs
        driver.switch_to.window(linkedIn_tab)

        apply_to_jobs(settings.search_term)

    except NoSuchWindowException:
        pass
    except Exception as e:
        critical_error_log("In Applier Main", e)
        pyautogui.alert(e, "Error Occurred. Closing Browser!")
    finally:
        print_lg(f"Jobs Easy Applied: {easy_applied_count}")
        print_lg(get_inspirational_quote())


if __name__ == "__main__":
    main()
