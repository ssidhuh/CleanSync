"""Repository module for cleaner persistence operations."""

from datetime import datetime

from src.database.database_manager import DatabaseManager
from src.models.cleaner import Cleaner
from src.repositories.repository_interface import RepositoryInterface


class CleanerRepository(RepositoryInterface[Cleaner]):
    """Handles cleaner database operations."""

    @staticmethod
    def save(entity: Cleaner) -> None:
        """Persist a cleaner using the common repository interface."""
        CleanerRepository.save_cleaner(entity)

    @staticmethod
    def save_cleaner(cleaner: Cleaner) -> None:
        """Save cleaner information to the database."""
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO cleaners (
                cleaner_id,
                first_name,
                last_name,
                email,
                phone_number,
                hourly_rate,
                rating,
                status,
                specializations,
                service_area,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cleaner.entity_id,
                cleaner.first_name,
                cleaner.last_name,
                cleaner.email,
                cleaner.phone_number,
                cleaner.hourly_rate,
                cleaner.rating,
                cleaner.status,
                cleaner.specializations,
                cleaner.service_area,
                cleaner.created_at.isoformat(),
            ),
        )

        connection.commit()
        connection.close()

    @staticmethod
    def find_all() -> list[Cleaner]:
        """Return all cleaners stored in the database."""
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                cleaner_id,
                first_name,
                last_name,
                email,
                phone_number,
                hourly_rate,
                rating,
                status,
                specializations,
                service_area,
                created_at
            FROM cleaners
            ORDER BY last_name, first_name
            """
        )

        rows = cursor.fetchall()
        connection.close()

        return [
            Cleaner(
                entity_id=row["cleaner_id"],
                created_at=datetime.fromisoformat(row["created_at"]),
                first_name=row["first_name"],
                last_name=row["last_name"],
                email=row["email"],
                phone_number=row["phone_number"],
                hourly_rate=row["hourly_rate"],
                rating=row["rating"],
                status=row["status"],
                specializations=row["specializations"],
                service_area=row["service_area"],
            )
            for row in rows
        ]

    @staticmethod
    def delete(entity_id: str) -> None:
        """Delete a cleaner by identifier."""
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM cleaners WHERE cleaner_id = ?", (entity_id,))

        connection.commit()
        connection.close()