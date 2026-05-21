"""Cleaner entity module."""

from dataclasses import dataclass

from src.models.base_entity import BaseEntity


@dataclass
class Cleaner(BaseEntity):
    """
    Represents an employee assigned to cleaning bookings.

    Cleaner state and profile rules are kept inside the entity
    so scheduling decisions do not depend only on UI logic.
    """

    first_name: str
    last_name: str
    email: str
    phone_number: str
    hourly_rate: float
    rating: float
    status: str
    specializations: str
    service_area: str = ""

    AVAILABLE_STATUS = "Available"
    ON_JOB_STATUS = "On Job"
    INACTIVE_STATUS = "Inactive"

    @property
    def full_name(self) -> str:
        """Provide one consistent display name across the system."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_available(self) -> bool:
        """Keep availability checks encapsulated inside the entity."""
        return self.status == self.AVAILABLE_STATUS

    @property
    def is_active(self) -> bool:
        """Separate inactive cleaners from assignable booking resources."""
        return self.status != self.INACTIVE_STATUS

    @property
    def specialization_list(self) -> list[str]:
        """Normalise specialisations for cleaner-service matching."""
        return [
            item.strip()
            for item in self.specializations.replace(";", ",").replace("|", ",").split(",")
            if item.strip()
        ]

    def mark_unavailable(self) -> None:
        """Synchronise cleaner state when assigned to a booking."""
        self.status = self.ON_JOB_STATUS

    def mark_available(self) -> None:
        """Release cleaner state after completion or cancellation."""
        self.status = self.AVAILABLE_STATUS

    def deactivate(self) -> None:
        """Control inactive state through the entity instead of the UI."""
        self.status = self.INACTIVE_STATUS

    def offers_service(self, service_name: str) -> bool:
        """Keep matching behaviour reusable across booking and schedule logic."""
        selected_service = service_name.strip().lower()

        return any(
            specialization.lower() == selected_service
            or specialization.lower() in selected_service
            or selected_service in specialization.lower()
            for specialization in self.specialization_list
        )

    def update_hourly_rate(self, new_rate: float) -> None:
        """Protect cleaner pricing from invalid external updates."""
        if new_rate <= 0:
            raise ValueError("Hourly rate must be greater than zero.")

        self.hourly_rate = new_rate

    def validate_profile(self) -> bool:
        """Keep cleaner validation independent from form-specific code."""
        return (
            self.__has_valid_email()
            and self.__has_valid_phone_number()
            and self.__has_valid_rate()
            and self.__has_valid_rating()
        )

    def __has_valid_email(self) -> bool:
        """Hide internal validation details from external layers."""
        return "@" in self.email and "." in self.email

    def __has_valid_phone_number(self) -> bool:
        """Apply the same Latvian phone rule used by customer profiles."""
        cleaned_phone = (
            self.phone_number.strip()
            .replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
        )

        if not cleaned_phone.startswith("+371"):
            return False

        local_number = cleaned_phone[4:]
        return local_number.isdigit() and len(local_number) == 8

    def __has_valid_rate(self) -> bool:
        """Keep payment-related limits inside the domain entity."""
        return self.hourly_rate > 0

    def __has_valid_rating(self) -> bool:
        """Preserve rating consistency before persistence."""
        return 1 <= self.rating <= 5