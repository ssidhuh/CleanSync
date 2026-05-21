"""Cleaning service entity module."""

from dataclasses import dataclass

from src.models.base_entity import BaseEntity


@dataclass
class CleaningService(BaseEntity):
    """
    Represents a cleaning service offered by the company.

    Pricing and category behaviour are kept inside the entity
    so bookings and invoices can reuse the same service rules.
    """

    service_name: str
    description: str
    duration_hours: float
    base_price: float
    category: str = "Residential"

    DEFAULT_CATEGORY = "Residential"
    MINIMUM_PRICE = 1.0
    MINIMUM_DURATION = 0.5

    @property
    def is_active(self) -> bool:
        """Keep service availability checks independent from the UI."""
        return self.validate_service_details()

    @property
    def hourly_equivalent_price(self) -> float:
        """Provide a reusable price comparison value for dashboards."""
        if self.duration_hours <= 0:
            return 0.0

        return round(self.base_price / self.duration_hours, 2)

    @property
    def category_list(self) -> list[str]:
        """Normalise service categories for filtering and display."""
        return [
            item.strip()
            for item in self.category.split(",")
            if item.strip()
        ]

    def calculate_service_cost(self) -> float:
        """Return the total base price for the full service process."""
        return round(self.base_price, 2)

    def update_price(self, new_price: float) -> None:
        """Protect service pricing from invalid external updates."""
        if new_price < self.MINIMUM_PRICE:
            raise ValueError("Service price must be greater than zero.")

        self.base_price = new_price

    def update_duration(self, new_duration: float) -> None:
        """Keep duration rules inside the service entity."""
        if new_duration < self.MINIMUM_DURATION:
            raise ValueError("Service duration is too short.")

        self.duration_hours = new_duration

    def belongs_to_category(self, category_name: str) -> bool:
        """Keep category matching reusable across service views."""
        return category_name.strip() in self.category_list

    def validate_service_details(self) -> bool:
        """Keep service validation independent from form-specific code."""
        return (
            bool(self.service_name.strip())
            and bool(self.description.strip())
            and self.base_price >= self.MINIMUM_PRICE
            and self.duration_hours >= self.MINIMUM_DURATION
        )