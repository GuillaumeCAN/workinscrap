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
#  © Abraxas – All rights reserved.
# ==============================================================================

from prompt_toolkit.application.current import get_app
from prompt_toolkit.formatted_text import ANSI
from datetime import datetime

_log_lines = []
_log_callback = None
MAX_LOG_LINES = 200

def info(msg): log(msg, level="INFO")
def debug(msg): log(msg, level="DEBUG")
def error(msg): log(msg, level="ERROR")
def scrap(msg): log(msg, level="SCRAP")
def warn(msg): log(msg, level="WARNING")

def set_log_callback(callback):
    global _log_callback
    _log_callback = callback

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    level = level.upper()

    if level == "ERROR":
        color = "ansired"

    elif level == "WARNING":
        color = "yellow"

    elif level == "DEBUG":
        color = "ansiblue"

    elif level == "SCRAP":
        color = "ansimagenta"

    else:
        color = "ansigreen"

    formatted = f"[{timestamp}] | [{level}] : {message}"
    entry = (color, formatted)

    if len(_log_lines) >= MAX_LOG_LINES:
        _log_lines.pop(0)
    _log_lines.append(entry)

    if _log_callback:
        _log_callback(formatted)

def get_log_text():
    if not _log_lines:
        return []

    return [(style, text + '\n') for style, text in _log_lines[-10:]]

def clear_logs():
    _log_lines.clear()
    if _log_callback:
        _log_callback("")
