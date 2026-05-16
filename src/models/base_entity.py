"""Base entity module for shared application model behaviour."""

from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4


@dataclass
class BaseEntity(ABC):
    """
    Provides shared attributes for all business entities.

    A common parent class reduces duplication and keeps
    object creation behaviour consistent across the system.
    """

    entity_id: str
    created_at: datetime

    @staticmethod
    def generate_id() -> str:
        """
        Generate a unique identifier for application entities.

        Returns:
            str: Randomly generated unique identifier.
        """
        return str(uuid4())
