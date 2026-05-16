"""Stable grid-based graphical user interface for CleanSync."""

from __future__ import annotations

import tkinter as tk
from datetime import datetime
from tkinter import messagebox

from src.models.base_entity import BaseEntity
from src.models.booking import Booking
from src.models.cleaner import Cleaner
from src.models.customer import Customer
from src.models.invoice import Invoice
from src.models.service import CleaningService
from src.repositories.booking_repository import BookingRepository
from src.repositories.cleaner_repository import CleanerRepository
from src.repositories.customer_repository import CustomerRepository
from src.repositories.invoice_repository import InvoiceRepository
from src.repositories.service_repository import ServiceRepository
from src.services.booking_service import BookingService


class CleanSyncApp(tk.Tk):
    """Single-window CleanSync desktop application."""

    def __init__(self) -> None:
        """Create the application shell."""
        super().__init__()
        self.title("CleanSync VERSION 3 GRID UI")
        self.geometry("1180x760")
        self.minsize(1180, 760)
        self.configure(bg="#eef2f7")

        self.entries: dict[str, tk.Entry] = {}
        self.records: tk.Listbox | None = None
        self.current_items: list = []
        self.customer_picker: tk.Listbox | None = None
        self.cleaner_picker: tk.Listbox | None = None
        self.service_picker: tk.Listbox | None = None
        self.booking_picker: tk.Listbox | None = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = tk.Frame(self, bg="#24364f", width=230)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        self.content = tk.Frame(self, bg="#eef2f7")
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(3, weight=1)

        self.build_menu()
        self.show_dashboard()

    def build_menu(self) -> None:
        """Build the sidebar navigation menu."""
        tk.Label(
            self.sidebar,
            text="CleanSync",
            bg="#24364f",
            fg="white",
            font=("Arial", 24, "bold"),
        ).pack(pady=(30, 24))

        menu_items = [
            ("Dashboard", self.show_dashboard),
            ("Customers", self.show_customers),
            ("Cleaners", self.show_cleaners),
            ("Services", self.show_services),
            ("Bookings", self.show_bookings),
            ("Invoices", self.show_invoices),
        ]

        for label, command in menu_items:
            tk.Button(
                self.sidebar,
                text=label,
                command=command,
                width=17,
                height=2,
                font=("Arial", 13, "bold"),
            ).pack(pady=8)

    def clear_page(self) -> None:
        """Remove the current page content."""
        for widget in self.content.winfo_children():
            widget.destroy()
        self.entries = {}
        self.records = None
        self.current_items = []
        self.customer_picker = None
        self.cleaner_picker = None
        self.service_picker = None
        self.booking_picker = None

    def header(self, title: str, subtitle: str) -> None:
        """Create the page header."""
        tk.Label(
            self.content,
            text=f"{title} - VERSION 3 GRID UI",
            bg="#eef2f7",
            fg="#172033",
            font=("Arial", 24, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=28, pady=(24, 4))
        tk.Label(
            self.content,
            text=subtitle,
            bg="#eef2f7",
            fg="#536170",
            font=("Arial", 13),
        ).grid(row=1, column=0, sticky="w", padx=30, pady=(0, 18))

    def show_dashboard(self) -> None:
        """Show the dashboard page."""
        self.clear_page()
        self.header("Dashboard", "Summary of CleanSync records and workflow.")

        cards = tk.Frame(self.content, bg="#eef2f7")
        cards.grid(row=2, column=0, sticky="ew", padx=24)

        counts = [
            ("Customers", len(CustomerRepository.find_all())),
            ("Cleaners", len(CleanerRepository.find_all())),
            ("Services", len(ServiceRepository.find_all())),
            ("Bookings", len(BookingRepository.find_all())),
            ("Invoices", len(InvoiceRepository.find_all())),
        ]

        for index, (label, value) in enumerate(counts):
            cards.grid_columnconfigure(index, weight=1)
            card = tk.Frame(cards, bg="white", relief="solid", bd=1)
            card.grid(row=0, column=index, sticky="ew", padx=6, pady=6)
            tk.Label(
                card,
                text=label,
                bg="white",
                fg="#24364f",
                font=("Arial", 12, "bold"),
            ).pack(pady=(16, 4))
            tk.Label(
                card,
                text=str(value),
                bg="white",
                fg="#172033",
                font=("Arial", 28, "bold"),
            ).pack(pady=(0, 16))

        tk.Label(
            self.content,
            text=(
                "Recommended workflow: add a customer, add a cleaner, add a "
                "cleaning service, create a booking, then generate an invoice."
            ),
            bg="#eef2f7",
            fg="#172033",
            font=("Arial", 15),
            wraplength=760,
            justify="left",
        ).grid(row=3, column=0, sticky="nw", padx=30, pady=32)

    def show_customers(self) -> None:
        """Show customer management page."""
        self.clear_page()
        self.header("Customers", "Add, view, and delete customer records.")
        self.form(["First Name", "Last Name", "Phone Number", "Email", "Address"])
        self.actions(
            [("Save Customer", self.save_customer), ("Delete Selected", self.delete_customer)]
        )
        self.record_list(self.customer_rows(), CustomerRepository.find_all())

    def show_cleaners(self) -> None:
        """Show cleaner management page."""
        self.clear_page()
        self.header("Cleaners", "Add, view, and delete cleaner records.")
        self.form(["First Name", "Last Name", "Phone Number", "Service Area", "Hourly Rate"])
        self.actions(
            [("Save Cleaner", self.save_cleaner), ("Delete Selected", self.delete_cleaner)]
        )
        self.record_list(self.cleaner_rows(), CleanerRepository.find_all())

    def show_services(self) -> None:
        """Show cleaning service management page."""
        self.clear_page()
        self.header("Services", "Add service types, durations, and prices.")
        self.form(["Service Name", "Description", "Duration Hours", "Base Price"])
        self.actions(
            [("Save Service", self.save_service), ("Delete Selected", self.delete_service)]
        )
        self.record_list(self.service_rows(), ServiceRepository.find_all())

    def show_bookings(self) -> None:
        """Show booking management page."""
        self.clear_page()
        self.header("Bookings", "Select records below to create a cleaning booking.")

        picker_area = tk.Frame(self.content, bg="#eef2f7")
        picker_area.grid(row=2, column=0, sticky="ew", padx=28)
        picker_area.grid_columnconfigure(0, weight=1)
        picker_area.grid_columnconfigure(1, weight=1)
        picker_area.grid_columnconfigure(2, weight=1)

        self.customer_picker = self.picker(
            picker_area,
            "Customers",
            self.customer_rows(short=True),
            0,
        )
        self.cleaner_picker = self.picker(
            picker_area,
            "Cleaners",
            self.cleaner_rows(short=True),
            1,
        )
        self.service_picker = self.picker(
            picker_area,
            "Services",
            self.service_rows(short=True),
            2,
        )

        date_row = tk.Frame(self.content, bg="#eef2f7")
        date_row.grid(row=3, column=0, sticky="w", padx=30, pady=12)
        tk.Label(
            date_row,
            text="Date and Time",
            bg="#eef2f7",
            font=("Arial", 12, "bold"),
        ).pack(side="left", padx=(0, 12))
        date_entry = tk.Entry(date_row, width=22, font=("Arial", 12))
        date_entry.insert(0, "2026-05-20 10:30")
        date_entry.pack(side="left")
        self.entries["Date and Time"] = date_entry
        tk.Label(
            date_row,
            text="Format: YYYY-MM-DD HH:MM",
            bg="#eef2f7",
            fg="#536170",
        ).pack(side="left", padx=12)

        self.actions(
            [("Create Booking", self.save_booking), ("Delete Selected", self.delete_booking)],
            row=4,
        )
        self.record_list(self.booking_rows(), BookingRepository.find_all(), row=5)

    def show_invoices(self) -> None:
        """Show invoice management page."""
        self.clear_page()
        self.header("Invoices", "Select a booking to generate or update an invoice.")

        picker_area = tk.Frame(self.content, bg="#eef2f7")
        picker_area.grid(row=2, column=0, sticky="ew", padx=28)
        picker_area.grid_columnconfigure(0, weight=1)
        self.booking_picker = self.picker(
            picker_area,
            "Bookings",
            self.booking_rows(short=True),
            0,
        )

        self.actions(
            [
                ("Generate Invoice", self.save_invoice),
                ("Mark Selected Paid", self.mark_invoice_paid),
            ],
            row=3,
        )
        self.record_list(self.invoice_rows(), InvoiceRepository.find_all(), row=4)

    def form(self, fields: list[str]) -> None:
        """Create a data entry form."""
        form = tk.Frame(self.content, bg="#eef2f7")
        form.grid(row=2, column=0, sticky="ew", padx=30)

        for row_index, field in enumerate(fields):
            tk.Label(
                form,
                text=field,
                bg="#eef2f7",
                font=("Arial", 12, "bold"),
            ).grid(row=row_index, column=0, sticky="w", pady=5)
            entry = tk.Entry(form, width=42, font=("Arial", 12))
            entry.grid(row=row_index, column=1, sticky="w", pady=5, padx=(16, 0))
            self.entries[field] = entry

    def actions(self, buttons: list[tuple[str, object]], row: int = 3) -> None:
        """Create command buttons."""
        button_row = tk.Frame(self.content, bg="#eef2f7")
        button_row.grid(row=row, column=0, sticky="w", padx=30, pady=14)
        for text, command in buttons:
            tk.Button(
                button_row,
                text=text,
                command=command,
                width=18,
                height=2,
                font=("Arial", 11, "bold"),
            ).pack(side="left", padx=(0, 10))

    def record_list(
        self,
        rows: list[str],
        items: list,
        row: int = 4,
    ) -> None:
        """Create the saved records list."""
        record_area = tk.Frame(self.content, bg="#eef2f7")
        record_area.grid(row=row, column=0, sticky="nsew", padx=30, pady=(6, 24))
        record_area.grid_columnconfigure(0, weight=1)
        record_area.grid_rowconfigure(1, weight=1)
        self.content.grid_rowconfigure(row, weight=1)

        tk.Label(
            record_area,
            text="Saved Records",
            bg="#eef2f7",
            font=("Arial", 13, "bold"),
        ).grid(row=0, column=0, sticky="w")
        self.records = tk.Listbox(
            record_area,
            height=10,
            font=("Courier New", 11),
            bg="white",
        )
        self.records.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        self.current_items = items
        for line in rows:
            self.records.insert(tk.END, line)

    def picker(
        self,
        parent: tk.Frame,
        title: str,
        rows: list[str],
        column: int,
    ) -> tk.Listbox:
        """Create a selection listbox."""
        frame = tk.Frame(parent, bg="#eef2f7")
        frame.grid(row=0, column=column, sticky="nsew", padx=6)
        tk.Label(
            frame,
            text=title,
            bg="#eef2f7",
            font=("Arial", 12, "bold"),
        ).pack(anchor="w")
        listbox = tk.Listbox(frame, height=6, font=("Courier New", 10), exportselection=False)
        listbox.pack(fill="both", expand=True, pady=(6, 0))
        for row in rows:
            listbox.insert(tk.END, row)
        return listbox

    def save_customer(self) -> None:
        """Validate and save customer data."""
        values = self.required(["First Name", "Last Name", "Phone Number", "Email", "Address"])
        if values is None:
            return
        customer = Customer(
            entity_id=BaseEntity.generate_id(),
            created_at=datetime.now(),
            first_name=values["First Name"],
            last_name=values["Last Name"],
            phone_number=values["Phone Number"],
            email=values["Email"],
            address=values["Address"],
        )
        if not customer.validate_contact_information():
            self.error("Please enter a valid email and phone number.")
            return
        CustomerRepository.save_customer(customer)
        messagebox.showinfo("Saved", "Customer saved successfully.")
        self.show_customers()

    def save_cleaner(self) -> None:
        """Validate and save cleaner data."""
        values = self.required(["First Name", "Last Name", "Phone Number", "Service Area", "Hourly Rate"])
        if values is None:
            return
        try:
            hourly_rate = float(values["Hourly Rate"])
        except ValueError:
            self.error("Hourly rate must be a number.")
            return
        CleanerRepository.save_cleaner(
            Cleaner(
                entity_id=BaseEntity.generate_id(),
                created_at=datetime.now(),
                first_name=values["First Name"],
                last_name=values["Last Name"],
                phone_number=values["Phone Number"],
                service_area=values["Service Area"],
                hourly_rate=hourly_rate,
            )
        )
        messagebox.showinfo("Saved", "Cleaner saved successfully.")
        self.show_cleaners()

    def save_service(self) -> None:
        """Validate and save service data."""
        values = self.required(["Service Name", "Description", "Duration Hours", "Base Price"])
        if values is None:
            return
        try:
            duration = float(values["Duration Hours"])
            price = float(values["Base Price"])
        except ValueError:
            self.error("Duration and price must be numbers.")
            return
        ServiceRepository.save_service(
            CleaningService(
                entity_id=BaseEntity.generate_id(),
                created_at=datetime.now(),
                service_name=values["Service Name"],
                description=values["Description"],
                duration_hours=duration,
                base_price=price,
            )
        )
        messagebox.showinfo("Saved", "Service saved successfully.")
        self.show_services()

    def save_booking(self) -> None:
        """Validate and save booking data."""
        customer = self.selected_from_picker(self.customer_picker, CustomerRepository.find_all())
        cleaner = self.selected_from_picker(self.cleaner_picker, CleanerRepository.find_all())
        service = self.selected_from_picker(self.service_picker, ServiceRepository.find_all())
        if customer is None or cleaner is None or service is None:
            self.error("Select a customer, cleaner, and service.")
            return
        try:
            booking_date = datetime.strptime(self.entries["Date and Time"].get(), "%Y-%m-%d %H:%M")
        except ValueError:
            self.error("Booking date must use YYYY-MM-DD HH:MM.")
            return
        booking = Booking(
            entity_id=BaseEntity.generate_id(),
            created_at=datetime.now(),
            customer=customer,
            cleaner=cleaner,
            cleaning_service=service,
            booking_date=booking_date,
            status="Pending",
        )
        try:
            BookingService.create_booking(booking)
        except ValueError as error:
            self.error(str(error))
            return
        messagebox.showinfo("Saved", "Booking created successfully.")
        self.show_bookings()

    def save_invoice(self) -> None:
        """Generate and save invoice data."""
        booking = self.selected_from_picker(self.booking_picker, BookingRepository.find_all())
        if booking is None:
            self.error("Select a booking.")
            return
        invoice = Invoice(
            entity_id=BaseEntity.generate_id(),
            created_at=datetime.now(),
            booking=booking,
            total_amount=booking.cleaning_service.calculate_service_cost(),
            payment_status="Unpaid",
        )
        InvoiceRepository.save_invoice(invoice)
        messagebox.showinfo("Saved", invoice.generate_invoice_summary())
        self.show_invoices()

    def mark_invoice_paid(self) -> None:
        """Mark selected invoice as paid."""
        invoice = self.selected_record()
        if invoice is None:
            return
        invoice.mark_as_paid()
        InvoiceRepository.save_invoice(invoice)
        messagebox.showinfo("Updated", "Invoice marked as paid.")
        self.show_invoices()

    def delete_customer(self) -> None:
        """Delete selected customer."""
        customer = self.selected_record()
        if customer is not None:
            CustomerRepository.delete(customer.entity_id)
            self.show_customers()

    def delete_cleaner(self) -> None:
        """Delete selected cleaner."""
        cleaner = self.selected_record()
        if cleaner is not None:
            CleanerRepository.delete(cleaner.entity_id)
            self.show_cleaners()

    def delete_service(self) -> None:
        """Delete selected service."""
        service = self.selected_record()
        if service is not None:
            ServiceRepository.delete(service.entity_id)
            self.show_services()

    def delete_booking(self) -> None:
        """Delete selected booking."""
        booking = self.selected_record()
        if booking is not None:
            BookingRepository.delete(booking.entity_id)
            self.show_bookings()

    def required(self, fields: list[str]) -> dict[str, str] | None:
        """Read required form values."""
        values = {field: self.entries[field].get().strip() for field in fields}
        if not all(values.values()):
            self.error("Please complete all fields.")
            return None
        return values

    def selected_record(self):
        """Return selected item from saved records list."""
        if self.records is None or not self.records.curselection():
            self.error("Select a saved record first.")
            return None
        return self.current_items[self.records.curselection()[0]]

    @staticmethod
    def selected_from_picker(listbox: tk.Listbox | None, items: list):
        """Return selected item from a picker list."""
        if listbox is None or not listbox.curselection():
            return None
        return items[listbox.curselection()[0]]

    @staticmethod
    def customer_rows(short: bool = False) -> list[str]:
        """Return customer display rows."""
        if short:
            return [item.full_name for item in CustomerRepository.find_all()]
        return [
            f"{item.full_name:<24} {item.phone_number:<14} {item.email:<30} {item.address}"
            for item in CustomerRepository.find_all()
        ]

    @staticmethod
    def cleaner_rows(short: bool = False) -> list[str]:
        """Return cleaner display rows."""
        if short:
            return [f"{item.full_name} - {item.service_area}" for item in CleanerRepository.find_all()]
        return [
            f"{item.full_name:<24} {item.service_area:<24} EUR {item.hourly_rate:<8.2f}"
            for item in CleanerRepository.find_all()
        ]

    @staticmethod
    def service_rows(short: bool = False) -> list[str]:
        """Return service display rows."""
        if short:
            return [item.service_name for item in ServiceRepository.find_all()]
        return [
            f"{item.service_name:<28} {item.duration_hours:<6} hours EUR {item.base_price:<8.2f}"
            for item in ServiceRepository.find_all()
        ]

    @staticmethod
    def booking_rows(short: bool = False) -> list[str]:
        """Return booking display rows."""
        if short:
            return [
                f"{item.customer.full_name} - {item.cleaning_service.service_name}"
                for item in BookingRepository.find_all()
            ]
        return [
            f"{item.customer.full_name:<22} {item.cleaner.full_name:<22} "
            f"{item.cleaning_service.service_name:<26} {item.status}"
            for item in BookingRepository.find_all()
        ]

    @staticmethod
    def invoice_rows() -> list[str]:
        """Return invoice display rows."""
        return [
            f"{item.booking.customer.full_name:<24} "
            f"{item.booking.cleaning_service.service_name:<30} "
            f"EUR {item.total_amount:<8.2f} {item.payment_status}"
            for item in InvoiceRepository.find_all()
        ]

    @staticmethod
    def error(message: str) -> None:
        """Show a validation error message."""
        messagebox.showerror("Validation Error", message)


def run_application() -> None:
    """Launch the CleanSync graphical application."""
    application = CleanSyncApp()
    application.mainloop()


if __name__ == "__main__":
    run_application()
