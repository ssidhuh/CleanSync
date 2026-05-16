"""Application entry point for CleanSync."""

from src.database.database_manager import DatabaseManager
from src.ui.modern_app import run_application


def main() -> None:
    """
    Initialise required resources and launch the graphical interface.

    Keeping startup logic small makes the application easier to
    maintain as more features are added.
    """
    print("Starting CleanSync from /Users/harpreetsingh/Documents/CleanSync")
    print("Expected window title: CleanSync")
    DatabaseManager.initialise_database()
    run_application()


if __name__ == "__main__":
    main()
