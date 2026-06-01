"""Base entity module for shared application model behaviour."""

from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4


@dataclass
class BaseEntity(ABC):
    """
    Provides shared behaviour for all business entities.

    A shared parent entity keeps object identity and creation
    rules consistent across the application architecture.
    """

    entity_id: str
    created_at: datetime

    @property
    def has_valid_identifier(self) -> bool:
        """Centralise identifier validation for all inherited entities."""
        return bool(self.entity_id.strip())

    @property
    def formatted_created_date(self) -> str:
        """Provide one reusable entity date display format."""
        return self.created_at.strftime("%d %b %Y %H:%M")

    @staticmethod
    def generate_id() -> str:
        """Generate consistent unique identifiers across the system."""
        return str(uuid4())

    @classmethod
    def create_timestamp(cls) -> datetime:
        """Keep entity creation timestamps standardised."""
        return datetime.now()

    def validate_entity(self) -> bool:
        """Provide reusable base validation for inherited entities."""
        return self.has_valid_identifier
