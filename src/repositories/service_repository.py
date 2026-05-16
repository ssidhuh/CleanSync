"""Repository module for cleaning service persistence operations."""

from datetime import datetime

from src.database.database_manager import DatabaseManager
from src.models.service import CleaningService
from src.repositories.repository_interface import RepositoryInterface


class ServiceRepository(RepositoryInterface[CleaningService]):
    """Handles cleaning service database operations."""

    @staticmethod
    def save(entity: CleaningService) -> None:
        """Persist a cleaning service using the common repository interface."""
        ServiceRepository.save_service(entity)

    @staticmethod
    def save_service(cleaning_service: CleaningService) -> None:
        """Save cleaning service information to the database."""
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO cleaning_services (
                service_id,
                service_name,
                description,
                duration_hours,
                base_price,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                cleaning_service.entity_id,
                cleaning_service.service_name,
                cleaning_service.description,
                cleaning_service.duration_hours,
                cleaning_service.base_price,
                cleaning_service.created_at.isoformat(),
            ),
        )
        connection.commit()
        connection.close()

    @staticmethod
    def find_all() -> list[CleaningService]:
        """Return all cleaning services stored in the database."""
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                service_id,
                service_name,
                description,
                duration_hours,
                base_price,
                created_at
            FROM cleaning_services
            ORDER BY service_name
            """
        )
        rows = cursor.fetchall()
        connection.close()

        return [
            CleaningService(
                entity_id=row["service_id"],
                created_at=datetime.fromisoformat(row["created_at"]),
                service_name=row["service_name"],
                description=row["description"],
                duration_hours=row["duration_hours"],
                base_price=row["base_price"],
            )
            for row in rows
        ]

    @staticmethod
    def delete(entity_id: str) -> None:
        """Delete a cleaning service by identifier."""
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM cleaning_services WHERE service_id = ?",
            (entity_id,),
        )
        connection.commit()
        connection.close()
