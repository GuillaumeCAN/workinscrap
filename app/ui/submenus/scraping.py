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
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from prompt_toolkit.output import ColorDepth
from prompt_toolkit.widgets import Frame
import time
import threading

from app import scrap, log
from app.scrap import api_key_status


def scraping(driver=None, connected=False):
    options = ["Toggle Scrapping (everything)", "Select only certain courses (coming soon...)", "Return to Main Menu"]
    nonlocal_vars = {"selected": 0}

    def get_menu_text():
        current_action = "Stop Scrapping" if scrap.is_scraping() else "Start Scrapping (everything)"
        dynamic_options = [current_action, "Select only certain courses (coming soon...)", "Return to Main Menu"]

        result = []
        for i, option in enumerate(dynamic_options):
            if i == 1:  # Option désactivée
                style = "class:disabled"
            elif i == nonlocal_vars["selected"]:
                style = "class:selected"
            else:
                style = "class:menu"

            prefix = "> " if i == nonlocal_vars["selected"] else "  "
            result.append((style, f"  {prefix}{option}\n"))
        return result

    menu_control = FormattedTextControl(get_menu_text)
    status_control = FormattedTextControl(scrap.get_status_text)
    warn_status_text = FormattedTextControl(scrap.warn_status_text)
    api_key_status = FormattedTextControl(scrap.api_key_status)
    courses_list = FormattedTextControl(scrap.get_courses(driver, connected))
    log_control = FormattedTextControl(log.get_log_text)

    menu_window = Window(content=menu_control, always_hide_cursor=True)
    api_key_window = Window(content=api_key_status, always_hide_cursor=True)
    status_window = Window(height=1, content=status_control)
    warn_status_window = Window(height=2, content=warn_status_text)
    courses_window = Window(content=courses_list, always_hide_cursor=True)

    log_window = Window(content=log_control, wrap_lines=True)
    log_frame = VSplit([
        Window(width=4, char=" "),
        Frame(
            body=log_window,
            title="📑 LOGS",
            style="class:frame"
        )
    ])

    root_container = HSplit([
        status_window,
        warn_status_window,
        api_key_window,
        Window(height=1, char=" "),
        VSplit([Window(width=4, char=" "), courses_window]),
        Window(height=1, char=" "),
        log_frame,
        Window(height=1, char=" "),
        VSplit([Window(width=4, char=" "), menu_window])
    ])

    kb = KeyBindings()

    @kb.add("up")
    def up(event):
        while True:
            nonlocal_vars["selected"] = (nonlocal_vars["selected"] - 1) % len(options)
            if nonlocal_vars["selected"] != 1:  # Skip disabled
                break
        menu_control.text = get_menu_text()
        event.app.invalidate()

    @kb.add("down")
    def down(event):
        while True:
            nonlocal_vars["selected"] = (nonlocal_vars["selected"] + 1) % len(options)
            if nonlocal_vars["selected"] != 1:  # Skip disabled
                break
        menu_control.text = get_menu_text()
        event.app.invalidate()

    @kb.add("enter")
    def enter(event):
        choice = nonlocal_vars["selected"]
        if choice == 2:  # "Return to Main Menu"
            event.app.exit(result=None)
            return

        elif choice == 1:
            pass  # disable

        else:
            # Toggle scraping status
            scrap.toggle_scraping(driver)
            menu_control.text = get_menu_text()
            event.app.invalidate()

    style = Style.from_dict({
        "menu": "bold white bg:default",
        "selected": "bold cyan bg:default",
        "status_green": "bold green",
        "status_red": "bold red",
        "frame.label": "bg:#444444 #ffffff bold",
        "disabled": "fg:#666666 italic",
        "frame.border": "#888888",
        "warn": "bold gold"
    })

    app = Application(layout=Layout(root_container),
                      key_bindings=kb,
                      style=style,
                      full_screen=False,
                      color_depth=ColorDepth.TRUE_COLOR)

    def ui_log_callback(_message):
        app.invalidate()

    log.set_log_callback(ui_log_callback)

    def update_status_loop():
        while True:
            time.sleep(1)
            app.invalidate()

    threading.Thread(target=update_status_loop, daemon=True).start()

    result = app.run()
    return result
