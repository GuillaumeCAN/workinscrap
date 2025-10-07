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

import threading
from rich.console import Console
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from datetime import datetime

from app.config import USER_TIME_SPENT
from app import log
from app.browser import check_login

console = Console()
idling_status = False
idling_start_time = None

def is_idling():
    return idling_status

def get_status_text():
    if idling_status and idling_start_time:
        elapsed = datetime.now() - idling_start_time
        elapsed_str = str(elapsed).split(".")[0]
        return [("class:status_green", f"  🟩 Now idling...(current session : {elapsed_str})")]
    else:
        return [("class:status_red", "  🔴 Idling stopped.")]

def toggle_idling(driver=None):
    global idling_status, idling_thread, idling_start_time
    if not idling_status:
        idling_status = True
        idling_start_time = datetime.now()
        idling_thread = threading.Thread(target=start_idling, args=(driver,), daemon=True)
        idling_thread.start()
    else:
        idling_status = False
        idling_start_time = None

def start_idling(driver):
    global idling_status
    log.info("Idle thread started...")

    try:
        while idling_status:

            if not check_login(driver):
                log.error("Connection lost! Idle thread stopped.")
                idling_status = False
                break

            try:
                driver.refresh()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, USER_TIME_SPENT))
                )
                time_spent = driver.find_element(By.XPATH, USER_TIME_SPENT).text
                log.debug(f"IDLE - Page refreshed, time spent : {time_spent}")
            except Exception as e:
                log.error(f"IDLE - ERROR: {e}")
            time.sleep(60)
    finally:
        log.info("Idle thread stopped...")
