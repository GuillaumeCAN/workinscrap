# ==============================================================================
#  This file is part of a private project and is intended for educational use only.
#  Unauthorized copying, distribution, or modification of this file, in whole or
#  in part, without explicit written permission from the author is strictly prohibited.
#
#  DISCLAIMER:
#  This program is not intended to be used for cheating, academic dishonesty,
#  or any other unethical activities. It is provided solely for learning and
#  research purposes.
#
#  © Guillaume CANCALON – All rights reserved.
# ==============================================================================

import requests
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from google import genai
from app import log
from app.config import API_KEY
from functools import lru_cache


from app.config import USER_NAME, USER_TIME_SPENT, COURSE_LIST_UL, MODULE_CARD_LIST

def get_course_list(driver=None, connected=False):
    if connected and driver is not None:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, COURSE_LIST_UL))
            )
            course_elements = driver.find_elements(By.CSS_SELECTOR, "li.activity-item")
            course_list = []
            formatted_list = []

            for course in course_elements:
                try:
                    title = course.find_element(By.CSS_SELECTOR, "span.software-title").text.strip()
                    percentage = course.find_element(By.CSS_SELECTOR, "div.circle-percent span").text.strip()
                    progress_value = course.find_element(By.CSS_SELECTOR, "div.formation-progress-value").text.strip()

                    formatted = f"{title.ljust(45, '.')} {percentage} ({progress_value})"
                    course_list.append(title)              # ← raw
                    formatted_list.append(formatted)       # ← formatted

                except NoSuchElementException:
                    continue

            return course_list, formatted_list  # ← return both

        except NoSuchElementException:
            return [], ["Error while fetching course list..."]


def get_module_list(driver=None, course_name=None, connected=False):
    if connected and driver is not None and course_name:
        try:
            course_xpath_text = escape_xpath_text(course_name)
            course_xpath = f"//span[contains(@class, 'software-title') and normalize-space(text())={course_xpath_text}]"
            log.debug(f"Selected course (xpath: {course_xpath})")

            course_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, course_xpath))
            )
            course_element.click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, MODULE_CARD_LIST))
            )

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "card-body"))
            )
            module_elements = driver.find_elements(By.CLASS_NAME, "card-body")
            modules = []

            for module in module_elements:
                try:
                    title = module.find_element(By.CSS_SELECTOR, "h3.card-title").text.strip()
                    modules.append(title)

                except NoSuchElementException:
                    continue

            return modules

        except NoSuchElementException:
            return "Error while fetching modules list..."


def get_user_name(driver=None, connected=False):
    if connected and driver is not None:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, USER_NAME))
            )
            user_name = driver.find_element(By.XPATH, USER_NAME).text
            return user_name

        except NoSuchElementException:
            return "Error while fetching user name..."

def get_user_time_spent(driver=None, connected=False):
    if connected and driver is not None:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, USER_TIME_SPENT))
            )
            time_spent = driver.find_element(By.XPATH, USER_TIME_SPENT).text
            return time_spent
        except NoSuchElementException:
            return "Error while fetching user time spent..."

def get_user_apikey():
    from app.config import API_KEY
    return bool(API_KEY)

@lru_cache(maxsize=1)
def is_api_key_valid():
    if not API_KEY:
        return False

    try:
        log.info("Checking if API key is valid...")
        client = genai.Client(api_key=API_KEY)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="ping"
        )
        log.info("API key is valid !")
        return bool(response.text)
    except Exception as e:
        log.error(f"Gemini API key test failed: {e}")
        return False

def escape_xpath_text(text: str) -> str:
    if "'" not in text:
        return f"'{text}'"
    elif '"' not in text:
        return f'"{text}"'
    else:
        parts = text.split("'")
        return "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"