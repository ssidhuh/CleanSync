"""Invoice entity module."""

from dataclasses import dataclass
from datetime import datetime

from src.models.base_entity import BaseEntity
from src.models.booking import Booking


@dataclass
class Invoice(BaseEntity):
    """
    Represents billing information for bookings.

    The invoice keeps financial details separate from booking
    scheduling details so accounting data can evolve independently.
    """

    booking: Booking
    total_amount: float
    payment_status: str
    invoice_number: str = ""
    due_date: datetime | None = None
    line_description: str = ""
    quantity: int = 1
    unit_price: float = 0.0
    tax_rate: float = 0.0
    notes: str = ""

    def mark_as_paid(self) -> None:
        """Update invoice payment status after successful payment."""
        self.payment_status = "paid"

    def mark_as_unpaid(self) -> None:
        """Restore invoice payment state if payment processing fails."""
        self.payment_status = "draft"

    def generate_invoice_summary(self) -> str:
        """Generate a readable invoice summary for reporting."""
        customer_name = self.booking.customer.full_name

        return (
            f"Invoice {self.invoice_number} for {customer_name} | "
            f"Amount: ${self.total_amount:.2f} | "
            f"Status: {self.payment_status}"
        )
