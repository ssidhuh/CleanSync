"""Customer entity module."""

from dataclasses import dataclass

from src.models.base_entity import BaseEntity


@dataclass
class Customer(BaseEntity):
    """
    Represents a customer who requests cleaning services.

    Customer behaviour is encapsulated inside the entity
    to reduce duplicated validation logic across the UI layer.
    """

    first_name: str
    last_name: str
    phone_number: str
    email: str
    address: str

    ACTIVE_STATUS = "Active"
    INACTIVE_STATUS = "Inactive"

    @property
    def full_name(self) -> str:
        """Provide a reusable customer display format."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_active(self) -> bool:
        """
        Keep customer activity checks centralised inside the entity.
        """
        return bool(
            self.first_name.strip()
            and self.last_name.strip()
            and self.validate_contact_information()
        )

    @property
    def formatted_phone_number(self) -> str:
        """Provide consistent Latvian contact formatting."""
        return self.phone_number.strip()

    def validate_contact_information(self) -> bool:
        """
        Keep customer validation rules independent from the UI layer.
        """
        return (
            self.__has_valid_email()
            and self.__has_valid_phone_number()
            and self.__has_valid_address()
        )

    def update_address(self, new_address: str) -> None:
        """Encapsulate customer address updates inside the entity."""
        self.address = new_address.strip()

    def update_phone_number(self, new_phone_number: str) -> None:
        """Prevent direct external manipulation of contact formatting."""
        self.phone_number = new_phone_number.strip()

    def has_complete_profile(self) -> bool:
        """
        Support future booking validation using reusable profile checks.
        """
        return all(
            [
                self.first_name.strip(),
                self.last_name.strip(),
                self.address.strip(),
                self.validate_contact_information(),
            ]
        )

    def __has_valid_email(self) -> bool:
        """Restrict internal validation rules from external access."""
        return (
            "@" in self.email
            and "." in self.email
            and len(self.email.strip()) >= 5
        )

    def __has_valid_phone_number(self) -> bool:
        """Keep Latvian phone validation consistent across the system."""
        cleaned_phone = self.phone_number.strip()

        if not cleaned_phone.startswith("+371"):
            return False

        numeric_part = cleaned_phone.replace("+371", "")

        return numeric_part.isdigit() and len(numeric_part) == 8

    def __has_valid_address(self) -> bool:
        """Ensure customer records contain usable booking locations."""
        return len(self.address.strip()) >= 5
