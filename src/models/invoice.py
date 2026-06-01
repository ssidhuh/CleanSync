"""Invoice entity module."""

from dataclasses import dataclass
from datetime import datetime

from src.models.base_entity import BaseEntity
from src.models.booking import Booking


@dataclass
class Invoice(BaseEntity):
    """
    Represents billing information for bookings.

    Invoice behaviour is kept inside the entity so financial
    rules are not duplicated across views and repositories.
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

    PAID_STATUS = "paid"
    DRAFT_STATUS = "draft"
    SENT_STATUS = "sent"
    OVERDUE_STATUS = "overdue"
    CANCELLED_STATUS = "cancelled"

    @property
    def is_paid(self) -> bool:
        """Keep payment-state checks encapsulated inside the invoice."""
        return self.payment_status == self.PAID_STATUS

    @property
    def is_active(self) -> bool:
        """Separate payable invoices from cancelled accounting records."""
        return self.payment_status != self.CANCELLED_STATUS

    @property
    def is_overdue(self) -> bool:
        """Keep due-date rules reusable across dashboards and reports."""
        if self.due_date is None or self.is_paid:
            return False

        return datetime.now() > self.due_date

    @property
    def subtotal(self) -> float:
        """Centralise invoice subtotal calculation."""
        return round(self.quantity * self.unit_price, 2)

    @property
    def tax_amount(self) -> float:
        """Keep tax calculation consistent with total invoice pricing."""
        return round(self.subtotal * (self.tax_rate / 100), 2)

    def calculate_total(self) -> float:
        """Use one method for invoice totals across UI and persistence."""
        return round(self.subtotal + self.tax_amount, 2)

    def refresh_total_amount(self) -> None:
        """Keep stored invoice total aligned with line item data."""
        self.total_amount = self.calculate_total()

    def mark_as_paid(self) -> None:
        """Control paid workflow through the entity."""
        self.payment_status = self.PAID_STATUS

    def mark_as_unpaid(self) -> None:
        """Return invoice to draft state when payment is not completed."""
        self.payment_status = self.DRAFT_STATUS

    def mark_as_sent(self) -> None:
        """Keep invoice workflow transitions explicit."""
        self.payment_status = self.SENT_STATUS

    def cancel_invoice(self) -> None:
        """Prevent external layers from directly changing cancellation state."""
        self.payment_status = self.CANCELLED_STATUS

    def update_due_date(self, new_due_date: datetime) -> None:
        """Encapsulate due-date changes for future validation reuse."""
        self.due_date = new_due_date

    def validate_financial_details(self) -> bool:
        """Keep accounting validation independent from form-specific code."""
        return (
            self.quantity > 0
            and self.unit_price >= 0
            and self.tax_rate >= 0
            and self.total_amount >= 0
        )

    def generate_invoice_summary(self) -> str:
        """Create one reusable invoice summary format."""
        customer_name = self.booking.customer.full_name

        return (
            f"Invoice {self.invoice_number} for {customer_name} | "
            f"Amount: €{self.total_amount:.2f} | "
            f"Status: {self.payment_status}"
        )
