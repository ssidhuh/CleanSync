"""Payment entity module."""

from dataclasses import dataclass
from datetime import datetime

from src.models.base_entity import BaseEntity
from src.models.invoice import Invoice


@dataclass
class Payment(BaseEntity):
    """
    Represents a payment recorded against an invoice.

    Payment workflow behaviour is encapsulated inside the entity
    to keep financial state management independent from the UI layer.
    """

    invoice: Invoice
    amount: float
    payment_date: datetime
    method: str
    reference_number: str
    status: str
    notes: str = ""

    COMPLETED_STATUS = "Completed"
    PENDING_STATUS = "Pending"
    FAILED_STATUS = "Failed"
    REFUNDED_STATUS = "Refunded"

    @property
    def is_completed(self) -> bool:
        """Keep payment-state checks reusable across the system."""
        return self.status == self.COMPLETED_STATUS

    @property
    def is_pending(self) -> bool:
        """Avoid duplicated workflow checks inside views."""
        return self.status == self.PENDING_STATUS

    @property
    def is_failed(self) -> bool:
        """Separate failed transactions from successful payments."""
        return self.status == self.FAILED_STATUS

    @property
    def formatted_amount(self) -> str:
        """Provide one reusable currency display format."""
        return f"€{self.amount:.2f}"

    def mark_as_completed(self) -> None:
        """Synchronise invoice and payment workflow states."""
        self.status = self.COMPLETED_STATUS
        self.invoice.mark_as_paid()

    def mark_as_pending(self) -> None:
        """Keep pending workflow transitions inside the entity."""
        self.status = self.PENDING_STATUS

    def mark_as_failed(self) -> None:
        """Prevent direct external manipulation of failed states."""
        self.status = self.FAILED_STATUS
        self.invoice.mark_as_unpaid()

    def refund_payment(self) -> None:
        """Encapsulate refund behaviour for future accounting reuse."""
        self.status = self.REFUNDED_STATUS
        self.invoice.mark_as_unpaid()

    def validate_payment_details(self) -> bool:
        """Keep payment validation independent from form-specific code."""
        return (
            self.amount > 0
            and bool(self.method.strip())
            and bool(self.reference_number.strip())
        )

    def generate_payment_summary(self) -> str:
        """Create one reusable payment summary format."""
        return (
            f"Payment {self.reference_number} | "
            f"Amount: {self.formatted_amount} | "
            f"Status: {self.status}"
        )
