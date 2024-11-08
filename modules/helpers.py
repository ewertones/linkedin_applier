import os
from time import sleep
from random import randint, choice
from datetime import datetime

import dateparser
from pyautogui import alert

from modules.settings import Settings

settings = Settings()


def make_directories(paths: list[str]) -> None:
    """
    Function to create missing directories
    """
    for path in paths:
        path = path.replace("//", "/")
        if "/" in path and "." in path:
            path = path[: path.rfind("/")]
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except Exception as e:
            print_lg(f'Error while creating directory "{path}": ', e)


def critical_error_log(possible_reason: str, stack_trace: Exception) -> None:
    """
    Function to log and print critical errors along with datetime stamp
    """
    print_lg(possible_reason, stack_trace)


def print_lg(*msgs: str) -> None:
    """
    Function to log and print
    """
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{now}]\t{'\n'.join(str(msg) for msg in msgs)}"
        print(message)

        path = settings.logs_folder_path + "/log.txt"
        with open(path.replace("//", "/"), "a+", encoding="utf-8") as file:
            file.write(message + "\n")

    except Exception as e:
        critical_error_log("Log.txt is open or is occupied by another program!", e)


def buffer(speed: int = 0) -> None:
    """
    Function to wait within a period of selected random range.
    * Will not wait if input `speed <= 0`
    * Will wait within a random range of
      - `0.6 to 1.0 secs` if `1 <= speed < 2`
      - `1.0 to 1.8 secs` if `2 <= speed < 3`
      - `1.8 to speed secs` if `3 <= speed`
    """
    if speed < 2:
        return sleep(randint(6, 10) * 0.1)
    elif speed <= 2 and speed < 3:
        return sleep(randint(10, 18) * 0.1)
    else:
        return sleep(randint(18, round(speed) * 10) * 0.1)


def manual_login_retry(is_logged_in: callable, limit: int = 2) -> None:
    """
    Function to ask and validate manual login
    """
    count = 0
    while not is_logged_in():
        print_lg("Seems like you're not logged in!")
        button = "Confirm Login"
        message = f'After you successfully Log In, please click "{button}" button below.'
        if count > limit:
            button = "Skip Confirmation"
            message = (
                f"If you're seeing this message even after you logged in, click '{button}'."
                "Seems like auto login confirmation failed!"
            )
        count += 1
        if alert(message, "Login Required", button) and count > limit:
            return


def calculate_date_posted(time_string: str) -> datetime:
    """Function to calculate date posted from string."""
    time_string = time_string.strip().lower()
    return dateparser.parse(time_string)


def get_inspirational_quote() -> str:
    quote = choice(
        [
            "You're one step closer than before.",
            "All the best with your future interviews.",
            "Keep up with the progress. You got this.",
            "If you're tired, learn to take rest but never give up.",
            "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill",
            "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle. - Christian D. Larson",
            "Every job is a self-portrait of the person who does it. Autograph your work with excellence.",
            "The only way to do great work is to love what you do. If you haven't found it yet, keep looking. Don't settle. - Steve Jobs",
            "Opportunities don't happen, you create them. - Chris Grosser",
            "The road to success and the road to failure are almost exactly the same. The difference is perseverance.",
            "Obstacles are those frightful things you see when you take your eyes off your goal. - Henry Ford",
            "The only limit to our realization of tomorrow will be our doubts of today. - Franklin D. Roosevelt",
        ]
    )
    return quote
