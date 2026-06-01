"""Repository module for payment persistence operations."""

from datetime import datetime

from mysql.connector import Error

from src.database.database_manager import DatabaseManager
from src.models.payment import Payment
from src.repositories.invoice_repository import InvoiceRepository
from src.repositories.repository_interface import RepositoryInterface


class PaymentRepository(RepositoryInterface[Payment]):
    """
    Handles payment persistence operations.

    Payment SQL is kept inside the repository so invoice/payment
    workflow objects remain separate from storage details.
    """

    @staticmethod
    def save(entity: Payment) -> None:
        """Use the shared repository contract for polymorphic persistence."""
        PaymentRepository.save_payment(entity)

    @staticmethod
    def save_payment(payment: Payment) -> None:
        """Persist payment state without exposing SQL to the UI layer."""
        InvoiceRepository.save_invoice(payment.invoice)

        connection = None

        try:
            connection = DatabaseManager.get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO payments (
                    payment_id,
                    invoice_id,
                    amount,
                    payment_date,
                    method,
                    reference_number,
                    status,
                    notes,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    invoice_id = VALUES(invoice_id),
                    amount = VALUES(amount),
                    payment_date = VALUES(payment_date),
                    method = VALUES(method),
                    reference_number = VALUES(reference_number),
                    status = VALUES(status),
                    notes = VALUES(notes)
                """,
                PaymentRepository._to_database_values(payment),
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
    def find_all() -> list[Payment]:
        """Return Payment objects so higher layers avoid raw database rows."""
        invoices_by_id = {
            invoice.entity_id: invoice
            for invoice in InvoiceRepository.find_all()
        }

        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                payment_id,
                invoice_id,
                amount,
                payment_date,
                method,
                reference_number,
                status,
                notes,
                created_at
            FROM payments
            ORDER BY payment_date DESC
            """
        )

        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        payments: list[Payment] = []

        for row in rows:
            invoice = invoices_by_id.get(row["invoice_id"])

            if invoice is None:
                continue

            payments.append(
                PaymentRepository._from_database_row(row, invoice)
            )

        return payments

    @staticmethod
    def delete(entity_id: str) -> None:
        """Keep payment deletion isolated from the UI layer."""
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM payments WHERE payment_id = %s",
            (entity_id,),
        )

        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def _to_database_values(payment: Payment) -> tuple:
        """Keep payment database mapping centralised for maintainability."""
        return (
            payment.entity_id,
            payment.invoice.entity_id,
            payment.amount,
            payment.payment_date.isoformat(),
            payment.method,
            payment.reference_number,
            payment.status,
            payment.notes,
            payment.created_at.isoformat(),
        )

    @staticmethod
    def _from_database_row(row: dict, invoice) -> Payment:
        """Hide payment reconstruction so callers only handle entities."""
        return Payment(
            entity_id=row["payment_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            invoice=invoice,
            amount=row["amount"],
            payment_date=datetime.fromisoformat(row["payment_date"]),
            method=row["method"],
            reference_number=row["reference_number"],
            status=row["status"],
            notes=row["notes"] or "",
        )
