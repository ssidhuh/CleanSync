"""Database management module."""

import sqlite3
from pathlib import Path


class DatabaseManager:
    """
    Centralises database connection management for the application.

    A dedicated database manager prevents duplicated connection
    logic across repositories and improves maintainability.
    """

    DATABASE_PATH = Path(__file__).resolve().parents[2] / "cleansync.db"

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        """Create and return a SQLite database connection."""
        connection = sqlite3.connect(cls.DATABASE_PATH)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.row_factory = sqlite3.Row
        return connection

    @classmethod
    def initialise_database(cls) -> None:
        """Create required database tables if they do not exist."""
        connection = cls.get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                email TEXT NOT NULL,
                address TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cleaners (
                cleaner_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                hourly_rate REAL NOT NULL,
                rating REAL NOT NULL,
                status TEXT NOT NULL,
                specializations TEXT NOT NULL,
                service_area TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cleaning_services (
                service_id TEXT PRIMARY KEY,
                service_name TEXT NOT NULL,
                description TEXT NOT NULL,
                duration_hours REAL NOT NULL,
                base_price REAL NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                cleaner_id TEXT NOT NULL,
                service_id TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                FOREIGN KEY (cleaner_id) REFERENCES cleaners(cleaner_id),
                FOREIGN KEY (service_id) REFERENCES cleaning_services(service_id)
            )
            """
        )

        booking_columns = {
            "booking_number": "TEXT",
            "end_time": "TEXT",
            "address": "TEXT",
            "total_amount": "REAL DEFAULT 0",
            "notes": "TEXT DEFAULT ''",
        }

        cursor.execute("PRAGMA table_info(bookings)")
        existing_columns = {row["name"] for row in cursor.fetchall()}

        for column_name, column_type in booking_columns.items():
            if column_name not in existing_columns:
                cursor.execute(
                    f"ALTER TABLE bookings ADD COLUMN {column_name} {column_type}"
                )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS invoices (
                invoice_id TEXT PRIMARY KEY,
                booking_id TEXT NOT NULL,
                total_amount REAL NOT NULL,
                payment_status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
            )
            """
        )

        invoice_columns = {
            "invoice_number": "TEXT",
            "due_date": "TEXT",
            "line_description": "TEXT DEFAULT ''",
            "quantity": "INTEGER DEFAULT 1",
            "unit_price": "REAL DEFAULT 0",
            "tax_rate": "REAL DEFAULT 0",
            "notes": "TEXT DEFAULT ''",
        }

        cursor.execute("PRAGMA table_info(invoices)")
        existing_columns = {row["name"] for row in cursor.fetchall()}

        for column_name, column_definition in invoice_columns.items():
            if column_name not in existing_columns:
                cursor.execute(
                    f"ALTER TABLE invoices ADD COLUMN {column_name} {column_definition}"
                )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
                 payment_id TEXT PRIMARY KEY,
                 invoice_id TEXT NOT NULL,
                 amount REAL NOT NULL,
                 payment_date TEXT NOT NULL,
                 method TEXT NOT NULL,
                 reference_number TEXT NOT NULL,
                 status TEXT NOT NULL,
                 notes TEXT DEFAULT '',
                 created_at TEXT NOT NULL,
                 FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
            )
            """
        )

        connection.commit()
        connection.close()
