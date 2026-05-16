"""Repository module for payment persistence operations."""

from datetime import datetime

from src.database.database_manager import DatabaseManager
from src.models.payment import Payment
from src.repositories.invoice_repository import InvoiceRepository
from src.repositories.repository_interface import RepositoryInterface


class PaymentRepository(RepositoryInterface[Payment]):
    """Handles payment database operations."""

    @staticmethod
    def save(entity: Payment) -> None:
        """Persist a payment using the common repository interface."""
        PaymentRepository.save_payment(entity)

    @staticmethod
    def save_payment(payment: Payment) -> None:
        """Save payment information to the database."""
        InvoiceRepository.save_invoice(payment.invoice)

        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO payments (
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payment.entity_id,
                payment.invoice.entity_id,
                payment.amount,
                payment.payment_date.isoformat(),
                payment.method,
                payment.reference_number,
                payment.status,
                payment.notes,
                payment.created_at.isoformat(),
            ),
        )

        connection.commit()
        connection.close()

    @staticmethod
    def find_all() -> list[Payment]:
        """Return all payments stored in the database."""
        invoices_by_id = {
            invoice.entity_id: invoice for invoice in InvoiceRepository.find_all()
        }

        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

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
        connection.close()

        payments: list[Payment] = []

        for row in rows:
            invoice = invoices_by_id.get(row["invoice_id"])

            if invoice is None:
                continue

            payments.append(
                Payment(
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
            )

        return payments

    @staticmethod
    def delete(entity_id: str) -> None:
        """Delete a payment by identifier."""
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM payments WHERE payment_id = ?", (entity_id,))

        connection.commit()
        connection.close()
