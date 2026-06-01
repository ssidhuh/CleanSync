"""Application entry point for CleanSync."""

from tkinter import messagebox

from mysql.connector import Error

from src.database.database_manager import DatabaseManager
from src.ui.modern_app import run_application


def main() -> None:
    """
    Initialise required resources and launch the graphical interface.

    The database is checked before the UI starts so connection issues
    are shown clearly instead of causing a terminal traceback.
    """
    print("Starting CleanSync")
    print("Expected window title: CleanSync")

    try:
        DatabaseManager.initialise_database()
    except Error as error:
        messagebox.showerror(
            "Database Connection Error",
            "CleanSync could not connect to the MySQL database.\n\n"
            "Please make sure XAMPP is open and MySQL Database is running.\n\n"
            f"Technical details:\n{error}",
        )
        return

    run_application()


if __name__ == "__main__":
    main()
