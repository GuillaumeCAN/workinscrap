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

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import tempfile, os
from rich.prompt import Prompt
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.config import LOGIN_URL, USERNAME_SELECTOR, PASSWORD_SELECTOR, SUBMIT_BUTTON_SELECTOR, SUCCESS_ELEMENT_SELECTOR

def start_browser():
    profile_dir = tempfile.mkdtemp(prefix="workinscrap_firefox_")
    options = Options()
    options.headless = True  # headless
    options.add_argument("-profile")
    options.add_argument(profile_dir)

    service = Service(log_path=os.devnull)

    driver = webdriver.Firefox(service=service, options=options)
    return driver


# ======================== LOGIN FONCTIONS ========================

def login(driver):
    username = Prompt.ask("[bold yellow]Username[/bold yellow]")
    password = Prompt.ask("[bold yellow]Password[/bold yellow]", password=True)

    driver.get(LOGIN_URL)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, USERNAME_SELECTOR))
        ).send_keys(username)

        driver.find_element(By.XPATH, PASSWORD_SELECTOR).send_keys(password)
        driver.find_element(By.XPATH, SUBMIT_BUTTON_SELECTOR).click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, SUCCESS_ELEMENT_SELECTOR))
        )

        print("✅ Login successful")
        return True

    except Exception as e:
        print("❌ Login failed")
        print(f"Error message: {e}")
        return False


def check_login(driver):
    try:
        driver.find_element(By.XPATH, SUCCESS_ELEMENT_SELECTOR)
        return True
    except NoSuchElementException:
        return False
