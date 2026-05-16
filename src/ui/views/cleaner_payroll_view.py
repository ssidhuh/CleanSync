"""Cleaner payroll view for the CleanSync desktop application."""

from __future__ import annotations

import customtkinter as ctk

from src.models.cleaner_payroll import CleanerPayroll
from src.repositories.cleaner_payroll_repository import CleanerPayrollRepository
from src.ui.theme import APP_COLORS, APP_FONTS


class CleanerPayrollView(ctk.CTkFrame):
    """Cleaner payroll page showing weekly earnings from completed bookings."""

    def __init__(self, parent) -> None:
        super().__init__(parent, fg_color=APP_COLORS["background"])
        self.pack(fill="both", expand=True)

        self.search_entry: ctk.CTkEntry | None = None
        self.table_frame: ctk.CTkFrame | None = None

        self._reload_data()
        self._build_page()

    def _reload_data(self) -> None:
        self.payroll_records = CleanerPayrollRepository.find_all()

    def _build_page(self) -> None:
        self._build_header()
        self._build_summary_cards()
        self._build_table()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(28, 18))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            left,
            text="Cleaner Payroll",
            text_color=APP_COLORS["foreground"],
            font=("Inter", 28, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="Weekly cleaner earnings calculated from completed bookings",
            text_color=APP_COLORS["muted_text"],
            font=APP_FONTS["body"],
        ).pack(anchor="w", pady=(4, 0))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")

        self.search_entry = ctk.CTkEntry(
            right,
            placeholder_text="Search cleaner...",
            width=250,
            height=40,
            corner_radius=10,
            border_color=APP_COLORS["border"],
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", lambda _event: self._refresh_table())

    def _build_summary_cards(self) -> None:
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="x", padx=30, pady=(0, 18))

        total_hours = sum(payroll.total_hours for payroll in self.payroll_records)
        total_earnings = sum(payroll.total_earnings for payroll in self.payroll_records)
        pending_count = len(
            [
                payroll
                for payroll in self.payroll_records
                if payroll.payment_status == "Pending"
            ]
        )

        values = [
            ("Payroll Records", len(self.payroll_records), "📄"),
            ("Total Hours", f"{total_hours:.2f}", "⏱️"),
            ("Total Earnings", f"€{total_earnings:.2f}", "€"),
            ("Pending Payments", pending_count, "🕒"),
        ]

        for column, (title, value, icon) in enumerate(values):
            cards.grid_columnconfigure(column, weight=1)
            self._summary_card(cards, title, value, icon, column)

    def _summary_card(self, parent, title: str, value, icon: str, column: int) -> None:
        card = ctk.CTkFrame(
            parent,
            fg_color=APP_COLORS["card"],
            corner_radius=16,
            border_width=1,
            border_color=APP_COLORS["border"],
        )
        card.grid(row=0, column=column, sticky="ew", padx=8)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(14, 4))

        ctk.CTkLabel(
            top,
            text=title,
            text_color=APP_COLORS["muted_text"],
            font=APP_FONTS["small"],
        ).pack(side="left")

        ctk.CTkLabel(top, text=icon, font=("Inter", 20)).pack(side="right")

        ctk.CTkLabel(
            card,
            text=str(value),
            text_color=APP_COLORS["foreground"],
            font=("Inter", 24, "bold"),
        ).pack(anchor="w", padx=18, pady=(0, 16))

    def _build_table(self) -> None:
        self.table_frame = ctk.CTkFrame(
            self,
            fg_color=APP_COLORS["card"],
            corner_radius=14,
            border_width=1,
            border_color=APP_COLORS["border"],
        )
        self.table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        self._refresh_table()

    def _refresh_table(self) -> None:
        if self.table_frame is None:
            return

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        records = self._filtered_payroll_records()

        headers = [
            "CLEANER",
            "PERIOD",
            "BOOKINGS",
            "HOURS",
            "RATE",
            "EARNINGS",
            "STATUS",
        ]
        widths = [160, 190, 100, 100, 100, 120, 120]

        for column, header in enumerate(headers):
            self.table_frame.grid_columnconfigure(column, weight=1, minsize=widths[column])
            ctk.CTkLabel(
                self.table_frame,
                text=header,
                text_color=APP_COLORS["muted_text"],
                font=("Inter", 11, "bold"),
            ).grid(row=0, column=column, sticky="w", padx=10, pady=(16, 10))

        if not records:
            ctk.CTkLabel(
                self.table_frame,
                text="No cleaner payroll records yet. Complete bookings to generate payroll.",
                text_color=APP_COLORS["muted_text"],
                font=APP_FONTS["body"],
            ).grid(row=1, column=0, columnspan=7, pady=80)
            return

        for row_index, payroll in enumerate(records, start=1):
            self._table_row(payroll, row_index)

    def _table_row(self, payroll: CleanerPayroll, row_index: int) -> None:
        values = [
            payroll.cleaner_name,
            payroll.period_text,
            str(payroll.completed_bookings),
            f"{payroll.total_hours:.2f}",
            f"€{payroll.hourly_pay_rate:.2f}/hr",
            f"€{payroll.total_earnings:.2f}",
        ]

        for column, value in enumerate(values):
            ctk.CTkLabel(
                self.table_frame,
                text=value,
                text_color=APP_COLORS["foreground"],
                font=("Inter", 13, "bold" if column in [0, 5] else "normal"),
            ).grid(row=row_index, column=column, sticky="w", padx=10, pady=12)

        status_bg, status_fg = self._status_colours(payroll.payment_status)

        ctk.CTkLabel(
            self.table_frame,
            text=payroll.payment_status,
            text_color=status_fg,
            fg_color=status_bg,
            corner_radius=8,
            height=24,
            width=76,
            font=("Inter", 11, "bold"),
        ).grid(row=row_index, column=6, sticky="w", padx=10, pady=12)

    def _filtered_payroll_records(self) -> list[CleanerPayroll]:
        search_text = self.search_entry.get().strip().lower() if self.search_entry else ""

        if not search_text:
            return self.payroll_records

        return [
            payroll
            for payroll in self.payroll_records
            if search_text in payroll.cleaner_name.lower()
            or search_text in payroll.payment_status.lower()
            or search_text in payroll.period_text.lower()
        ]

    @staticmethod
    def _status_colours(status: str) -> tuple[str, str]:
        if status == "Paid":
            return "#dcfce7", "#059669"

        return "#fef3c7", "#b45309"