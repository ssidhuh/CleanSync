"""Modern CleanSync application shell."""

from __future__ import annotations

from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from src.database.database_manager import DatabaseManager
from src.ui.sidebar import Sidebar
from src.ui.theme import APP_COLORS
from src.ui.views.booking_view import BookingsView
from src.ui.views.cleaner_payroll_view import CleanerPayrollView
from src.ui.views.cleaner_view import CleanersView
from src.ui.views.customer_view import CustomersView
from src.ui.views.dashboard_view import DashboardView
from src.ui.views.invoice_view import InvoicesView
from src.ui.views.payment_view import PaymentsView
from src.ui.views.schedule_view import ScheduleView
from src.ui.views.service_view import ServicesView


class CleanSyncModernApp(ctk.CTk):
    """Main application window with sidebar navigation and page area."""

    def __init__(self) -> None:
        super().__init__()

        self.title("CleanSync")
        self.geometry("1180x760")
        self.minsize(1180, 760)
        self.configure(fg_color=APP_COLORS["background"])
        self.protocol("WM_DELETE_WINDOW", self.exit_application)

        self.sidebar = Sidebar(self, self.show_page, self.exit_application)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.main_area = ctk.CTkFrame(self, fg_color=APP_COLORS["background"])
        self.main_area.pack(side="left", fill="both", expand=True)
        self.main_area.pack_propagate(False)

        self._build_top_bar()

        self.content = ctk.CTkFrame(self.main_area, fg_color=APP_COLORS["background"])
        self.content.pack(side="top", fill="both", expand=True)
        self.content.pack_propagate(False)

        self.show_page("dashboard")

    def _build_top_bar(self) -> None:
        """Create the simple greeting bar above the page content."""
        top_bar = ctk.CTkFrame(
            self.main_area,
            height=66,
            fg_color=APP_COLORS["card"],
            corner_radius=0,
        )
        top_bar.pack(side="top", fill="x")
        top_bar.pack_propagate(False)

        greeting_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        greeting_frame.pack(side="left", padx=30, pady=(9, 9))

        greeting = ctk.CTkLabel(
            greeting_frame,
            text=self._get_greeting_text(),
            font=("Inter", 13, "bold"),
            text_color=APP_COLORS["foreground"],
        )
        greeting.pack(anchor="w")

        date_label = ctk.CTkLabel(
            greeting_frame,
            text=self._get_current_date_text(),
            font=("Inter", 12),
            text_color=APP_COLORS["muted_text"],
        )
        date_label.pack(anchor="w")

    def _get_greeting_text(self) -> str:
        """Return a time-aware greeting for the top bar."""
        current_hour = datetime.now().hour

        if current_hour < 12:
            return "Good morning 👋"
        if current_hour < 18:
            return "Good afternoon 👋"

        return "Good evening 👋"

    def _get_current_date_text(self) -> str:
        """Return the current date in a clean readable format."""
        return datetime.now().strftime("%A, %B %-d, %Y")

    def exit_application(self) -> None:
        """Disconnect the database and close the application safely."""
        confirm_exit = messagebox.askyesno(
            "Exit CleanSync",
            "Do you want to disconnect the database and exit CleanSync?",
        )

        if confirm_exit:
            DatabaseManager.close_database()
            self.destroy()

    def clear_content(self) -> None:
        """Remove the currently displayed page."""
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_page(self, page_key: str) -> None:
        """Display the selected page."""
        self.clear_content()

        if page_key == "dashboard":
            DashboardView(self.content)
        elif page_key == "customers":
            CustomersView(self.content)
        elif page_key == "cleaners":
            CleanersView(self.content)
        elif page_key == "services":
            ServicesView(self.content)
        elif page_key == "bookings":
            BookingsView(self.content)
        elif page_key == "schedule":
            ScheduleView(self.content)
        elif page_key == "invoices":
            InvoicesView(self.content)
        elif page_key == "cleaner_payroll":
            CleanerPayrollView(self.content)
        elif page_key == "payments":
            PaymentsView(self.content)
        else:
            self.show_placeholder(page_key)

    def show_placeholder(self, page_key: str) -> None:
        """Show a temporary page until the real view is implemented."""
        frame = ctk.CTkFrame(self.content, fg_color=APP_COLORS["background"])
        frame.pack(fill="both", expand=True)

        title = ctk.CTkLabel(
            frame,
            text=page_key.title(),
            font=("Inter", 28, "bold"),
            text_color=APP_COLORS["foreground"],
        )
        title.pack(anchor="w", padx=30, pady=(30, 6))


def run_application() -> None:
    """Launch the modern CleanSync desktop application."""
    print("RUNNING MODERN APP NOW")
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = CleanSyncModernApp()
    app.mainloop()


if __name__ == "__main__":
    run_application()
