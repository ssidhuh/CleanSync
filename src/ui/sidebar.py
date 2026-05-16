"""Sidebar navigation component for the CleanSync desktop application."""

import customtkinter as ctk

from src.ui.theme import APP_COLORS, APP_FONTS

NAV_ITEMS = [
    ("🧰", "Dashboard", "dashboard"),
    ("👥", "Customers", "customers"),
    ("👨🏻‍🔧", "Cleaners", "cleaners"),
    ("🛠️", "Services", "services"),
    ("📅", "Bookings", "bookings"),
    ("🗓️", "Schedule", "schedule"),
    ("📄", "Invoices", "invoices"),
    ("💶", "Cleaner Payroll", "cleaner_payroll"),
    ("💳", "Payments", "payments"),
]


class Sidebar(ctk.CTkFrame):
    """Left navigation sidebar used to switch between CleanSync views."""

    def __init__(self, parent, on_navigation):
        super().__init__(
            parent,
            width=240,
            fg_color=APP_COLORS["sidebar"],
            corner_radius=0,
        )
        self.on_navigation = on_navigation
        self.active_page = "dashboard"
        self.buttons = {}

        self.grid_propagate(False)
        self._build_logo()
        self._build_navigation()

    def _build_logo(self):
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(fill="x", padx=14, pady=(16, 20))

        logo_icon = ctk.CTkLabel(
            logo_frame,
            text="💧",
            width=40,
            height=40,
            fg_color=APP_COLORS["sidebar_active"],
            corner_radius=10,
            font=("Inter", 20),
        )
        logo_icon.pack(side="left")

        logo_text = ctk.CTkLabel(
            logo_frame,
            text="CleanSync",
            text_color=APP_COLORS["sidebar_active_text"],
            font=("Inter", 20, "bold"),
        )
        logo_text.pack(side="left", padx=(10, 0))

    def _build_navigation(self):
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=10)

        for icon, label, page_key in NAV_ITEMS:
            button = ctk.CTkButton(
                nav_frame,
                text=f"{icon}  {label}",
                anchor="w",
                height=42,
                corner_radius=10,
                font=APP_FONTS["body"],
                fg_color="transparent",
                hover_color=APP_COLORS["sidebar_hover"],
                text_color=APP_COLORS["sidebar_text"],
                command=lambda key=page_key: self.select_page(key),
            )
            button.pack(fill="x", pady=4)
            self.buttons[page_key] = button

        self._refresh_active_button()

    def select_page(self, page_key):
        self.active_page = page_key
        self._refresh_active_button()
        self.on_navigation(page_key)

    def _refresh_active_button(self):
        for page_key, button in self.buttons.items():
            if page_key == self.active_page:
                button.configure(
                    fg_color=APP_COLORS["sidebar_active"],
                    text_color=APP_COLORS["sidebar_active_text"],
                )
            else:
                button.configure(
                    fg_color="transparent",
                    text_color=APP_COLORS["sidebar_text"],
                )