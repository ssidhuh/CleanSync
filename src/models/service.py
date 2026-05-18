"""Cleaning service entity module."""

from dataclasses import dataclass

from src.models.base_entity import BaseEntity


@dataclass
class CleaningService(BaseEntity):
    """
    Represents a cleaning service offered by the company.

    Separating services into their own entity allows the system
    to support multiple cleaning categories and pricing models.
    """

    service_name: str
    description: str
    duration_hours: float
    base_price: float
    category: str = "Residential"

    def calculate_service_cost(self) -> float:
        """
        Return the standard service cost before adjustments.

        Returns:
            float: Base service price.
        """
        return round(self.base_price, 2)
