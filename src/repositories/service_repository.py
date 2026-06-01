"""Repository module for cleaning service persistence operations."""

from datetime import datetime

from src.database.database_manager import DatabaseManager
from src.models.service import CleaningService
from src.repositories.repository_interface import RepositoryInterface


class ServiceRepository(RepositoryInterface[CleaningService]):
    """
    Handles cleaning service persistence operations.

    Service SQL is isolated inside the repository so business
    entities remain independent from database-specific behaviour.
    """

    @staticmethod
    def save(entity: CleaningService) -> None:
        """Use the shared repository contract for polymorphic persistence."""
        ServiceRepository.save_service(entity)

    @staticmethod
    def _ensure_category_column() -> None:
        """Preserve compatibility with older database structures."""
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SHOW COLUMNS FROM cleaning_services LIKE 'category'"
        )

        column_exists = cursor.fetchone() is not None

        if not column_exists:
            cursor.execute(
                """
                ALTER TABLE cleaning_services
                ADD COLUMN category TEXT DEFAULT 'Residential'
                """
            )

        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def save_service(cleaning_service: CleaningService) -> None:
        """Persist service state without exposing SQL to the UI layer."""
        ServiceRepository._ensure_category_column()

        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO cleaning_services (
                service_id,
                service_name,
                description,
                category,
                duration_hours,
                base_price,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                service_name = VALUES(service_name),
                description = VALUES(description),
                category = VALUES(category),
                duration_hours = VALUES(duration_hours),
                base_price = VALUES(base_price)
            """,
            ServiceRepository._to_database_values(cleaning_service),
        )

        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def find_all() -> list[CleaningService]:
        """Return entity objects instead of exposing raw database rows."""
        ServiceRepository._ensure_category_column()

        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                service_id,
                service_name,
                description,
                category,
                duration_hours,
                base_price,
                created_at
            FROM cleaning_services
            ORDER BY service_name
            """
        )

        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        return [
            ServiceRepository._from_database_row(row)
            for row in rows
        ]

    @staticmethod
    def delete(entity_id: str) -> None:
        """Keep deletion behaviour isolated from the user interface."""
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM cleaning_services WHERE service_id = %s",
            (entity_id,),
        )

        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def _to_database_values(
        cleaning_service: CleaningService,
    ) -> tuple:
        """Keep database mapping centralised for easier maintenance."""
        return (
            cleaning_service.entity_id,
            cleaning_service.service_name,
            cleaning_service.description,
            cleaning_service.category,
            cleaning_service.duration_hours,
            cleaning_service.base_price,
            cleaning_service.created_at.isoformat(),
        )

    @staticmethod
    def _from_database_row(row: dict) -> CleaningService:
        """Hide row reconstruction so callers only handle entities."""
        return CleaningService(
            entity_id=row["service_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            service_name=row["service_name"],
            description=row["description"],
            duration_hours=row["duration_hours"],
            base_price=row["base_price"],
            category=row["category"] or "Residential",
        )
