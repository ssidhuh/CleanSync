"""Repository module for invoice persistence operations."""

from datetime import datetime

from mysql.connector import Error

from src.database.database_manager import DatabaseManager
from src.models.invoice import Invoice
from src.repositories.booking_repository import BookingRepository
from src.repositories.repository_interface import RepositoryInterface


class InvoiceRepository(RepositoryInterface[Invoice]):
    """
    Handles invoice persistence operations.

    Financial storage logic is separated from invoice entities
    to keep database responsibilities isolated from business behaviour.
    """

    @staticmethod
    def save(entity: Invoice) -> None:
        """Use the shared repository contract for polymorphic persistence."""
        InvoiceRepository.save_invoice(entity)

    @staticmethod
    def save_invoice(invoice: Invoice) -> None:
        """Persist invoice state without exposing SQL to the UI layer."""
        connection = None

        try:
            connection = DatabaseManager.get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO invoices (
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
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    booking_id = VALUES(booking_id),
                    total_amount = VALUES(total_amount),
                    payment_status = VALUES(payment_status),
                    invoice_number = VALUES(invoice_number),
                    due_date = VALUES(due_date),
                    line_description = VALUES(line_description),
                    quantity = VALUES(quantity),
                    unit_price = VALUES(unit_price),
                    tax_rate = VALUES(tax_rate),
                    notes = VALUES(notes)
                """,
                InvoiceRepository._to_database_values(invoice),
            )

            connection.commit()
            cursor.close()

        except Error:
            if connection:
                connection.rollback()
            raise

        finally:
            if connection:
                connection.close()

    @staticmethod
    def find_all() -> list[Invoice]:
        """Return Invoice objects so higher layers avoid raw database rows."""
        bookings_by_id = {
            booking.entity_id: booking
            for booking in BookingRepository.find_all()
        }

        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)

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
        cursor.close()
        connection.close()

        invoices: list[Invoice] = []

        for row in rows:
            booking = bookings_by_id.get(row["booking_id"])

            if booking is None:
                continue

            invoices.append(
                InvoiceRepository._from_database_row(row, booking)
            )

        return invoices

    @staticmethod
    def delete(entity_id: str) -> None:
        """Remove related payments before deleting invoice records."""
        connection = None

        try:
            connection = DatabaseManager.get_connection()
            cursor = connection.cursor()

            cursor.execute(
                "DELETE FROM payments WHERE invoice_id = %s",
                (entity_id,),
            )

            cursor.execute(
                "DELETE FROM invoices WHERE invoice_id = %s",
                (entity_id,),
            )

            connection.commit()
            cursor.close()

        except Error:
            if connection:
                connection.rollback()
            raise

        finally:
            if connection:
                connection.close()

    @staticmethod
    def _to_database_values(invoice: Invoice) -> tuple:
        """Keep invoice database mapping centralised for maintainability."""
        return (
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
        )

    @staticmethod
    def _from_database_row(row: dict, booking) -> Invoice:
        """Hide invoice reconstruction so callers only handle entities."""
        due_date = None

        if row["due_date"]:
            due_date = datetime.fromisoformat(row["due_date"])

        return Invoice(
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