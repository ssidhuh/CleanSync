"""Payment entity module."""

from dataclasses import dataclass
from datetime import datetime

from src.models.base_entity import BaseEntity
from src.models.invoice import Invoice


@dataclass
class Payment(BaseEntity):
    """Represents a payment recorded against an invoice."""

    invoice: Invoice
    amount: float
    payment_date: datetime
    method: str
    reference_number: str
    status: str
    notes: str = ""
