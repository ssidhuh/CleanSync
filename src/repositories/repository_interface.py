"""Repository abstraction for CleanSync persistence classes."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class RepositoryInterface(ABC, Generic[T]):
    """
    Defines a shared persistence contract for repository classes.

    The interface keeps storage behaviour consistent while allowing
    each repository to implement entity-specific SQL details separately.
    """

    @staticmethod
    @abstractmethod
    def save(entity: T) -> None:
        """Require every repository to support object persistence."""

    @staticmethod
    @abstractmethod
    def find_all() -> list[T]:
        """Require every repository to return entity objects, not raw rows."""

    @staticmethod
    @abstractmethod
    def delete(entity_id: str) -> None:
        """Require deletion behaviour without exposing SQL to the UI."""