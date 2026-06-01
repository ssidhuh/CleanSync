"""Sidebar navigation component for the CleanSync desktop application."""

import customtkinter as ctk

from src.ui.theme import APP_COLORS, APP_FONTS

NAV_SECTIONS = [
    ("OVERVIEW", [
        ("🧰", "Dashboard", "dashboard"),
    ]),
    ("OPERATIONS", [
        ("👥", "Customers", "customers"),
        ("👨🏻‍🔧", "Cleaners", "cleaners"),
        ("🛠️", "Services", "services"),
        ("📅", "Bookings", "bookings"),
        ("🗓️", "Schedule", "schedule"),
    ]),
    ("FINANCE", [
        ("📄", "Invoices", "invoices"),
        ("💶", "Cleaner Payroll", "cleaner_payroll"),
        ("💳", "Payments", "payments"),
    ]),
]


class Sidebar(ctk.CTkFrame):
    """Left navigation sidebar used to switch between CleanSync views."""

    EXPANDED_WIDTH = 240
    COLLAPSED_WIDTH = 70

    def __init__(self, parent, on_navigation, on_exit):
        super().__init__(
            parent,
            width=self.EXPANDED_WIDTH,
            fg_color=APP_COLORS["sidebar"],
            corner_radius=0,
        )
        self.on_navigation = on_navigation
        self.on_exit = on_exit
        self.active_page = "dashboard"
        self.collapsed = False
        self.buttons = {}
        self.section_labels = []

        self.pack_propagate(False)

        self._build_logo()
        self._build_navigation()
        self._build_exit_button()
        self._build_collapse_button()
        self._refresh_active_button()

    def _build_logo(self):
        self.logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.logo_frame.pack(fill="x", padx=14, pady=(16, 20))

        self.logo_icon = ctk.CTkLabel(
            self.logo_frame,
            text="💧",
            width=40,
            height=40,
            fg_color=APP_COLORS["sidebar_active"],
            corner_radius=10,
            font=("Inter", 20),
        )
        self.logo_icon.pack(side="left")

        self.logo_text = ctk.CTkLabel(
            self.logo_frame,
            text="CleanSync",
            text_color=APP_COLORS["sidebar_active_text"],
            font=("Inter", 20, "bold"),
        )
        self.logo_text.pack(side="left", padx=(10, 0))

    def _build_navigation(self):
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(fill="both", expand=True, padx=10)

        for section_title, items in NAV_SECTIONS:
            section_label = ctk.CTkLabel(
                self.nav_frame,
                text=section_title,
                anchor="w",
                font=("Inter", 11, "bold"),
                text_color="#6B7280",
            )
            section_label.pack(fill="x", padx=6, pady=(12, 4))
            self.section_labels.append(section_label)

            for icon, label, page_key in items:
                button = ctk.CTkButton(
                    self.nav_frame,
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

    def _build_exit_button(self):
        self.exit_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.exit_frame.pack(fill="x", side="bottom", padx=10, pady=(8, 8))

        self.exit_button = ctk.CTkButton(
            self.exit_frame,
            text="🚪  Exit",
            anchor="w",
            height=42,
            corner_radius=10,
            font=APP_FONTS["body"],
            fg_color="#DC2626",
            hover_color="#B91C1C",
            text_color="#FFFFFF",
            command=self.on_exit,
        )
        self.exit_button.pack(fill="x")

    def _build_collapse_button(self):
        self.collapse_button = ctk.CTkButton(
            self,
            text="<",
            width=30,
            height=28,
            corner_radius=8,
            font=("Inter", 15, "bold"),
            fg_color="transparent",
            hover_color=APP_COLORS["sidebar_hover"],
            text_color=APP_COLORS["sidebar_text"],
            command=self.toggle_sidebar,
        )
        self.collapse_button.pack(side="bottom", anchor="e", padx=12, pady=(0, 14))

    def toggle_sidebar(self):
        """Collapse or expand the sidebar while keeping navigation visible."""
        self.collapsed = not self.collapsed
        self.configure(
            width=self.COLLAPSED_WIDTH if self.collapsed else self.EXPANDED_WIDTH
        )
        self._refresh_sidebar_layout()
        self._refresh_active_button()

    def _refresh_sidebar_layout(self):
        """Update sidebar text visibility without removing navigation buttons."""
        if self.collapsed:
            self.logo_text.pack_forget()
            self.collapse_button.configure(text=">")
            self.exit_button.configure(text="🚪", anchor="center")

            for section_label in self.section_labels:
                section_label.pack_forget()

            for page_key, button in self.buttons.items():
                button.configure(
                    text=self._get_icon_for_page(page_key),
                    anchor="center",
                    width=42,
                )

            return

        if not self.logo_text.winfo_ismapped():
            self.logo_text.pack(side="left", padx=(10, 0))

        self.collapse_button.configure(text="<")
        self.exit_button.configure(text="🚪  Exit", anchor="w")

        for widget in self.nav_frame.winfo_children():
            widget.pack_forget()

        label_index = 0

        for _, items in NAV_SECTIONS:
            section_label = self.section_labels[label_index]
            section_label.pack(fill="x", padx=6, pady=(12, 4))
            label_index += 1

            for icon, label, page_key in items:
                button = self.buttons[page_key]
                button.configure(
                    text=f"{icon}  {label}",
                    anchor="w",
                    width=200,
                )
                button.pack(fill="x", pady=4)

    def _get_icon_for_page(self, page_key):
        icon, _ = self._get_icon_and_label_for_page(page_key)
        return icon

    def _get_icon_and_label_for_page(self, page_key):
        for _, items in NAV_SECTIONS:
            for icon, label, key in items:
                if key == page_key:
                    return icon, label
        return "", ""

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
