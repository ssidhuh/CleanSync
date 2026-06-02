"""Payments view for the CleanSync desktop application."""

from __future__ import annotations

from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from src.models.base_entity import BaseEntity
from src.models.payment import Payment
from src.repositories.invoice_repository import InvoiceRepository
from src.repositories.payment_repository import PaymentRepository
from src.ui.theme import APP_COLORS, APP_FONTS

PAYMENT_METHODS = ["cash", "credit card", "bank transfer", "online"]
PAYMENT_STATUSES = ["pending", "completed", "failed", "refunded"]


class PaymentsView(ctk.CTkFrame):
    """Payments page with table and payment modal."""

    def __init__(self, parent) -> None:
        super().__init__(parent, fg_color=APP_COLORS["background"])
        self.pack(fill="both", expand=True)

        self.search_entry: ctk.CTkEntry | None = None
        self.table_frame: ctk.CTkFrame | None = None

        self._reload_data()
        self._build_page()

    def _reload_data(self) -> None:
        self.invoices = InvoiceRepository.find_all()
        self.payments = PaymentRepository.find_all()

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
            text="Payments",
            text_color=APP_COLORS["foreground"],
            font=("Inter", 28, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text=f"{len(self.payments)} total payments",
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
            text="+  Record Payment",
            width=180,
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

        payments = self._filtered_payments()

        headers = ["CUSTOMER", "AMOUNT", "METHOD", "DATE", "REFERENCE", "STATUS", ""]
        widths = [180, 120, 150, 160, 170, 140, 90]

        for column, header in enumerate(headers):
            self.table_frame.grid_columnconfigure(column, weight=1, minsize=widths[column])
            ctk.CTkLabel(
                self.table_frame,
                text=header,
                text_color=APP_COLORS["muted_text"],
                font=("Inter", 11, "bold"),
            ).grid(row=0, column=column, sticky="w", padx=10, pady=(16, 10))

        self._table_separator(1)

        if not payments:
            ctk.CTkLabel(
                self.table_frame,
                text="No payments found. Record your first payment above.",
                text_color=APP_COLORS["muted_text"],
                font=APP_FONTS["body"],
            ).grid(row=2, column=0, columnspan=7, pady=80)
            return

        for index, payment in enumerate(payments):
            row_number = 2 + (index * 2)
            self._table_row(payment, row_number)
            self._table_separator(row_number + 1)

    def _table_separator(self, row: int) -> None:
        if self.table_frame is None:
            return

        ctk.CTkFrame(
            self.table_frame,
            fg_color=APP_COLORS["border"],
            height=1,
        ).grid(row=row, column=0, columnspan=7, sticky="ew")

    def _table_row(self, payment: Payment, row_index: int) -> None:
        values = [
            payment.invoice.booking.customer.full_name,
            f"€{payment.amount:.2f}",
            payment.method.title(),
            payment.payment_date.strftime("%b %d, %Y"),
            payment.reference_number,
        ]

        for column, value in enumerate(values):
            ctk.CTkLabel(
                self.table_frame,
                text=value,
                text_color=APP_COLORS["foreground"],
                font=("Inter", 13, "bold" if column in [0, 1] else "normal"),
            ).grid(row=row_index, column=column, sticky="w", padx=10, pady=12)

        method_bg, method_fg = self._method_colours(payment.method)

        ctk.CTkLabel(
            self.table_frame,
            text=payment.method.title(),
            text_color=method_fg,
            fg_color=method_bg,
            corner_radius=8,
            height=24,
            width=112,
            font=("Inter", 11, "bold"),
        ).grid(row=row_index, column=2, sticky="w", padx=10, pady=12)

        status_bg, status_fg = self._status_colours(payment.status)

        ctk.CTkLabel(
            self.table_frame,
            text=payment.status.title(),
            text_color=status_fg,
            fg_color=status_bg,
            corner_radius=8,
            height=24,
            width=96,
            font=("Inter", 11, "bold"),
        ).grid(row=row_index, column=5, sticky="w", padx=10, pady=12)

        actions = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        actions.grid(row=row_index, column=6, sticky="w", padx=10, pady=8)

        ctk.CTkButton(
            actions,
            text="✎",
            width=30,
            height=28,
            fg_color="transparent",
            hover_color=APP_COLORS["muted"],
            text_color=APP_COLORS["foreground"],
            command=lambda selected=payment: self._open_modal(selected),
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            actions,
            text="🗑",
            width=30,
            height=28,
            fg_color="transparent",
            hover_color=APP_COLORS["muted"],
            text_color=APP_COLORS["danger"],
            command=lambda selected=payment: self._delete_payment(selected),
        ).pack(side="left")

    def _open_modal(self, payment: Payment | None = None) -> None:
        self._reload_data()

        modal = ctk.CTkToplevel(self)
        modal.title("Edit Payment" if payment else "Record Payment")
        modal.geometry("480x620")
        modal.resizable(False, False)
        modal.grab_set()

        card = ctk.CTkFrame(modal, fg_color=APP_COLORS["card"], corner_radius=16)
        card.pack(fill="both", expand=True, padx=18, pady=18)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=22, pady=(20, 12))

        ctk.CTkLabel(
            top,
            text="Edit Payment" if payment else "Record Payment",
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

        invoice_var = ctk.StringVar(value="Select invoice")
        if payment is not None:
            invoice_var.set(self._invoice_display(payment.invoice))

        invoice_combo = self._modal_combo(
            body,
            "Invoice *",
            invoice_var,
            [self._invoice_display(invoice) for invoice in self.invoices],
        )

        row_one = ctk.CTkFrame(body, fg_color="transparent")
        row_one.pack(fill="x")
        row_one.grid_columnconfigure((0, 1), weight=1)

        amount_entry = self._modal_entry_grid(row_one, "Amount (€) *", 0, 0)
        date_entry = self._modal_entry_grid(row_one, "Payment Date *", 0, 1)

        row_two = ctk.CTkFrame(body, fg_color="transparent")
        row_two.pack(fill="x")
        row_two.grid_columnconfigure((0, 1), weight=1)

        method_var = ctk.StringVar(value=payment.method if payment else "cash")
        self._modal_combo(row_two, "Method", method_var, PAYMENT_METHODS, 0, 0)

        reference_entry = self._modal_entry_grid(row_two, "Reference #", 0, 1)

        def autofill_payment_fields(selected_invoice_display: str) -> None:
            selected_invoice = self._find_invoice_by_display(selected_invoice_display)

            if selected_invoice is None:
                return

            reference_entry.delete(0, "end")
            reference_entry.insert(0, self._reference_number_for_invoice(selected_invoice))

            amount_entry.delete(0, "end")
            amount_entry.insert(0, f"{selected_invoice.total_amount:.2f}")

        invoice_combo.configure(command=autofill_payment_fields)

        status_var = ctk.StringVar(value=payment.status if payment else "completed")
        self._modal_combo(body, "Status", status_var, PAYMENT_STATUSES)

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

        if payment is not None:
            amount_entry.insert(0, str(payment.amount))
            date_entry.insert(0, payment.payment_date.strftime("%d/%m/%Y"))
            reference_entry.insert(0, payment.reference_number)
            notes_entry.insert("1.0", payment.notes)
        else:
            date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))

            if self.invoices:
                first_invoice = self.invoices[0]
                invoice_var.set(self._invoice_display(first_invoice))
                reference_entry.insert(0, self._reference_number_for_invoice(first_invoice))
                amount_entry.insert(0, f"{first_invoice.total_amount:.2f}")

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
            command=lambda: self._save_payment(
                modal,
                payment,
                invoice_var,
                amount_entry,
                date_entry,
                method_var,
                reference_entry,
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

    def _save_payment(
        self,
        modal: ctk.CTkToplevel,
        existing_payment: Payment | None,
        invoice_var: ctk.StringVar,
        amount_entry: ctk.CTkEntry,
        date_entry: ctk.CTkEntry,
        method_var: ctk.StringVar,
        reference_entry: ctk.CTkEntry,
        status_var: ctk.StringVar,
        notes_entry: ctk.CTkTextbox,
    ) -> None:
        invoice = self._find_invoice_by_display(invoice_var.get())

        if invoice is None:
            self._error("Please select a valid invoice.")
            return

        try:
            amount = float(amount_entry.get().strip())
            payment_date = datetime.strptime(date_entry.get().strip(), "%d/%m/%Y")
        except ValueError:
            self._error("Amount must be a number and date must be DD/MM/YYYY.")
            return

        if amount <= 0:
            self._error("Amount must be greater than zero.")
            return

        payment = Payment(
            entity_id=existing_payment.entity_id if existing_payment else BaseEntity.generate_id(),
            created_at=existing_payment.created_at if existing_payment else datetime.now(),
            invoice=invoice,
            amount=amount,
            payment_date=payment_date,
            method=method_var.get(),
            reference_number=reference_entry.get().strip() or self._reference_number_for_invoice(invoice),
            status=status_var.get(),
            notes=notes_entry.get("1.0", "end").strip(),
        )

        if payment.status == "completed":
            invoice.payment_status = "paid"
            InvoiceRepository.save_invoice(invoice)

        PaymentRepository.save_payment(payment)
        modal.destroy()
        self._refresh_whole_page()

    def _filtered_payments(self) -> list[Payment]:
        search_text = self.search_entry.get().strip().lower() if self.search_entry else ""

        if not search_text:
            return self.payments

        return [
            payment
            for payment in self.payments
            if search_text in payment.invoice.booking.customer.full_name.lower()
            or search_text in payment.method.lower()
            or search_text in payment.reference_number.lower()
            or search_text in payment.status.lower()
        ]

    def _delete_payment(self, payment: Payment) -> None:
        confirmed = messagebox.askyesno(
            "Delete Payment",
            f"Delete payment {payment.reference_number}?",
        )

        if not confirmed:
            return

        PaymentRepository.delete(payment.entity_id)
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
        row: int | None = None,
        column: int | None = None,
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
            values=values if values else ["No invoices available"],
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
        ).pack(anchor="w", pady=(12, 4))

        entry = ctk.CTkEntry(
            frame,
            height=40,
            corner_radius=10,
            border_color=APP_COLORS["border"],
        )
        entry.pack(fill="x")
        return entry

    def _invoice_display(self, invoice) -> str:
        invoice_number = invoice.invoice_number or invoice.entity_id[:8]
        return f"{invoice_number} - {invoice.booking.customer.full_name} - €{invoice.total_amount:.2f}"

    def _find_invoice_by_display(self, display: str):
        for invoice in self.invoices:
            if self._invoice_display(invoice) == display:
                return invoice
        return None

    def _reference_number_for_invoice(self, invoice) -> str:
        invoice_number = invoice.invoice_number or invoice.entity_id[:8]
        invoice_digits = "".join(character for character in invoice_number if character.isdigit())

        if not invoice_digits:
            invoice_digits = f"{len(self.payments) + 1:03d}"

        invoice_digits = invoice_digits[-4:].zfill(4)

        return f"PAY-{datetime.now().year}-{invoice_digits}"

    @staticmethod
    def _method_colours(method: str) -> tuple[str, str]:
        if method == "credit card":
            return "#ede9fe", "#6d28d9"
        if method == "bank transfer":
            return "#ccfbf1", "#0f766e"
        if method == "online":
            return "#f3e8ff", "#7e22ce"
        return "#f1f5f9", APP_COLORS["foreground"]

    @staticmethod
    def _status_colours(status: str) -> tuple[str, str]:
        if status == "completed":
            return "#dcfce7", "#059669"
        if status == "pending":
            return "#fef3c7", "#b45309"
        if status == "failed":
            return "#fee2e2", APP_COLORS["danger"]
        return "#dbeafe", "#2563eb"

    @staticmethod
    def _error(message: str) -> None:
        messagebox.showerror("Validation Error", message)
