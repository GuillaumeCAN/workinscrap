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

from rich.padding import Padding
from selenium.webdriver.common.by import By
from pyfiglet import Figlet
from rich.console import Console
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.config import APP_NAME, AUTHOR, VERSION
from app.get_user import get_user_name, get_user_time_spent
from app.idle import is_idling

console = Console()

def show_title(driver=None, connected=False):
    f = Figlet(font="slant")
    ascii_art = f.renderText(APP_NAME)
    console.clear()
    console.print(f"[bold cyan]{ascii_art}[/bold cyan]")
    console.print(Padding(f"[italic white]Coded by {AUTHOR}[/italic white]", (0, 0, 0, 4)))
    console.print(Padding(f"\n[italic cyan]Why study, when you can scrape? - {APP_NAME} v{VERSION}[/italic cyan]\n", (0, 0, 0, 6)))


    if connected and driver is not None:
        try:
            user_name = get_user_name(driver, connected)
            time_spent = get_user_time_spent(driver, connected)

            console.print(Padding(f"[purple]Connected as {user_name}[/purple]", (0, 0, 0, 4)))
            if is_idling():
                console.print(Padding(f"[dodger_blue1]Time spent on WorkinLive : {time_spent}[/dodger_blue1] [green4](idling in background...)[/green4]", (0, 0, 0, 4)))
            else:
                console.print(Padding(f"[dodger_blue1]Time spent on WorkinLive : {time_spent}[/dodger_blue1] [grey70](idling daemon not running)[/grey70]", (0, 0, 0, 4)))
        except Exception as e:
            console.print(Padding(f"[red]Failed to fetch user info: {e}[/red]", (0, 0, 0, 4)))
    else:
        console.print(Padding(f"[red]Not connected...[/red]", (0, 0, 0, 4)))

    console.rule()
