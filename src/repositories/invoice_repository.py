"""Repository module for invoice persistence operations."""

import sqlite3
from datetime import datetime

from src.database.database_manager import DatabaseManager
from src.models.invoice import Invoice
from src.repositories.booking_repository import BookingRepository
from src.repositories.repository_interface import RepositoryInterface


class InvoiceRepository(RepositoryInterface[Invoice]):
    """Handles invoice database operations."""

    @staticmethod
    def save(entity: Invoice) -> None:
        """Persist an invoice using the common repository interface."""
        InvoiceRepository.save_invoice(entity)

    @staticmethod
    def save_invoice(invoice: Invoice) -> None:
        """Save invoice information to the database."""
        BookingRepository.save_booking(invoice.booking)

        connection = None

        try:
            connection = DatabaseManager.get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO invoices (
                    invoice_id,
                    booking_id,
                    total_amount,
                    payment_status,
                    invoice_number,
                    due_date,
                    line_description,
                    quantity,
                    unit_price,
                    tax_rate,
                    notes,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    invoice.entity_id,
                    invoice.booking.entity_id,
                    invoice.total_amount,
                    invoice.payment_status,
                    invoice.invoice_number,
                    invoice.due_date.isoformat() if invoice.due_date else "",
                    invoice.line_description,
                    invoice.quantity,
                    invoice.unit_price,
                    invoice.tax_rate,
                    invoice.notes,
                    invoice.created_at.isoformat(),
                ),
            )

            connection.commit()

        except sqlite3.Error:
            if connection:
                connection.rollback()
            raise

        finally:
            if connection:
                connection.close()

    @staticmethod
    def find_all() -> list[Invoice]:
        """Return all invoices stored in the database."""
        bookings_by_id = {
            booking.entity_id: booking for booking in BookingRepository.find_all()
        }

        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                invoice_id,
                booking_id,
                total_amount,
                payment_status,
                invoice_number,
                due_date,
                line_description,
                quantity,
                unit_price,
                tax_rate,
                notes,
                created_at
            FROM invoices
            ORDER BY created_at DESC
            """
        )

        rows = cursor.fetchall()
        connection.close()

        invoices: list[Invoice] = []

        for row in rows:
            booking = bookings_by_id.get(row["booking_id"])

            if booking is None:
                continue

            due_date = None
            if row["due_date"]:
                due_date = datetime.fromisoformat(row["due_date"])

            invoices.append(
                Invoice(
                    entity_id=row["invoice_id"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    booking=booking,
                    total_amount=row["total_amount"],
                    payment_status=row["payment_status"],
                    invoice_number=row["invoice_number"] or "",
                    due_date=due_date,
                    line_description=row["line_description"] or "",
                    quantity=row["quantity"] or 1,
                    unit_price=row["unit_price"] or 0.0,
                    tax_rate=row["tax_rate"] or 0.0,
                    notes=row["notes"] or "",
                )
            )

        return invoices

    @staticmethod
    def delete(entity_id: str) -> None:
        """Delete an invoice and its related payment records."""
        connection = None

        try:
            connection = DatabaseManager.get_connection()
            cursor = connection.cursor()

            cursor.execute("DELETE FROM payments WHERE invoice_id = ?", (entity_id,))
            cursor.execute("DELETE FROM invoices WHERE invoice_id = ?", (entity_id,))

            connection.commit()

        except sqlite3.Error:
            if connection:
                connection.rollback()
            raise

        finally:
            if connection:
                connection.close()