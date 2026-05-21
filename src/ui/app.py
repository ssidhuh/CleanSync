"""Compatibility entry point for the CleanSync graphical interface.

The real user interface lives in ``src.ui.modern_app``. This module redirects
older launch paths so VS Code does not accidentally run outdated UI code.
"""

from src.ui.modern_app import run_application


if __name__ == "__main__":
    run_application()