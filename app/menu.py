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

from pyfiglet import Figlet
from rich.console import Console, Group

from app.config import APP_NAME, AUTHOR

console = Console()

def show_title():
    f = Figlet(font="slant")
    ascii_art = f.renderText(APP_NAME)
    console.print(f"[bold cyan]{ascii_art}[/bold cyan]")

