"""Schedule view for the CleanSync desktop application."""

from __future__ import annotations

from datetime import datetime, timedelta

import customtkinter as ctk

from src.repositories.booking_repository import BookingRepository
from src.repositories.cleaner_repository import CleanerRepository
from src.ui.theme import APP_COLORS, APP_FONTS


class ScheduleView(ctk.CTkFrame):
    """Weekly schedule page translated from the  schedule layout."""

    def __init__(self, parent) -> None:
        super().__init__(parent, fg_color=APP_COLORS["background"])
        self.pack(fill="both", expand=True)

        self.week_start = self._start_of_week(datetime.now())
        self.cleaner_filter: ctk.CTkComboBox | None = None
        self.schedule_frame: ctk.CTkFrame | None = None

        self._build_page()

    def _build_page(self) -> None:
        self._build_header()
        self._build_controls()
        self._build_schedule_grid()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(28, 22))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            left,
            text="Schedule",
            text_color=APP_COLORS["foreground"],
            font=("Inter", 28, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="Weekly booking overview",
            text_color=APP_COLORS["muted_text"],
            font=APP_FONTS["body"],
        ).pack(anchor="w", pady=(4, 0))

        cleaners = CleanerRepository.find_all()
        cleaner_values = ["All Cleaners"] + [cleaner.full_name for cleaner in cleaners]

        self.cleaner_filter = ctk.CTkComboBox(
            header,
            values=cleaner_values,
            width=190,
            height=40,
            corner_radius=10,
            border_width=2,
            border_color=APP_COLORS["border"],
            fg_color=APP_COLORS["card"],
            button_color=APP_COLORS["muted"],
            button_hover_color=APP_COLORS["border"],
            text_color=APP_COLORS["foreground"],
            dropdown_fg_color=APP_COLORS["card"],
            dropdown_hover_color=APP_COLORS["accent"],
            dropdown_text_color=APP_COLORS["foreground"],
            state="readonly",
            command=lambda _value: self._refresh_schedule(),
        )
        self.cleaner_filter.set("All Cleaners")
        self.cleaner_filter.grid(row=0, column=1, sticky="e")

    def _build_controls(self) -> None:
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(fill="x", padx=30, pady=(0, 22))
        controls.grid_columnconfigure(1, weight=1)

        button_group = ctk.CTkFrame(controls, fg_color="transparent")
        button_group.grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            button_group,
            text="← Previous",
            width=110,
            height=38,
            corner_radius=10,
            fg_color=APP_COLORS["secondary"],
            text_color=APP_COLORS["secondary_text"],
            hover_color=APP_COLORS["border"],
            font=APP_FONTS["button"],
            command=self._previous_week,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            button_group,
            text="Today",
            width=90,
            height=38,
            corner_radius=10,
            fg_color=APP_COLORS["primary"],
            hover_color=APP_COLORS["primary_hover"],
            font=APP_FONTS["button"],
            command=self._today,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            button_group,
            text="Next →",
            width=110,
            height=38,
            corner_radius=10,
            fg_color=APP_COLORS["secondary"],
            text_color=APP_COLORS["secondary_text"],
            hover_color=APP_COLORS["border"],
            font=APP_FONTS["button"],
            command=self._next_week,
        ).pack(side="left")

        week_end = self.week_start + timedelta(days=6)

        ctk.CTkLabel(
            controls,
            text=f"{self.week_start.strftime('%b %d')} — {week_end.strftime('%b %d, %Y')}",
            text_color=APP_COLORS["muted_text"],
            font=("Inter", 14, "bold"),
        ).grid(row=0, column=2, sticky="e")

    def _build_schedule_grid(self) -> None:
        self.schedule_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.schedule_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        self._refresh_schedule()

    def _refresh_schedule(self) -> None:
        if self.schedule_frame is None:
            return

        for widget in self.schedule_frame.winfo_children():
            widget.destroy()

        days = [self.week_start + timedelta(days=index) for index in range(7)]

        for column, day in enumerate(days):
            self.schedule_frame.grid_columnconfigure(column, weight=1, uniform="days")

            day_column = ctk.CTkFrame(
                self.schedule_frame,
                fg_color="transparent",
            )
            day_column.grid(row=0, column=column, sticky="nsew", padx=6)

            is_today = day.date() == datetime.now().date()

            day_header = ctk.CTkFrame(
                day_column,
                fg_color=APP_COLORS["primary"] if is_today else APP_COLORS["muted"],
                corner_radius=12,
                height=72,
            )
            day_header.pack(fill="x", pady=(0, 12))
            day_header.pack_propagate(False)

            ctk.CTkLabel(
                day_header,
                text=day.strftime("%a"),
                text_color=APP_COLORS["primary_text"] if is_today else APP_COLORS["foreground"],
                font=("Inter", 12, "bold"),
            ).pack(pady=(10, 0))

            ctk.CTkLabel(
                day_header,
                text=day.strftime("%d"),
                text_color=APP_COLORS["primary_text"] if is_today else APP_COLORS["foreground"],
                font=("Inter", 22, "bold"),
            ).pack(pady=(0, 8))

            bookings = self._bookings_for_day(day)

            if not bookings:
                ctk.CTkLabel(
                    day_column,
                    text="No bookings",
                    text_color=APP_COLORS["muted_text"],
                    font=APP_FONTS["small"],
                ).pack(pady=20)
                continue

            for booking in bookings:
                self._booking_card(day_column, booking)

    def _booking_card(self, parent, booking) -> None:
        card = ctk.CTkFrame(
            parent,
            fg_color=APP_COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=APP_COLORS["border"],
        )
        card.pack(fill="x", pady=6)

        ctk.CTkLabel(
            card,
            text=booking.customer.full_name,
            text_color=APP_COLORS["foreground"],
            font=("Inter", 13, "bold"),
        ).pack(anchor="w", padx=12, pady=(12, 2))

        time_text = booking.booking_date.strftime("%H:%M")
        if getattr(booking, "end_time", None) is not None:
            time_text = f"{booking.booking_date.strftime('%H:%M')} – {booking.end_time.strftime('%H:%M')}"

        ctk.CTkLabel(
            card,
            text=time_text,
            text_color=APP_COLORS["muted_text"],
            font=APP_FONTS["small"],
        ).pack(anchor="w", padx=12)

        ctk.CTkLabel(
            card,
            text=self._short_text(booking.cleaning_service.service_name, 18),
            text_color=APP_COLORS["muted_text"],
            font=APP_FONTS["small"],
        ).pack(anchor="w", padx=12, pady=(2, 0))

        ctk.CTkLabel(
            card,
            text=booking.cleaner.full_name,
            text_color=APP_COLORS["primary"],
            font=("Inter", 11, "bold"),
        ).pack(anchor="w", padx=12, pady=(4, 6))

        status_bg, status_fg = self._status_colours(booking.status)

        ctk.CTkLabel(
            card,
            text=str(booking.status),
            text_color=status_fg,
            fg_color=status_bg,
            corner_radius=8,
            height=24,
            font=("Inter", 11, "bold"),
        ).pack(anchor="w", padx=12, pady=(0, 12), ipadx=10)

    def _bookings_for_day(self, day: datetime) -> list:
        selected_cleaner = "All Cleaners"

        if self.cleaner_filter is not None:
            selected_cleaner = self.cleaner_filter.get()

        result = []

        for booking in BookingRepository.find_all():
            same_day = booking.booking_date.date() == day.date()
            same_cleaner = (
                selected_cleaner == "All Cleaners"
                or booking.cleaner.full_name == selected_cleaner
            )

            if same_day and same_cleaner:
                result.append(booking)

        return sorted(result, key=lambda booking: booking.booking_date)

    def _previous_week(self) -> None:
        self.week_start -= timedelta(days=7)
        self._rebuild_page()

    def _next_week(self) -> None:
        self.week_start += timedelta(days=7)
        self._rebuild_page()

    def _today(self) -> None:
        self.week_start = self._start_of_week(datetime.now())
        self._rebuild_page()

    def _rebuild_page(self) -> None:
        selected_cleaner = "All Cleaners"

        if self.cleaner_filter is not None:
            selected_cleaner = self.cleaner_filter.get()

        for widget in self.winfo_children():
            widget.destroy()

        self._build_page()

        if self.cleaner_filter is not None:
            self.cleaner_filter.set(selected_cleaner)

        self._refresh_schedule()

    @staticmethod
    def _start_of_week(date_value: datetime) -> datetime:
        return date_value - timedelta(days=date_value.weekday())

    @staticmethod
    def _short_text(text: str, limit: int) -> str:
        if len(text) <= limit:
            return text
        return text[:limit].rstrip() + "..."

    @staticmethod
    def _status_colours(status: str) -> tuple[str, str]:
        status_text = str(status).lower()

        if status_text == "confirmed":
            return "#dbeafe", "#2563eb"
        if status_text in {"in progress", "in_progress"}:
            return "#ede9fe", "#6d28d9"
        if status_text == "pending":
            return "#fef3c7", "#b45309"
        if status_text == "completed":
            return "#dcfce7", "#059669"
        return "#fee2e2", APP_COLORS["danger"]
