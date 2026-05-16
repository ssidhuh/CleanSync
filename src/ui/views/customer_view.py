"""Customers view for the CleanSync desktop application."""

from __future__ import annotations

import re
from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from src.models.base_entity import BaseEntity
from src.models.customer import Customer
from src.repositories.customer_repository import CustomerRepository
from src.ui.theme import APP_COLORS, APP_FONTS


class CustomersView(ctk.CTkFrame):
    """Customers page with searchable table and modal customer form."""

    def __init__(self, parent) -> None:
        super().__init__(parent, fg_color=APP_COLORS["background"])
        self.pack(fill="both", expand=True)

        self.search_entry: ctk.CTkEntry | None = None
        self.count_label: ctk.CTkLabel | None = None
        self.table_frame: ctk.CTkFrame | None = None

        self._build_page()

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
            text="Customers",
            text_color=APP_COLORS["foreground"],
            font=("Inter", 28, "bold"),
        ).pack(anchor="w")

        self.count_label = ctk.CTkLabel(
            left,
            text=f"{len(CustomerRepository.find_all())} total customers",
            text_color=APP_COLORS["muted_text"],
            font=APP_FONTS["body"],
        )
        self.count_label.pack(anchor="w", pady=(4, 0))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")

        self.search_entry = ctk.CTkEntry(
            right,
            placeholder_text="Search...",
            width=250,
            height=40,
            corner_radius=10,
            border_color=APP_COLORS["border"],
        )
        self.search_entry.pack(side="left", padx=(0, 12))
        self.search_entry.bind("<KeyRelease>", lambda _event: self._refresh_table())

        ctk.CTkButton(
            right,
            text="+  Add Customer",
            width=160,
            height=40,
            corner_radius=10,
            fg_color=APP_COLORS["primary"],
            hover_color=APP_COLORS["primary_hover"],
            font=APP_FONTS["button"],
            command=lambda: self._open_customer_modal(),
        ).pack(side="left")

    def _build_table(self) -> None:
        self.table_frame = ctk.CTkFrame(
            self,
            fg_color=APP_COLORS["card"],
            corner_radius=16,
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

        customers = self._filtered_customers()

        headers = ["Name", "Email", "Phone", "Address", "Status", "Actions"]
        weights = [2, 2, 2, 2, 1, 1]

        for column, weight in enumerate(weights):
            self.table_frame.grid_columnconfigure(column, weight=weight)

        for column, header in enumerate(headers):
            ctk.CTkLabel(
                self.table_frame,
                text=header.upper(),
                text_color=APP_COLORS["muted_text"],
                font=("Inter", 11, "bold"),
            ).grid(row=0, column=column, sticky="w", padx=14, pady=(16, 10))

        if not customers:
            ctk.CTkLabel(
                self.table_frame,
                text="No customers found. Add your first customer using the button above.",
                text_color=APP_COLORS["muted_text"],
                font=APP_FONTS["body"],
            ).grid(row=1, column=0, columnspan=6, pady=60)
            return

        for row_index, customer in enumerate(customers, start=1):
            self._table_label(row_index, 0, customer.full_name, bold=True)
            self._table_label(row_index, 1, customer.email)
            self._table_label(row_index, 2, customer.phone_number)
            self._table_label(row_index, 3, customer.address)

            status = ctk.CTkLabel(
                self.table_frame,
                text="Active",
                text_color=APP_COLORS["success"],
                fg_color="#dcfce7",
                corner_radius=10,
                width=70,
                height=24,
                font=APP_FONTS["small"],
            )
            status.grid(row=row_index, column=4, sticky="w", padx=14, pady=9)

            actions = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            actions.grid(row=row_index, column=5, sticky="w", padx=14, pady=8)

            ctk.CTkButton(
                actions,
                text="Edit",
                width=58,
                height=28,
                fg_color=APP_COLORS["secondary"],
                hover_color=APP_COLORS["border"],
                text_color=APP_COLORS["foreground"],
                command=lambda selected=customer: self._open_customer_modal(selected),
            ).pack(side="left", padx=(0, 6))

            ctk.CTkButton(
                actions,
                text="Delete",
                width=66,
                height=28,
                fg_color=APP_COLORS["danger"],
                hover_color=APP_COLORS["danger_hover"],
                command=lambda selected=customer: self._delete_customer(selected),
            ).pack(side="left")

    def _table_label(self, row: int, column: int, text: str, bold: bool = False) -> None:
        ctk.CTkLabel(
            self.table_frame,
            text=text,
            text_color=APP_COLORS["foreground"],
            font=("Inter", 13, "bold") if bold else APP_FONTS["body"],
        ).grid(row=row, column=column, sticky="w", padx=14, pady=12)

    def _filtered_customers(self) -> list[Customer]:
        search_text = ""

        if self.search_entry is not None:
            search_text = self.search_entry.get().strip().lower()

        customers = CustomerRepository.find_all()

        if not search_text:
            return customers

        return [
            customer
            for customer in customers
            if search_text in customer.full_name.lower()
            or search_text in customer.email.lower()
            or search_text in customer.phone_number.lower()
            or search_text in customer.address.lower()
        ]

    def _open_customer_modal(self, customer: Customer | None = None) -> None:
        modal = ctk.CTkToplevel(self)
        modal.title("Edit Customer" if customer else "New Customer")
        modal.geometry("520x650")
        modal.resizable(False, False)
        modal.grab_set()

        card = ctk.CTkFrame(
            modal,
            fg_color=APP_COLORS["card"],
            corner_radius=16,
        )
        card.pack(fill="both", expand=True, padx=18, pady=18)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=22, pady=(20, 14))

        ctk.CTkLabel(
            top,
            text="Edit Customer" if customer else "New Customer",
            text_color=APP_COLORS["foreground"],
            font=APP_FONTS["subheading"],
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

        fields = ctk.CTkFrame(card, fg_color="transparent")
        fields.pack(fill="x", padx=22, pady=(0, 10))

        entries: dict[str, ctk.CTkEntry] = {}

        entries["First Name"] = self._modal_entry(fields, "First Name *")
        entries["Last Name"] = self._modal_entry(fields, "Last Name *")
        entries["Email"] = self._modal_entry(fields, "Email *")
        entries["Phone Number"] = self._modal_entry(fields, "Phone Number *")
        entries["Address"] = self._modal_entry(fields, "Address *")

        if customer is not None:
            entries["First Name"].insert(0, customer.first_name)
            entries["Last Name"].insert(0, customer.last_name)
            entries["Email"].insert(0, customer.email)
            entries["Phone Number"].insert(0, customer.phone_number)
            entries["Address"].insert(0, customer.address)

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.pack(fill="x", padx=22, pady=(18, 20))

        ctk.CTkButton(
            buttons,
            text="Cancel",
            height=44,
            corner_radius=10,
            fg_color=APP_COLORS["secondary"],
            hover_color=APP_COLORS["border"],
            text_color=APP_COLORS["foreground"],
            font=APP_FONTS["button"],
            command=modal.destroy,
        ).pack(side="left", fill="x", expand=True, padx=(8, 0))

        ctk.CTkButton(
            buttons,
            text="Save",
            height=44,
            corner_radius=10,
            fg_color=APP_COLORS["primary"],
            hover_color=APP_COLORS["primary_hover"],
            font=APP_FONTS["button"],
            command=lambda: self._save_customer(entries, modal, customer),
        ).pack(side="right", fill="x", expand=True, padx=(0, 8))

    def _modal_entry(self, parent, label: str) -> ctk.CTkEntry:
        ctk.CTkLabel(
            parent,
            text=label,
            text_color=APP_COLORS["foreground"],
            font=APP_FONTS["small"],
        ).pack(anchor="w", pady=(8, 4))

        entry = ctk.CTkEntry(
            parent,
            height=40,
            corner_radius=10,
            border_color=APP_COLORS["border"],
        )
        entry.pack(fill="x", pady=(0, 4))
        return entry

    def _save_customer(
        self,
        entries: dict[str, ctk.CTkEntry],
        modal: ctk.CTkToplevel,
        existing_customer: Customer | None,
    ) -> None:
        values = {field: entry.get().strip() for field, entry in entries.items()}

        if not all(values.values()):
            self._error("Please complete all required fields.")
            return

        first_name = values["First Name"]
        last_name = values["Last Name"]
        email = values["Email"]
        phone_number = values["Phone Number"]
        address = values["Address"]

        if len(first_name) < 2 or not first_name.replace(" ", "").isalpha():
            self._error("First name must contain valid letters only.")
            return

        if len(last_name) < 2 or not last_name.replace(" ", "").isalpha():
            self._error("Last name must contain valid letters only.")
            return

        email_pattern = (
            r"^[A-Za-z0-9._%+-]+@"
            r"(gmail|yahoo|outlook|hotmail|icloud|protonmail|inbox)"
            r"\.(com|lv|co\.uk|org|net)$"
        )

        if not re.match(email_pattern, email.lower()):
            self._error(
                "Please enter a valid email address "
                "(example: name@gmail.com)."
            )
            return

        cleaned_phone = (
            phone_number.replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
            .replace("+", "")
        )

        if not cleaned_phone.isdigit():
            self._error("Phone number must contain digits only.")
            return

        if len(cleaned_phone) < 8 or len(cleaned_phone) > 15:
            self._error("Phone number must contain 8–15 digits.")
            return

        if len(address) < 8:
            self._error("Address must be at least 8 characters long.")
            return

        if not any(character.isalpha() for character in address):
            self._error("Address must contain letters.")
            return

        if not any (character.isdigit() for character in address):
            self._error("Address must contain street or building number.")
            return

        invalid_patterns = ["asdf", "qwer", "zxcv", "test", "abc"]

        if any(pattern in address.lower() for pattern in invalid_patterns):
             self._error("Please enter a realistic address.")
             return



        customer = Customer(
            entity_id=existing_customer.entity_id if existing_customer else BaseEntity.generate_id(),
            created_at=existing_customer.created_at if existing_customer else datetime.now(),
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            address=address,
        )

        CustomerRepository.save_customer(customer)
        modal.destroy()
        self._refresh_page()

    def _delete_customer(self, customer: Customer) -> None:
        confirmed = messagebox.askyesno(
            "Delete Customer",
            f"Delete {customer.full_name}?",
        )

        if not confirmed:
            return

        CustomerRepository.delete(customer.entity_id)
        self._refresh_page()

    def _refresh_page(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

        self.search_entry = None
        self.count_label = None
        self.table_frame = None

        self._build_page()

    @staticmethod
    def _error(message: str) -> None:
        messagebox.showerror("Validation Error", message)
