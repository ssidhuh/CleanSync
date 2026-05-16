"""Compatibility entry point for the CleanSync graphical interface.

The real user interface lives in ``src.ui.fixed_app``. This module only
redirects older launch paths so VS Code cannot accidentally run the previous
broken layout.
"""
# ruff: noqa: I001

from src.ui.fixed_app import run_application


if __name__ == "__main__":
    run_application()
