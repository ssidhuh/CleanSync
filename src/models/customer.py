"""Customer entity module."""

from dataclasses import dataclass

from src.models.base_entity import BaseEntity


@dataclass
class Customer(BaseEntity):
    """
    Represents a customer who requests cleaning services.

    The customer entity stores contact and address data
    required for booking management and communication.
    """

    first_name: str
    last_name: str
    phone_number: str
    email: str
    address: str

    @property
    def full_name(self) -> str:
        """
        Combine first and last names into a display-friendly format.

        Returns:
            str: Customer full name.
        """
        return f"{self.first_name} {self.last_name}"

    def validate_contact_information(self) -> bool:
        """
        Validate customer communication details before persistence.

        Returns:
            bool: True when minimum validation rules are satisfied.
        """
        return "@" in self.email and len(self.phone_number) >= 8
