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

from app import scrap, log, get_user
from app.scrap import api_key_status

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from prompt_toolkit.output import ColorDepth
from prompt_toolkit.widgets import Frame
import time
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.config import BACK_TO_COURSE_BTN, COURSE_LIST_UL


from app import scrap, log, get_user
from app.scrap import api_key_status


def scraping(driver=None, connected=False):
    raw_courses, formatted_courses = scrap.get_courses(driver, connected)
    courses = formatted_courses
    nonlocal_vars = {"selected": 0, "in_modules_menu": False, "current_modules": [], "current_course": None}

    # ───────────────────────────────────────────────────────────────
    #  courses menu function
    # ───────────────────────────────────────────────────────────────
    def get_courses_text():
        result = []
        for i, course in enumerate(courses):
            style = "class:selected" if i == nonlocal_vars["selected"] else "class:menu"
            prefix = "> " if i == nonlocal_vars["selected"] else "  "
            result.append((style, f"  {prefix}{course}\n"))

        idx_return = len(courses)
        style = "class:selected" if nonlocal_vars["selected"] == idx_return else "class:menu"
        result.append((style, f"  {'> ' if nonlocal_vars['selected'] == idx_return else '  '}Return to Main Menu\n"))
        return result

    # ───────────────────────────────────────────────────────────────
    #  modules menu function
    # ───────────────────────────────────────────────────────────────
    def get_modules_text():
        modules = nonlocal_vars["current_modules"]
        course_name = nonlocal_vars["current_course"] or "Unknown course"
        result = []

        # En-tête du menu modules
        result.append(("class:title", f"\n📘 Modules for : {course_name}\n"))
        result.append(
            ("class:disabled", "================================================================================\n\n"))

        # Liste des modules
        for i, mod in enumerate(modules):
            style = "class:selected" if i == nonlocal_vars["selected"] else "class:menu"
            prefix = "> " if i == nonlocal_vars["selected"] else "  "
            result.append((style, f"  {prefix}{mod}\n"))

        # Ligne vide + séparateur + ligne vide
        result.append(("class:menu", "\n"))
        result.append(("class:disabled", "  ────────────────────────────\n"))
        result.append(("class:menu", "\n"))

        # Bouton de retour
        idx_return = len(modules)
        style = "class:selected" if nonlocal_vars["selected"] == idx_return else "class:menu"
        result.append((style, f"  {'> ' if nonlocal_vars['selected'] == idx_return else '  '}Back to Courses Menu\n"))

        return result

    # ───────────────────────────────────────────────────────────────
    #  Share UI
    # ───────────────────────────────────────────────────────────────
    menu_control = FormattedTextControl(get_courses_text)
    status_control = FormattedTextControl(scrap.get_status_text)
    warn_status_text = FormattedTextControl(scrap.warn_status_text)
    api_key_status = FormattedTextControl(scrap.api_key_status)
    log_control = FormattedTextControl(log.get_log_text)

    menu_window = Window(content=menu_control, always_hide_cursor=True)
    api_key_window = Window(content=api_key_status, always_hide_cursor=True)
    status_window = Window(height=1, content=status_control)
    warn_status_window = Window(height=2, content=warn_status_text)
    log_window = Window(content=log_control, wrap_lines=True)
    log_frame = VSplit([Window(width=4, char=" "), Frame(body=log_window, title="📑 LOGS", style="class:frame")])

    root_container = HSplit([
        status_window,
        warn_status_window,
        api_key_window,
        Window(height=1, char=" "),
        log_frame,
        Window(height=1, char=" "),
        VSplit([Window(width=4, char=" "), menu_window])
    ])

    # ───────────────────────────────────────────────────────────────
    #  keyboard
    # ───────────────────────────────────────────────────────────────
    kb = KeyBindings()

    @kb.add("up")
    def up(event):
        if nonlocal_vars["in_modules_menu"]:
            modules = nonlocal_vars["current_modules"]
            nonlocal_vars["selected"] = (nonlocal_vars["selected"] - 1) % (len(modules) + 1)
            menu_control.text = get_modules_text()
        else:
            nonlocal_vars["selected"] = (nonlocal_vars["selected"] - 1) % (len(courses) + 1)
            menu_control.text = get_courses_text()
        event.app.invalidate()

    @kb.add("down")
    def down(event):
        if nonlocal_vars["in_modules_menu"]:
            modules = nonlocal_vars["current_modules"]
            nonlocal_vars["selected"] = (nonlocal_vars["selected"] + 1) % (len(modules) + 1)
            menu_control.text = get_modules_text()
        else:
            nonlocal_vars["selected"] = (nonlocal_vars["selected"] + 1) % (len(courses) + 1)
            menu_control.text = get_courses_text()
        event.app.invalidate()

    @kb.add("enter")
    def enter(event):
        if nonlocal_vars["in_modules_menu"]:
            modules = nonlocal_vars["current_modules"]
            choice = nonlocal_vars["selected"]
            if choice == len(modules):

                # back to course btn

                try:
                    log.info("Returning to course list...")
                    back_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, BACK_TO_COURSE_BTN))
                    )
                    back_btn.click()

                    # attendre que la liste des cours réapparaisse
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, COURSE_LIST_UL))
                    )
                    log.info("Course list reloaded successfully.")
                except Exception as e:
                    log.error(f"Could not click BACK_TO_COURSE button: {e}")

                # revenir au menu des cours dans le terminal
                nonlocal_vars["in_modules_menu"] = False
                nonlocal_vars["selected"] = 0
                menu_control.text = get_courses_text()
                event.app.invalidate()
            else:
                selected_module = modules[choice]
                log.info(f"Selected module: {selected_module}")
            event.app.invalidate()
        else:
            choice = nonlocal_vars["selected"]
            if choice == len(courses):
                event.app.exit(result=None)
            else:
                course_name = raw_courses[choice]
                log.info(f"Fetching modules for {course_name}...")
                modules = get_user.get_module_list(driver, course_name, connected)
                if not modules:
                    log.warn(f"No modules found for {course_name}")
                    return

                nonlocal_vars["current_modules"] = modules
                nonlocal_vars["current_course"] = course_name
                nonlocal_vars["in_modules_menu"] = True
                nonlocal_vars["selected"] = 0
                menu_control.text = get_modules_text()
            event.app.invalidate()

    # ───────────────────────────────────────────────────────────────
    #  style & app
    # ───────────────────────────────────────────────────────────────
    style = Style.from_dict({
        "menu": "bold white bg:default",
        "selected": "bold cyan bg:default",
        "status_green": "bold green",
        "status_red": "bold red",
        "frame.label": "bg:#444444 #ffffff bold",
        "disabled": "fg:#666666 italic",
        "frame.border": "#888888",
        "warn": "bold gold",
        "title": "bold cyan underline",
    })

    app = Application(
        layout=Layout(root_container),
        key_bindings=kb,
        style=style,
        full_screen=False,
        color_depth=ColorDepth.TRUE_COLOR
    )

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

