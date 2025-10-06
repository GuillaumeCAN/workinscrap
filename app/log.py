from prompt_toolkit.application.current import get_app
from prompt_toolkit.formatted_text import ANSI
from datetime import datetime

_log_lines = []
_log_callback = None
MAX_LOG_LINES = 200

def info(msg): log(msg, level="INFO")
def debug(msg): log(msg, level="DEBUG")
def error(msg): log(msg, level="ERROR")

def set_log_callback(callback):
    global _log_callback
    _log_callback = callback

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    level = level.upper()

    if level == "ERROR":
        color = "ansired"

    elif level == "DEBUG":
        color = "ansiblue"

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
