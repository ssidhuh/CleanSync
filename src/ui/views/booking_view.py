"""Bookings view for the CleanSync desktop application."""

from __future__ import annotations

from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from src.models.base_entity import BaseEntity
from src.models.booking import Booking
from src.repositories.booking_repository import BookingRepository
from src.repositories.cleaner_repository import CleanerRepository
from src.repositories.customer_repository import CustomerRepository
from src.repositories.service_repository import ServiceRepository
from src.ui.theme import APP_COLORS, APP_FONTS


BOOKING_STATUSES = ["Pending", "Confirmed", "In Progress", "Completed", "Cancelled"]


class BookingsView(ctk.CTkFrame):
    """Bookings page with Base44-style table and modal booking workflow."""

    def __init__(self, parent) -> None:
        super().__init__(parent, fg_color=APP_COLORS["background"])
        self.pack(fill="both", expand=True)

        self.search_entry: ctk.CTkEntry | None = None
        self.status_filter: ctk.CTkComboBox | None = None
        self.table_frame: ctk.CTkFrame | None = None

        self._reload_data()
        self._build_page()

    def _reload_data(self) -> None:
        self.customers = CustomerRepository.find_all()
        self.cleaners = CleanerRepository.find_all()
        self.services = ServiceRepository.find_all()
        self.bookings = BookingRepository.find_all()

    def _build_page(self) -> None:
        self._build_header()
        self._build_table()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(28, 22))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            left,
            text="Bookings",
            text_color=APP_COLORS["foreground"],
            font=("Inter", 28, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text=f"{len(self.bookings)} total bookings",
            text_color=APP_COLORS["muted_text"],
            font=APP_FONTS["body"],
        ).pack(anchor="w", pady=(4, 0))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")

        self.search_entry = ctk.CTkEntry(
            right,
            placeholder_text="Search...",
            width=210,
            height=40,
            corner_radius=10,
            border_color=APP_COLORS["border"],
        )
        self.search_entry.pack(side="left", padx=(0, 12))
        self.search_entry.bind("<KeyRelease>", lambda _event: self._refresh_table())

        self.status_filter = ctk.CTkComboBox(
            right,
            values=["All Status"] + BOOKING_STATUSES,
            width=150,
            height=40,
            corner_radius=10,
            border_width=1,
            border_color=APP_COLORS["border"],
            fg_color=APP_COLORS["card"],
            button_color=APP_COLORS["card"],
            button_hover_color=APP_COLORS["muted"],
            text_color=APP_COLORS["foreground"],
            dropdown_fg_color=APP_COLORS["card"],
            dropdown_hover_color=APP_COLORS["accent"],
            dropdown_text_color=APP_COLORS["foreground"],
            state="readonly",
            command=lambda _value: self._refresh_table(),
        )
        self.status_filter.set("All Status")
        self.status_filter.pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            right,
            text="+  New Booking",
            width=160,
            height=40,
            corner_radius=10,
            fg_color=APP_COLORS["primary"],
            hover_color=APP_COLORS["primary_hover"],
            font=APP_FONTS["button"],
            command=lambda: self._open_modal(),
        ).pack(side="left")

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

        rows = self._filtered_bookings()

        headers = ["CUSTOMER", "CLEANER", "SERVICE", "DATE", "TIME", "AMOUNT", "STATUS", ""]
        widths = [150, 140, 180, 120, 130, 90, 130, 80]

        for column, header in enumerate(headers):
            self.table_frame.grid_columnconfigure(column, weight=1, minsize=widths[column])
            ctk.CTkLabel(
                self.table_frame,
                text=header,
                text_color=APP_COLORS["muted_text"],
                font=("Inter", 11, "bold"),
            ).grid(row=0, column=column, sticky="w", padx=10, pady=(16, 10))

        if not rows:
            ctk.CTkLabel(
                self.table_frame,
                text="No bookings found. Create your first booking above.",
                text_color=APP_COLORS["muted_text"],
                font=APP_FONTS["body"],
            ).grid(row=1, column=0, columnspan=8, pady=80)
            return

        for row_index, booking in enumerate(rows, start=1):
            self._table_row(booking, row_index)

    def _table_row(self, booking: Booking, row_index: int) -> None:
        time_text = booking.booking_date.strftime("%H:%M")
        if booking.end_time is not None:
            time_text = f"{booking.booking_date.strftime('%H:%M')} – {booking.end_time.strftime('%H:%M')}"

        amount = booking.total_amount or booking.cleaning_service.base_price

        values = [
            booking.customer.full_name,
            booking.cleaner.full_name,
            booking.cleaning_service.service_name,
            booking.booking_date.strftime("%b %d, %Y"),
            time_text,
            f"${amount:.0f}",
        ]

        for column, value in enumerate(values):
            ctk.CTkLabel(
                self.table_frame,
                text=value,
                text_color=APP_COLORS["foreground"],
                font=("Inter", 13, "bold" if column in [0, 5] else "normal"),
            ).grid(row=row_index, column=column, sticky="w", padx=10, pady=12)

        status_bg, status_fg = self._status_colours(booking.status)

        ctk.CTkLabel(
            self.table_frame,
            text=booking.status,
            text_color=status_fg,
            fg_color=status_bg,
            corner_radius=8,
            height=24,
            width=96,
            font=("Inter", 11, "bold"),
        ).grid(row=row_index, column=6, sticky="w", padx=10, pady=12)

        actions = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        actions.grid(row=row_index, column=7, sticky="w", padx=10, pady=8)

        ctk.CTkButton(
            actions,
            text="✎",
            width=30,
            height=28,
            fg_color="transparent",
            hover_color=APP_COLORS["muted"],
            text_color=APP_COLORS["foreground"],
            command=lambda selected=booking: self._open_modal(selected),
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            actions,
            text="🗑",
            width=30,
            height=28,
            fg_color="transparent",
            hover_color=APP_COLORS["muted"],
            text_color=APP_COLORS["danger"],
            command=lambda selected=booking: self._delete_booking(selected),
        ).pack(side="left")

    def _open_modal(self, booking: Booking | None = None) -> None:
        self._reload_data()

        modal = ctk.CTkToplevel(self)
        modal.title("Edit Booking" if booking else "New Booking")
        modal.geometry("560x690")
        modal.resizable(False, False)
        modal.grab_set()

        card = ctk.CTkFrame(modal, fg_color=APP_COLORS["card"], corner_radius=16)
        card.pack(fill="both", expand=True, padx=18, pady=18)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=22, pady=(20, 12))

        ctk.CTkLabel(
            top,
            text="Edit Booking" if booking else "New Booking",
            text_color=APP_COLORS["foreground"],
            font=("Inter", 20, "bold"),
        ).pack(side="left")

        ctk.CTkButton(
            top,
            text="×",
            width=34,
            height=30,
            fg_color="transparent",
            hover_color=APP_COLORS["muted"],
            text_color=APP_COLORS["muted_text"],
            command=modal.destroy,
        ).pack(side="right")

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=22)

        customer_var = ctk.StringVar(value=booking.customer.full_name if booking else "Select customer")
        cleaner_var = ctk.StringVar(value=booking.cleaner.full_name if booking else "Select cleaner")
        service_var = ctk.StringVar(value=booking.cleaning_service.service_name if booking else "Select service")
        status_var = ctk.StringVar(value=booking.status if booking else "Pending")

        row_one = ctk.CTkFrame(body, fg_color="transparent")
        row_one.pack(fill="x")
        row_one.grid_columnconfigure((0, 1), weight=1)

        self._modal_combo(
            row_one,
            "Customer *",
            customer_var,
            [customer.full_name for customer in self.customers],
            0,
            0,
        )

        cleaner_combo = self._modal_combo(
            row_one,
            "Cleaner *",
            cleaner_var,
            [cleaner.full_name for cleaner in self.cleaners],
            0,
            1,
        )

        service_combo = self._modal_combo(
            body,
            "Service *",
            service_var,
            self._service_names_for_cleaner(cleaner_var.get()),
        )

        def update_services_for_cleaner(selected_cleaner: str) -> None:
            updated_services = self._service_names_for_cleaner(selected_cleaner)
            service_var.set("Select service")
            service_combo.configure(values=updated_services)

        cleaner_combo.configure(command=update_services_for_cleaner)

        row_two = ctk.CTkFrame(body, fg_color="transparent")
        row_two.pack(fill="x")
        row_two.grid_columnconfigure((0, 1, 2), weight=1)

        date_entry = self._modal_entry_grid(row_two, "Date *", 0, 0)
        start_entry = self._modal_entry_grid(row_two, "Start Time *", 0, 1)
        end_entry = self._modal_entry_grid(row_two, "End Time", 0, 2)

        if booking is not None:
            date_entry.insert(0, booking.booking_date.strftime("%d/%m/%Y"))
            start_entry.insert(0, booking.booking_date.strftime("%I:%M %p"))
            if booking.end_time is not None:
                end_entry.insert(0, booking.end_time.strftime("%I:%M %p"))
        else:
            date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
            start_entry.insert(0, "12:30 PM")
            end_entry.insert(0, "12:30 PM")

        row_three = ctk.CTkFrame(body, fg_color="transparent")
        row_three.pack(fill="x")
        row_three.grid_columnconfigure((0, 1), weight=1)

        address_entry = self._modal_entry_grid(row_three, "Address", 0, 0)
        amount_entry = self._modal_entry_grid(row_three, "Total Amount ($)", 0, 1)

        if booking is not None:
            address_entry.insert(0, booking.address)
            amount_entry.insert(0, str(booking.total_amount or booking.cleaning_service.base_price))

        self._modal_combo(body, "Status", status_var, BOOKING_STATUSES)

        ctk.CTkLabel(
            body,
            text="Notes",
            text_color=APP_COLORS["foreground"],
            font=APP_FONTS["small"],
        ).pack(anchor="w", pady=(12, 4))

        notes_entry = ctk.CTkTextbox(
            body,
            height=64,
            corner_radius=10,
            border_width=1,
            border_color=APP_COLORS["border"],
            fg_color=APP_COLORS["card"],
            text_color=APP_COLORS["foreground"],
        )
        notes_entry.pack(fill="x")

        if booking is not None and booking.notes:
            notes_entry.insert("1.0", booking.notes)

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.pack(fill="x", padx=22, pady=(16, 20))

        ctk.CTkButton(
            buttons,
            text="Save",
            width=80,
            height=40,
            corner_radius=10,
            fg_color="#9bd3f0",
            hover_color=APP_COLORS["primary"],
            text_color="#ffffff",
            font=APP_FONTS["button"],
            command=lambda: self._save_booking(
                modal,
                booking,
                customer_var,
                cleaner_var,
                service_var,
                date_entry,
                start_entry,
                end_entry,
                address_entry,
                amount_entry,
                status_var,
                notes_entry,
            ),
        ).pack(side="right")

        ctk.CTkButton(
            buttons,
            text="Cancel",
            width=90,
            height=40,
            corner_radius=10,
            fg_color=APP_COLORS["card"],
            hover_color=APP_COLORS["muted"],
            text_color=APP_COLORS["foreground"],
            border_width=1,
            border_color=APP_COLORS["border"],
            font=APP_FONTS["button"],
            command=modal.destroy,
        ).pack(side="right", padx=(0, 10))

    def _save_booking(
        self,
        modal: ctk.CTkToplevel,
        existing_booking: Booking | None,
        customer_var: ctk.StringVar,
        cleaner_var: ctk.StringVar,
        service_var: ctk.StringVar,
        date_entry: ctk.CTkEntry,
        start_entry: ctk.CTkEntry,
        end_entry: ctk.CTkEntry,
        address_entry: ctk.CTkEntry,
        amount_entry: ctk.CTkEntry,
        status_var: ctk.StringVar,
        notes_entry: ctk.CTkTextbox,
    ) -> None:
        customer = self._find_by_name(self.customers, customer_var.get(), "full_name")
        cleaner = self._find_by_name(self.cleaners, cleaner_var.get(), "full_name")
        service = self._find_by_name(self.services, service_var.get(), "service_name")

        if customer is None or cleaner is None or service is None:
            self._error("Please select a customer, cleaner, and service.")
            return

        allowed_services = self._service_names_for_cleaner(cleaner.full_name)

        if service.service_name not in allowed_services:
            self._error("This cleaner does not offer the selected service.")
            return

        try:
            booking_date = datetime.strptime(
                f"{date_entry.get().strip()} {start_entry.get().strip()}",
                "%d/%m/%Y %I:%M %p",
            )
            end_time = datetime.strptime(
                f"{date_entry.get().strip()} {end_entry.get().strip()}",
                "%d/%m/%Y %I:%M %p",
            )
        except ValueError:
            self._error("Date must be DD/MM/YYYY and time must be like 12:30 PM.")
            return

        try:
            total_amount = (
                float(amount_entry.get().strip())
                if amount_entry.get().strip()
                else service.base_price
            )
        except ValueError:
            self._error("Total amount must be a valid number.")
            return

        booking = Booking(
            entity_id=existing_booking.entity_id if existing_booking else BaseEntity.generate_id(),
            created_at=existing_booking.created_at if existing_booking else datetime.now(),
            customer=customer,
            cleaner=cleaner,
            cleaning_service=service,
            booking_date=booking_date,
            end_time=end_time,
            address=address_entry.get().strip(),
            total_amount=total_amount,
            notes=notes_entry.get("1.0", "end").strip(),
            status=status_var.get(),
        )

        BookingRepository.save_booking(booking)
        modal.destroy()
        self._refresh_whole_page()

    def _delete_booking(self, booking: Booking) -> None:
        confirmed = messagebox.askyesno(
            "Delete Booking",
            f"Delete booking for {booking.customer.full_name}?",
        )

        if not confirmed:
            return

        BookingRepository.delete(booking.entity_id)
        self._refresh_whole_page()

    def _filtered_bookings(self) -> list[Booking]:
        search_text = self.search_entry.get().strip().lower() if self.search_entry else ""
        selected_status = self.status_filter.get() if self.status_filter else "All Status"

        filtered = []

        for booking in BookingRepository.find_all():
            searchable = (
                f"{booking.customer.full_name} "
                f"{booking.cleaner.full_name} "
                f"{booking.cleaning_service.service_name} "
                f"{booking.status}"
            ).lower()

            matches_search = not search_text or search_text in searchable
            matches_status = selected_status == "All Status" or booking.status == selected_status

            if matches_search and matches_status:
                filtered.append(booking)

        return filtered

    def _refresh_whole_page(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

        self.search_entry = None
        self.status_filter = None
        self.table_frame = None

        self._reload_data()
        self._build_page()

    def _service_names_for_cleaner(self, cleaner_name: str) -> list[str]:
        cleaner = self._find_by_name(self.cleaners, cleaner_name, "full_name")

        if cleaner is None:
            return ["Select cleaner first"]

        cleaner_specializations = cleaner.specializations.strip().lower()

        if not cleaner_specializations:
            return ["No services available"]

        cleaner_tokens = [
            item.strip()
            for item in cleaner_specializations.replace(";", ",").replace("|", ",").split(",")
            if item.strip()
        ]

        matching_services = []

        for service in self.services:
            service_name = service.service_name.strip().lower()
            service_description = service.description.strip().lower()

            for token in cleaner_tokens:
                if (
                    token == service_name
                    or token in service_name
                    or service_name in token
                    or token in service_description
                ):
                    matching_services.append(service.service_name)
                    break

        return matching_services if matching_services else ["No services available"]

    def _modal_combo(
        self,
        parent,
        label: str,
        variable: ctk.StringVar,
        values: list[str],
        row: int | None = None,
        column: int | None = None,
        command=None,
    ) -> ctk.CTkComboBox:
        frame = ctk.CTkFrame(parent, fg_color="transparent")

        if row is None or column is None:
            frame.pack(fill="x", pady=(8, 0))
        else:
            frame.grid(row=row, column=column, sticky="ew", padx=(0, 8) if column == 0 else (8, 0))

        ctk.CTkLabel(
            frame,
            text=label,
            text_color=APP_COLORS["foreground"],
            font=APP_FONTS["small"],
        ).pack(anchor="w", pady=(0, 4))

        combo = ctk.CTkComboBox(
            frame,
            values=values if values else ["No records available"],
            variable=variable,
            height=40,
            corner_radius=10,
            border_width=1,
            border_color=APP_COLORS["border"],
            fg_color=APP_COLORS["card"],
            button_color=APP_COLORS["card"],
            button_hover_color=APP_COLORS["muted"],
            text_color=APP_COLORS["foreground"],
            dropdown_fg_color=APP_COLORS["card"],
            dropdown_hover_color=APP_COLORS["accent"],
            dropdown_text_color=APP_COLORS["foreground"],
            state="readonly",
            command=command,
        )
        combo.pack(fill="x")
        return combo

    def _modal_entry_grid(self, parent, label: str, row: int, column: int) -> ctk.CTkEntry:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=column, sticky="ew", padx=(0, 8) if column == 0 else (8, 0))

        ctk.CTkLabel(
            frame,
            text=label,
            text_color=APP_COLORS["foreground"],
            font=APP_FONTS["small"],
        ).pack(anchor="w", pady=(12, 4))

        entry = ctk.CTkEntry(
            frame,
            height=40,
            corner_radius=10,
            border_color=APP_COLORS["border"],
        )
        entry.pack(fill="x")
        return entry

    @staticmethod
    def _find_by_name(items: list, name: str, attribute: str):
        for item in items:
            if getattr(item, attribute) == name:
                return item
        return None

    @staticmethod
    def _status_colours(status: str) -> tuple[str, str]:
        if status == "Confirmed":
            return "#dbeafe", "#2563eb"
        if status == "In Progress":
            return "#ede9fe", "#6d28d9"
        if status == "Pending":
            return "#fef3c7", "#b45309"
        if status == "Completed":
            return "#dcfce7", "#059669"
        return "#fee2e2", APP_COLORS["danger"]

    @staticmethod
    def _error(message: str) -> None:
        messagebox.showerror("Validation Error", message)