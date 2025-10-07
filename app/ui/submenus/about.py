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

from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.output.color_depth import ColorDepth
from prompt_toolkit.widgets import Frame
import webbrowser

from app.config import GITHUB_REPO, AUTHOR, APP_NAME

def about(driver=None, connected=False):
    options = ["Visit Github project repository", "Return to Main Menu"]
    selected = {"index": 0}

    about_text = [
        ("","\n"),
        ("class:title", f"{APP_NAME} is an application for educational purposes only;\n"),
        ("", "It is in "),
        ("class:bold", "no way designed to cheat or falsify results.\n"),
        ("", "This project's sole purpose is to improve programming and web scraping skills.\n"),
        ("", "I dissociate myself from any use for cheating purposes.\n"),
        ("", "This project is coded in Python 3.12 and uses Selenium as well as API requests to Gemini AI.\n\n"),
        ("class:author", f"Best regards - {AUTHOR}\n"),
        ("class:ps", "PS: je cherche toujours une alternance pitié 🙏\n"),
    ]

    def get_menu_text():
        result = []
        for i, option in enumerate(options):
            prefix = "> " if i == selected["index"] else "  "
            style = "class:selected" if i == selected["index"] else "class:menu"
            result.append((style, f"{prefix}{option}\n"))
        return result

    about_window = VSplit([
        Window(width=4, char=" "),
        Frame(
            body=Window(
                content=FormattedTextControl(about_text),
                wrap_lines=True,
                always_hide_cursor=True,
            ),
            title="📘 About This Project",
            style="class:frame"
        )
    ])
    menu_control = FormattedTextControl(get_menu_text)
    menu_window = Window(content=menu_control, always_hide_cursor=True)

    root_container = HSplit([
        Window(height=1, char=" "),
        about_window,
        Window(height=1, char=" "),
        VSplit([Window(width=4, char=" "), menu_window]),
    ])

    kb = KeyBindings()

    @kb.add("up")
    def move_up(event):
        selected["index"] = (selected["index"] - 1) % len(options)
        menu_control.text = get_menu_text()
        event.app.invalidate()

    @kb.add("down")
    def move_down(event):
        selected["index"] = (selected["index"] + 1) % len(options)
        menu_control.text = get_menu_text()
        event.app.invalidate()

    @kb.add("enter")
    def select_option(event):
        choice = selected["index"]
        if choice == 0:
            # Open GitHub repo
            webbrowser.open_new_tab(GITHUB_REPO)
        elif choice == 1:
            event.app.exit(result=None)

    style = Style.from_dict({
        "menu": "bold white bg:default",
        "selected": "bold cyan bg:default",

        "title": "bold cyan",
        "bold": "bold yellow",
        "author": "magenta bold",
        "ps": "italic green",

        "frame.label": "bg:#444444 #ffffff bold",
        "frame.border": "#888888",
    })

    app = Application(layout=Layout(root_container),
                      key_bindings=kb,
                      style=style,
                      full_screen=False,
                      color_depth=ColorDepth.TRUE_COLOR)

    app.run()
