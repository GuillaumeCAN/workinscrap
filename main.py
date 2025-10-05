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

from app.browser import start_browser, login
from app.menu import menu, show_title
from rich.console import Console

console = Console()

def main():
    driver = start_browser()
    connected = False
    show_title(driver, connected)
    try:
        if login(driver):
            connected = True
            console.clear()
            show_title(driver, connected)
            menu(driver, connected)
        else:
            print("🚫 Login failed... exiting script")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()