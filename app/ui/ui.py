from rich.padding import Padding
from selenium.webdriver.common.by import By
from pyfiglet import Figlet
from rich.console import Console
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.config import APP_NAME, AUTHOR, USER_NAME, USER_TIME_SPENT
from app.idle import is_idling

console = Console()

def show_title(driver=None, connected=False):
    f = Figlet(font="slant")
    ascii_art = f.renderText(APP_NAME)
    console.clear()
    console.print(f"[bold cyan]{ascii_art}[/bold cyan]")
    console.print(Padding(f"[italic white]Coded by {AUTHOR}[/italic white]", (0, 0, 0, 4)))

    if connected and driver is not None:
        try:
            user_name = driver.find_element(By.XPATH, USER_NAME).text
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, USER_TIME_SPENT))
            )
            time_spent = driver.find_element(By.XPATH, USER_TIME_SPENT).text
            console.print(Padding(f"[purple]Connected as {user_name}[/purple]", (0, 0, 0, 4)))
            if is_idling():
                console.print(Padding(f"[dodger_blue1]Time spent on WorkinLive : {time_spent}[/dodger_blue1] [green4](idling in background...)[/green4]", (0, 0, 0, 4)))
            else:
                console.print(Padding(f"[dodger_blue1]Time spent on WorkinLive : {time_spent}[/dodger_blue1] [grey70](idling deamon not running)[/grey70]", (0, 0, 0, 4)))
        except Exception as e:
            console.print(Padding(f"[red]Failed to fetch user info: {e}[/red]", (0, 0, 0, 4)))
    else:
        console.print(Padding(f"[red]Not connected...[/red]", (0, 0, 0, 4)))

    console.rule()
