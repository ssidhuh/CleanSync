"""Repository abstraction for CleanSync persistence classes."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class RepositoryInterface(ABC, Generic[T]):
    """
    Defines common persistence behaviour for repository classes.

    The interface supports the assessment requirement for abstraction while
    keeping SQL details hidden from the user interface and service layers.
    """

    @staticmethod
    @abstractmethod
    def save(entity: T) -> None:
        """Persist an entity."""

    @staticmethod
    @abstractmethod
    def find_all() -> list[T]:
        """Return all stored entities."""

    @staticmethod
    @abstractmethod
    def delete(entity_id: str) -> None:
        """Delete an entity by its identifier."""
