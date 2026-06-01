"""Repository module for customer persistence operations."""

from datetime import datetime

from mysql.connector import IntegrityError

from src.database.database_manager import DatabaseManager
from src.models.customer import Customer
from src.repositories.repository_interface import RepositoryInterface


class CustomerRepository(RepositoryInterface[Customer]):
    """
    Handles customer persistence operations.

    Keeping SQL inside the repository prevents database logic
    from leaking into the user interface.
    """

    @staticmethod
    def save(entity: Customer) -> None:
        """Use the shared repository contract for polymorphic persistence."""
        CustomerRepository.save_customer(entity)

    @staticmethod
    def save_customer(customer: Customer) -> None:
        """Persist customer state without exposing SQL to the UI layer."""
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO customers (
                customer_id,
                first_name,
                last_name,
                phone_number,
                email,
                address,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                first_name = VALUES(first_name),
                last_name = VALUES(last_name),
                phone_number = VALUES(phone_number),
                email = VALUES(email),
                address = VALUES(address)
            """,
            CustomerRepository._to_database_values(customer),
        )

        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def find_all() -> list[Customer]:
        """Return Customer objects so higher layers avoid raw database rows."""
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                customer_id,
                first_name,
                last_name,
                phone_number,
                email,
                address,
                created_at
            FROM customers
            ORDER BY last_name, first_name
            """
        )

        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        return [
            CustomerRepository._from_database_row(row)
            for row in rows
        ]

    @staticmethod
    def delete(entity_id: str) -> None:
        """Protect booking history by blocking unsafe customer deletion."""
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "DELETE FROM customers WHERE customer_id = %s",
                (entity_id,),
            )
            connection.commit()
        except IntegrityError as error:
            connection.rollback()
            raise ValueError(
                "This customer cannot be deleted because they are linked to existing bookings."
            ) from error
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def _to_database_values(customer: Customer) -> tuple:
        """Keep database mapping in one place for easier maintenance."""
        return (
            customer.entity_id,
            customer.first_name,
            customer.last_name,
            customer.phone_number,
            customer.email,
            customer.address,
            customer.created_at.isoformat(),
        )

    @staticmethod
    def _from_database_row(row: dict) -> Customer:
        """Hide row reconstruction so callers only handle Customer objects."""
        return Customer(
            entity_id=row["customer_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            first_name=row["first_name"],
            last_name=row["last_name"],
            phone_number=row["phone_number"],
            email=row["email"],
            address=row["address"],
        )
