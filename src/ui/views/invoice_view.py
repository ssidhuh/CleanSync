"""Invoices view for the CleanSync desktop application."""

from __future__ import annotations

from datetime import datetime, timedelta
from tkinter import messagebox

import customtkinter as ctk

from src.models.base_entity import BaseEntity
from src.models.invoice import Invoice
from src.repositories.booking_repository import BookingRepository
from src.repositories.invoice_repository import InvoiceRepository
from src.ui.theme import APP_COLORS, APP_FONTS

INVOICE_STATUSES = ["draft", "sent", "paid", "overdue", "cancelled"]


class InvoicesView(ctk.CTkFrame):
    """Invoices page with  table and modal invoice workflow."""

    def __init__(self, parent) -> None:
        super().__init__(parent, fg_color=APP_COLORS["background"])
        self.pack(fill="both", expand=True)

        self.search_entry: ctk.CTkEntry | None = None
        self.table_frame: ctk.CTkFrame | None = None

        self._reload_data()
        self._build_page()

    def _reload_data(self) -> None:
        self.bookings = BookingRepository.find_all()
        self.invoices = InvoiceRepository.find_all()

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
            text="Invoices",
            text_color=APP_COLORS["foreground"],
            font=("Inter", 28, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text=f"{len(self.invoices)} total invoices",
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

        ctk.CTkButton(
            right,
            text="+  New Invoice",
            width=160,
            height=40,
            corner_radius=10,
            fg_color=APP_COLORS["primary"],
            hover_color=APP_COLORS["primary_hover"],
            font=APP_FONTS["button"],
            command=self._open_modal,
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

        invoices = self._filtered_invoices()
        headers = ["INVOICE #", "CUSTOMER", "AMOUNT", "DUE DATE", "STATUS", ""]
        widths = [150, 220, 140, 170, 140, 90]

        for column, header in enumerate(headers):
            self.table_frame.grid_columnconfigure(column, weight=1, minsize=widths[column])
            ctk.CTkLabel(
                self.table_frame,
                text=header,
                text_color=APP_COLORS["muted_text"],
                font=("Inter", 11, "bold"),
            ).grid(row=0, column=column, sticky="w", padx=10, pady=(16, 10))

        self._table_separator(1)

        if not invoices:
            ctk.CTkLabel(
                self.table_frame,
                text="No invoices found. Create your first invoice above.",
                text_color=APP_COLORS["muted_text"],
                font=APP_FONTS["body"],
            ).grid(row=2, column=0, columnspan=6, pady=80)
            return

        for index, invoice in enumerate(invoices):
            row_number = 2 + (index * 2)
            self._table_row(invoice, row_number)
            self._table_separator(row_number + 1)

    def _table_separator(self, row: int) -> None:
        if self.table_frame is None:
            return

        ctk.CTkFrame(
            self.table_frame,
            fg_color=APP_COLORS["border"],
            height=1,
        ).grid(row=row, column=0, columnspan=6, sticky="ew")

    def _table_row(self, invoice: Invoice, row_index: int) -> None:
        due_date = invoice.due_date.strftime("%b %d, %Y") if invoice.due_date else "No due date"

        values = [
            invoice.invoice_number or invoice.entity_id[:8],
            invoice.booking.customer.full_name,
            f"€{invoice.total_amount:.2f}",
            due_date,
        ]

        for column, value in enumerate(values):
            ctk.CTkLabel(
                self.table_frame,
                text=value,
                text_color=APP_COLORS["foreground"],
                font=("Inter", 13, "bold" if column in [1, 2] else "normal"),
            ).grid(row=row_index, column=column, sticky="w", padx=10, pady=12)

        status_bg, status_fg = self._status_colours(invoice.payment_status)

        ctk.CTkLabel(
            self.table_frame,
            text=invoice.payment_status.title(),
            text_color=status_fg,
            fg_color=status_bg,
            corner_radius=8,
            height=24,
            width=70,
            font=("Inter", 11, "bold"),
        ).grid(row=row_index, column=4, sticky="w", padx=10, pady=12)

        actions = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        actions.grid(row=row_index, column=5, sticky="w", padx=10, pady=8)

        ctk.CTkButton(
            actions,
            text="✎",
            width=30,
            height=28,
            fg_color="transparent",
            hover_color=APP_COLORS["muted"],
            text_color=APP_COLORS["foreground"],
            command=lambda selected=invoice: self._open_modal(selected),
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            actions,
            text="🗑",
            width=30,
            height=28,
            fg_color="transparent",
            hover_color=APP_COLORS["muted"],
            text_color=APP_COLORS["danger"],
            command=lambda selected=invoice: self._delete_invoice(selected),
        ).pack(side="left")

    def _open_modal(self, invoice: Invoice | None = None) -> None:
        self._reload_data()

        modal = ctk.CTkToplevel(self)
        modal.title("Edit Invoice" if invoice else "New Invoice")
        modal.geometry("700x650")
        modal.resizable(False, False)
        modal.grab_set()

        card = ctk.CTkFrame(modal, fg_color=APP_COLORS["card"], corner_radius=16)
        card.pack(fill="both", expand=True, padx=18, pady=18)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=22, pady=(20, 12))

        ctk.CTkLabel(
            top,
            text="Edit Invoice" if invoice else "New Invoice",
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

        row_one = ctk.CTkFrame(body, fg_color="transparent")
        row_one.pack(fill="x")
        row_one.grid_columnconfigure((0, 1, 2), weight=1)

        invoice_number_entry = self._modal_entry_grid(row_one, "Invoice #", 0, 0)

        customer_var = ctk.StringVar(value="Select booking")
        if invoice is not None:
            customer_var.set(
                f"{invoice.booking.booking_number} - "
                f"{invoice.booking.customer.full_name}"
            )

        customer_combo = self._modal_combo(
            row_one,
            "Customer *",
            customer_var,
            [
                f"{booking.booking_number} - "
                f"{booking.customer.full_name}"
                for booking in self.bookings
            ],
            0,
            1,
        )

        due_date_entry = self._modal_entry_grid(row_one, "Due Date", 0, 2)

        if invoice is not None:
            invoice_number_entry.insert(0, invoice.invoice_number)
            if invoice.due_date is not None:
                due_date_entry.insert(0, invoice.due_date.strftime("%d/%m/%Y"))
        else:
            if self.bookings:
                invoice_number_entry.insert(0, self._next_invoice_number(self.bookings[0]))
            else:
                invoice_number_entry.insert(0, "INV-0001")

            due_date_entry.insert(0, (datetime.now() + timedelta(days=5)).strftime("%d/%m/%Y"))

        ctk.CTkLabel(
            body,
            text="Line Items",
            text_color=APP_COLORS["foreground"],
            font=APP_FONTS["small"],
        ).pack(anchor="w", pady=(16, 4))

        line_items_frame = ctk.CTkFrame(body, fg_color="transparent")
        line_items_frame.pack(fill="x")

        line_items: list[dict[str, object]] = []

        ctk.CTkButton(
            body,
            text="+  Add Item",
            width=110,
            height=34,
            corner_radius=8,
            fg_color=APP_COLORS["card"],
            hover_color=APP_COLORS["muted"],
            text_color=APP_COLORS["foreground"],
            border_width=1,
            border_color=APP_COLORS["border"],
            font=APP_FONTS["button"],
            command=lambda: add_line_item(),
        ).pack(anchor="w", pady=(8, 12))

        totals = ctk.CTkFrame(body, fg_color="transparent")
        totals.pack(fill="x")
        totals.grid_columnconfigure(0, weight=1)

        totals_right = ctk.CTkFrame(totals, fg_color="transparent")
        totals_right.grid(row=0, column=1, sticky="e")

        subtotal_label = self._total_row(totals_right, "Subtotal", "€0.00")
        tax_entry = self._tax_row(totals_right)
        total_label = self._total_row(totals_right, "Total", "€0.00", bold=True)

        def update_totals(_event=None) -> None:
            subtotal = 0.0

            for item in line_items:
                quantity_entry = item["quantity"]
                price_entry = item["price"]
                total_label_for_row = item["total"]

                if not isinstance(quantity_entry, ctk.CTkEntry):
                    continue
                if not isinstance(price_entry, ctk.CTkEntry):
                    continue
                if not isinstance(total_label_for_row, ctk.CTkLabel):
                    continue

                try:
                    quantity = int(quantity_entry.get().strip() or "0")
                    unit_price = float(price_entry.get().strip() or "0")
                except ValueError:
                    quantity = 0
                    unit_price = 0.0

                row_total = quantity * unit_price
                subtotal += row_total
                total_label_for_row.configure(text=f"€{row_total:.2f}")

            try:
                tax_rate = float(tax_entry.get().strip() or "0")
            except ValueError:
                tax_rate = 0.0

            tax_amount = subtotal * (tax_rate / 100)
            total = subtotal + tax_amount

            subtotal_label.configure(text=f"€{subtotal:.2f}")
            total_label.configure(text=f"€{total:.2f}")

        def remove_line_item(item_frame: ctk.CTkFrame, item_data: dict[str, object]) -> None:
            if item_data in line_items:
                line_items.remove(item_data)
            item_frame.destroy()
            update_totals()

        def add_line_item(
            description: str = "",
            quantity_value: str = "1",
            price_value: str = "0",
        ) -> None:
            item_frame = ctk.CTkFrame(line_items_frame, fg_color="transparent")
            item_frame.pack(fill="x", pady=(0, 8))

            item_frame.grid_columnconfigure(0, weight=3)
            item_frame.grid_columnconfigure((1, 2), weight=1)
            item_frame.grid_columnconfigure(3, weight=1)

            description_entry = ctk.CTkEntry(
                item_frame,
                placeholder_text="Description",
                height=40,
                corner_radius=10,
                border_color=APP_COLORS["border"],
            )
            description_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
            description_entry.insert(0, description)

            quantity_entry = ctk.CTkEntry(
                item_frame,
                height=40,
                corner_radius=10,
                border_color=APP_COLORS["border"],
            )
            quantity_entry.grid(row=0, column=1, sticky="ew", padx=(0, 8))
            quantity_entry.insert(0, quantity_value)

            price_entry = ctk.CTkEntry(
                item_frame,
                height=40,
                corner_radius=10,
                border_color=APP_COLORS["border"],
            )
            price_entry.grid(row=0, column=2, sticky="ew", padx=(0, 8))
            price_entry.insert(0, price_value)

            row_total_label = ctk.CTkLabel(
                item_frame,
                text="€0.00",
                text_color=APP_COLORS["foreground"],
                font=("Inter", 13, "bold"),
            )
            row_total_label.grid(row=0, column=3, sticky="e", padx=(0, 8))

            item_data: dict[str, object] = {
                "frame": item_frame,
                "description": description_entry,
                "quantity": quantity_entry,
                "price": price_entry,
                "total": row_total_label,
            }

            ctk.CTkButton(
                item_frame,
                text="🗑",
                width=28,
                height=28,
                fg_color="transparent",
                hover_color=APP_COLORS["muted"],
                text_color=APP_COLORS["danger"],
                command=lambda: remove_line_item(item_frame, item_data),
            ).grid(row=0, column=4, sticky="e")

            line_items.append(item_data)

            quantity_entry.bind("<KeyRelease>", update_totals)
            price_entry.bind("<KeyRelease>", update_totals)
            update_totals()

        def autofill_booking_items(customer_name: str) -> None:
            booking = self._find_booking_by_customer(customer_name)

            if booking is None:
                return

            invoice_number_entry.delete(0, "end")
            invoice_number_entry.insert(0, self._next_invoice_number(booking))

            for existing_item in line_items.copy():
                item_frame = existing_item.get("frame")
                if isinstance(item_frame, ctk.CTkFrame):
                    item_frame.destroy()

            line_items.clear()

            service_name = booking.cleaning_service.service_name
            service_price = booking.total_amount or booking.cleaning_service.calculate_service_cost()

            add_line_item(
                description=service_name,
                quantity_value="1",
                price_value=str(service_price),
            )
            update_totals()

        customer_combo.configure(command=autofill_booking_items)

        if invoice is not None:
            add_line_item(
                invoice.line_description,
                str(invoice.quantity),
                str(invoice.unit_price),
            )
            tax_entry.insert(0, str(invoice.tax_rate))
        else:
            tax_entry.insert(0, "0")

            if self.bookings:
                first_customer = (
                    f"{self.bookings[0].booking_number} - "
                    f"{self.bookings[0].customer.full_name}"
                )
                customer_var.set(first_customer)
                autofill_booking_items(first_customer)
            else:
                add_line_item()

        tax_entry.bind("<KeyRelease>", update_totals)
        update_totals()

        bottom = ctk.CTkFrame(body, fg_color="transparent")
        bottom.pack(fill="x", pady=(16, 0))
        bottom.grid_columnconfigure((0, 1), weight=1)

        status_var = ctk.StringVar(value=invoice.payment_status if invoice else "draft")

        self._modal_combo(
            bottom,
            "Status",
            status_var,
            INVOICE_STATUSES,
            0,
            0,
        )

        notes_frame = ctk.CTkFrame(bottom, fg_color="transparent")
        notes_frame.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        ctk.CTkLabel(
            notes_frame,
            text="Notes",
            text_color=APP_COLORS["foreground"],
            font=APP_FONTS["small"],
        ).pack(anchor="w", pady=(0, 4))

        notes_entry = ctk.CTkTextbox(
            notes_frame,
            height=64,
            corner_radius=10,
            border_width=1,
            border_color=APP_COLORS["border"],
            fg_color=APP_COLORS["card"],
            text_color=APP_COLORS["foreground"],
        )
        notes_entry.pack(fill="x")

        if invoice is not None:
            notes_entry.insert("1.0", invoice.notes)

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.pack(fill="x", padx=22, pady=(18, 22))

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
            command=lambda: self._save_invoice(
                modal,
                invoice,
                invoice_number_entry,
                customer_var,
                due_date_entry,
                line_items,
                tax_entry,
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

    def _save_invoice(
        self,
        modal: ctk.CTkToplevel,
        existing_invoice: Invoice | None,
        invoice_number_entry: ctk.CTkEntry,
        customer_var: ctk.StringVar,
        due_date_entry: ctk.CTkEntry,
        line_items: list[dict[str, object]],
        tax_entry: ctk.CTkEntry,
        status_var: ctk.StringVar,
        notes_entry: ctk.CTkTextbox,
    ) -> None:
        booking = self._find_booking_by_customer(customer_var.get())

        if booking is None:
            self._error("Please select a valid booking.")
            return

        if existing_invoice is None:
            for invoice in self.invoices:
                if invoice.booking.entity_id == booking.entity_id:
                    self._error("An invoice already exists for this booking.")
                    return

        try:
            due_date = datetime.strptime(due_date_entry.get().strip(), "%d/%m/%Y")
            tax_rate = float(tax_entry.get().strip())
        except ValueError:
            self._error("Please enter a valid due date and tax.")
            return

        descriptions = []
        subtotal = 0.0
        saved_quantity = 1
        saved_unit_price = 0.0

        for item in line_items:
            description_entry = item["description"]
            quantity_entry = item["quantity"]
            price_entry = item["price"]

            if not isinstance(description_entry, ctk.CTkEntry):
                continue
            if not isinstance(quantity_entry, ctk.CTkEntry):
                continue
            if not isinstance(price_entry, ctk.CTkEntry):
                continue

            try:
                quantity = int(quantity_entry.get().strip())
                unit_price = float(price_entry.get().strip())
            except ValueError:
                self._error("Each line item needs a valid quantity and price.")
                return

            description = description_entry.get().strip() or "Invoice item"
            descriptions.append(f"{description} x{quantity} @ €{unit_price:.2f}")
            subtotal += quantity * unit_price

            saved_quantity = quantity
            saved_unit_price = unit_price

        total_amount = subtotal + (subtotal * (tax_rate / 100))

        invoice = Invoice(
            entity_id=existing_invoice.entity_id if existing_invoice else BaseEntity.generate_id(),
            created_at=existing_invoice.created_at if existing_invoice else datetime.now(),
            booking=booking,
            total_amount=total_amount,
            payment_status=status_var.get(),
            invoice_number=invoice_number_entry.get().strip(),
            due_date=due_date,
            line_description="; ".join(descriptions),
            quantity=saved_quantity,
            unit_price=saved_unit_price,
            tax_rate=tax_rate,
            notes=notes_entry.get("1.0", "end").strip(),
        )

        InvoiceRepository.save_invoice(invoice)
        modal.destroy()
        self._refresh_whole_page()

    def _filtered_invoices(self) -> list[Invoice]:
        search_text = self.search_entry.get().strip().lower() if self.search_entry else ""

        if not search_text:
            return self.invoices

        return [
            invoice
            for invoice in self.invoices
            if search_text in invoice.invoice_number.lower()
            or search_text in invoice.booking.customer.full_name.lower()
            or search_text in invoice.payment_status.lower()
        ]

    def _delete_invoice(self, invoice: Invoice) -> None:
        confirmed = messagebox.askyesno(
            "Delete Invoice",
            f"Delete invoice {invoice.invoice_number}?",
        )

        if not confirmed:
            return

        InvoiceRepository.delete(invoice.entity_id)
        self._refresh_whole_page()

    def _refresh_whole_page(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

        self.search_entry = None
        self.table_frame = None

        self._reload_data()
        self._build_page()

    def _modal_combo(
        self,
        parent,
        label: str,
        variable: ctk.StringVar,
        values: list[str],
        row: int,
        column: int,
    ) -> ctk.CTkComboBox:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
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
        ).pack(anchor="w", pady=(0, 4))

        entry = ctk.CTkEntry(
            frame,
            height=40,
            corner_radius=10,
            border_color=APP_COLORS["border"],
        )
        entry.pack(fill="x")
        return entry

    def _total_row(self, parent, label: str, value: str, bold: bool = False) -> ctk.CTkLabel:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=2)

        font = ("Inter", 15, "bold") if bold else APP_FONTS["body"]

        ctk.CTkLabel(
            row,
            text=label,
            text_color=APP_COLORS["foreground"] if bold else APP_COLORS["muted_text"],
            font=font,
            width=120,
            anchor="w",
        ).pack(side="left")

        value_label = ctk.CTkLabel(
            row,
            text=value,
            text_color=APP_COLORS["foreground"],
            font=font,
            width=90,
            anchor="e",
        )
        value_label.pack(side="right")

        return value_label

    def _tax_row(self, parent) -> ctk.CTkEntry:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=2)

        ctk.CTkLabel(
            row,
            text="Tax (%)",
            text_color=APP_COLORS["muted_text"],
            font=APP_FONTS["body"],
            width=120,
            anchor="w",
        ).pack(side="left")

        tax_entry = ctk.CTkEntry(
            row,
            width=90,
            height=32,
            corner_radius=8,
            border_color=APP_COLORS["border"],
        )
        tax_entry.pack(side="right")

        return tax_entry

    def _next_invoice_number(self, booking) -> str:
        booking_number = getattr(booking, "booking_number", "")

        if booking_number.startswith("BOOK-"):
            return booking_number.replace("BOOK-", "INV-", 1)

        return f"INV-{len(self.invoices) + 1:04d}"

    def _find_booking_by_customer(self, customer_name: str):
        for booking in self.bookings:
            booking_display = (
                f"{booking.booking_number} - "
                f"{booking.customer.full_name}"
            )

            if booking_display == customer_name:
                return booking

        return None

    @staticmethod
    def _status_colours(status: str) -> tuple[str, str]:
        if status == "paid":
            return "#dcfce7", "#059669"
        if status == "sent":
            return "#dbeafe", "#2563eb"
        if status == "draft":
            return "#f1f5f9", APP_COLORS["muted_text"]
        if status == "overdue":
            return "#fee2e2", APP_COLORS["danger"]
        return "#fef3c7", "#b45309"

    @staticmethod
    def _error(message: str) -> None:
        messagebox.showerror("Validation Error", message)
