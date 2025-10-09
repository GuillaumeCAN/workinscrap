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

from rich.console import Console
from app.get_user import get_course_list
import threading
import time

from app import log, idle
from app.get_user import is_api_key_valid

console = Console()
scraping_status = False

def is_scraping(driver=None, connected=False):
    return scraping_status

def get_status_text():
    if scraping_status:
        return [("class:status_green", "  🟩 Now scraping..."),]
    else:
        return [("class:status_red", "  🔴 Scraping stopped.")]

def warn_status_text():
    if idle.is_idling():
        return [("class:warn", "  ⚠️  [WARN] Idle daemon is currently running.\n"),
                ("class:warn", "     It may cause problems during the scrap ! Turn off idle to avoid any troubles")]
    else:
        return []

def api_key_status():
    if not is_api_key_valid():
        return [
            ("class:warn", "  🔑 API Key invalid or not found !\n"),
            ("class:warn", "     Please check your Gemini API key in config.py."),
        ]
    else:
        return [
            ("class:status_green", "  🔑 Gemini API Key is valid — you're ready to scrap !")
        ]

def get_courses(driver=None, connected=False):
    courses = get_course_list(driver, connected)
    return courses

def toggle_scraping(driver=None):
    global scraping_status
    if not scraping_status:
        scraping_status = True
        scraping_thread = threading.Thread(target=start_scraping, args=(driver,), daemon=True)
        scraping_thread.start()
    else:
        scraping_status = False

def start_scraping(driver):
    global scraping_status
    log.debug("Scraping thread started...")

    try:
        while scraping_status:
            try:
                log.info("Scraping...")
                # scraping logic
                time.sleep(5)
            except Exception as e:
                log.error(f"[SCRAP] Error during scraping loop: {e}")
    finally:
        log.debug("Scraping thread stopped.")


