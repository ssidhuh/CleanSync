"""Repository module for cleaner persistence operations."""

from datetime import datetime

from mysql.connector import IntegrityError

from src.database.database_manager import DatabaseManager
from src.models.cleaner import Cleaner
from src.repositories.repository_interface import RepositoryInterface


class CleanerRepository(RepositoryInterface[Cleaner]):
    """
    Handles cleaner persistence operations.

    Keeping SQL in the repository preserves separation between
    business objects and database-specific storage details.
    """

    @staticmethod
    def save(entity: Cleaner) -> None:
        """Use the shared repository contract for polymorphic persistence."""
        CleanerRepository.save_cleaner(entity)

    @staticmethod
    def save_cleaner(cleaner: Cleaner) -> None:
        """Persist cleaner state without exposing SQL to the UI layer."""
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO cleaners (
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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                first_name = VALUES(first_name),
                last_name = VALUES(last_name),
                email = VALUES(email),
                phone_number = VALUES(phone_number),
                hourly_rate = VALUES(hourly_rate),
                rating = VALUES(rating),
                status = VALUES(status),
                specializations = VALUES(specializations),
                service_area = VALUES(service_area)
            """,
            CleanerRepository._to_database_values(cleaner),
        )

        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def find_all() -> list[Cleaner]:
        """Return Cleaner objects so higher layers work with entities."""
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)

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
        cursor.close()
        connection.close()

        return [
            CleanerRepository._from_database_row(row)
            for row in rows
        ]

    @staticmethod
    def delete(entity_id: str) -> None:
        """Protect booking history by blocking unsafe cleaner deletion."""
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "DELETE FROM cleaners WHERE cleaner_id = %s",
                (entity_id,),
            )
            connection.commit()
        except IntegrityError as error:
            connection.rollback()
            raise ValueError(
                "This cleaner cannot be deleted because they are linked to existing bookings."
            ) from error
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def _to_database_values(cleaner: Cleaner) -> tuple:
        """Keep database mapping in one place for easier maintenance."""
        return (
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
        )

    @staticmethod
    def _from_database_row(row: dict) -> Cleaner:
        """Hide row reconstruction so callers only handle Cleaner objects."""
        return Cleaner(
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
