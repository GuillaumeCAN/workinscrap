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
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from prompt_toolkit.output import ColorDepth
from prompt_toolkit.layout.containers import VSplit

from app.config import APP_NAME, AUTHOR
from app.ui.ui import show_title
from app.ui.submenus.idling import idling
from app.get_user import get_course_list

console = Console()

MENU_OPTIONS = [
    "Idling account for fake time",
    "Start scraping and filling exercises",
    "About WorkinScrap",
    "Quit the script"
]

class Menu:
    def __init__(self, options):
        self.options = options
        self.selected = 0
        self.control = FormattedTextControl(self.get_menu_text)
        self.window = Window(
            content=self.control,
            always_hide_cursor=True,
        )
        self.bindings = self.get_key_bindings()
        self.app = Application(
            layout=Layout(
                HSplit([
                    VSplit([
                        Window(width=4, char=" "),  # padding gauche
                        self.window,
                    ])
                ])
            ),
            key_bindings=self.bindings,
            full_screen=False,
            mouse_support=False,
            style=Style.from_dict({
                "menu": "bold white bg:default",
                "selected": "bold cyan bg:default"
            }),
            color_depth=ColorDepth.TRUE_COLOR,
        )

    def get_menu_text(self):
        result = []
        for i, option in enumerate(self.options):
            if i == self.selected:
                result.append(("class:selected", f"> {option}\n"))
            else:
                result.append(("class:menu", f"  {option}\n"))
        return result

    def get_key_bindings(self):
        bindings = KeyBindings()

        @bindings.add("up")
        def move_up(event):
            self.selected = (self.selected - 1) % len(self.options)
            self.control.text = self.get_menu_text()

        @bindings.add("down")
        def move_down(event):
            self.selected = (self.selected + 1) % len(self.options)
            self.control.text = self.get_menu_text()

        @bindings.add("enter")
        def select_option(event):
            self.app.exit(result=self.selected)

        @bindings.add("escape")
        def exit_app(event):
            self.app.exit(result=None)

        return bindings

    def run(self):
        return self.app.run()

def handle_selection(index, driver=None, connected=False):
    console.clear()
    show_title(driver, connected)

    option = MENU_OPTIONS[index]

    if option == "Idling account for fake time":
        idling(driver, connected)
    elif option == "Start scraping and filling exercises":
        print(get_course_list(driver, connected))
        input("Press Enter to return to main menu...")
    elif option == "About WorkinScrap":

        console.print(f"[cyan]{APP_NAME}[/cyan] is an application for educational purposes only;\n")
        console.print("it is in [bold]no way designed to cheat or falsify results.[/bold]")
        console.print("This project's sole purpose is to improve programming and web scraping skills.")
        console.print("I dissociate myself from any use for cheating purposes.")
        console.print("This project is coded in Python 3.12 and uses Selenium as well as API requests to Gemini AI.\n")

        console.print(f"[magenta]Best regards - [bold]{AUTHOR}[/bold][/magenta]")
        console.print("PS: je cherche toujours une alternance pitié 🙏")

        input("Press Enter to return to main menu...")
    elif option == "Quit the script":
        console.print("[bold red]→ Exiting script...[/bold red]")
        driver.quit()
        console.clear()
        exit()

    console.clear()
    show_title(driver, connected)

def menu(driver=None, connected=False):
    while True:
        menu = Menu(MENU_OPTIONS)
        selected = menu.run()
        if selected is None:
            console.print("[bold red]→ Menu quitté.[/bold red]")
            break
        handle_selection(selected, driver, connected)