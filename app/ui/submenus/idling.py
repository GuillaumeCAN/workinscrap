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

from app import idle, log

def idling(driver=None, connected=False):
    options = ["Toggle Idling", "Return to Main Menu"]  # Placeholder list
    nonlocal_vars = {"selected": 0}

    def get_menu_text():
        current_action = "Stop Idling" if idle.is_idling() else "Start Idling"
        dynamic_options = [current_action, "Return to Main Menu"]
        result = []
        for i, option in enumerate(dynamic_options):
            prefix = "> " if i == nonlocal_vars["selected"] else "  "
            style = "class:selected" if i == nonlocal_vars["selected"] else "class:menu"
            result.append((style, f"  {prefix}{option}\n"))
        return result

    menu_control = FormattedTextControl(get_menu_text)
    status_control = FormattedTextControl(idle.get_status_text)
    log_control = FormattedTextControl(log.get_log_text)

    menu_window = Window(content=menu_control, always_hide_cursor=True)
    status_window = Window(height=1, content=status_control)

    log_window = Window(content=log_control, wrap_lines=True)
    log_frame = Frame(
        body=log_window,
        title="📑 LOGS",
        style="class:frame"
    )

    root_container = HSplit([
        status_window,
        Window(height=1, char=" "),
        VSplit([Window(width=4, char=" "), menu_window]),
        log_frame
    ])

    kb = KeyBindings()

    @kb.add("up")
    def up(event):
        nonlocal_vars["selected"] = (nonlocal_vars["selected"] - 1) % len(options)
        menu_control.text = get_menu_text()
        event.app.invalidate()

    @kb.add("down")
    def down(event):
        nonlocal_vars["selected"] = (nonlocal_vars["selected"] + 1) % len(options)
        menu_control.text = get_menu_text()
        event.app.invalidate()

    @kb.add("enter")
    def enter(event):
        choice = nonlocal_vars["selected"]
        if choice == 1:  # "Return to Main Menu"
            event.app.exit(result=None)
        else:
            # Toggle idling status
            idle.toggle_idling(driver)
            menu_control.text = get_menu_text()
            event.app.invalidate()

    style = Style.from_dict({
        "menu": "bold white bg:default",
        "selected": "bold cyan bg:default",
        "status_green": "bold green",
        "status_red": "bold red",
        "frame.label" : "bg:#444444 #ffffff bold",
        "frame.border": "#888888"
    })

    app = Application(layout=Layout(root_container),
                      key_bindings=kb,
                      style=style,
                      full_screen=False,
                      color_depth=ColorDepth.TRUE_COLOR)

    def ui_log_callback(_message):
        app.invalidate()

    log.set_log_callback(ui_log_callback)

    result = app.run()
    return result
