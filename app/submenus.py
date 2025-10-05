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

def idling(driver=None, connected=False):
    options = ["Start Idling", "Stop Idling", "Return to Main Menu"]
    nonlocal_vars = {"selected": 0, "idling_status": False}

    def get_menu_text():
        result = []
        for i, option in enumerate(options):
            prefix = "> " if i == nonlocal_vars["selected"] else "  "
            style = "class:selected" if i == nonlocal_vars["selected"] else "class:menu"
            result.append((style, f"  {prefix}{option}\n"))
        return result

    def get_status_text():
        if nonlocal_vars["idling_status"]:
            return [("class:status_green", "  🟩 Now idling...")]
        else:
            return [("class:status_red", "  🔴 Idling stopped.")]

    menu_control = FormattedTextControl(get_menu_text)
    status_control = FormattedTextControl(get_status_text)

    menu_window = Window(content=menu_control, always_hide_cursor=True)
    status_window = Window(height=1, content=status_control)

    root_container = HSplit([
        status_window,
        Window(height=1, char=" "),
        VSplit([Window(width=4, char=" "), menu_window])
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
        if choice == len(options) - 1:
            event.app.exit(result=None)
        else:
            if choice == 0:
                nonlocal_vars["idling_status"] = True
            elif choice == 1:
                nonlocal_vars["idling_status"] = False
            event.app.invalidate()

    style = Style.from_dict({
        "menu": "bold white bg:default",
        "selected": "bold cyan bg:default",
        "status_green": "bold green",
        "status_red": "bold red"
    })

    app = Application(layout=Layout(root_container),
                      key_bindings=kb,
                      style=style,
                      full_screen=False,
                      color_depth=ColorDepth.TRUE_COLOR)

    result = app.run()
    return result
