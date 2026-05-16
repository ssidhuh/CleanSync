"""Repository module for customer persistence operations."""

from datetime import datetime

from src.database.database_manager import DatabaseManager
from src.models.customer import Customer
from src.repositories.repository_interface import RepositoryInterface


class CustomerRepository(RepositoryInterface[Customer]):
    """
    Handles customer database operations.

    Keeping customer SQL separate from the user interface
    prevents the GUI from becoming difficult to maintain.
    """

    @staticmethod
    def save(entity: Customer) -> None:
        """Persist a customer using the common repository interface."""
        CustomerRepository.save_customer(entity)

    @staticmethod
    def save_customer(customer: Customer) -> None:
        """
        Save customer information to the database.

        Args:
            customer (Customer): Customer instance to persist.
        """
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO customers (
                customer_id,
                first_name,
                last_name,
                phone_number,
                email,
                address,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                customer.entity_id,
                customer.first_name,
                customer.last_name,
                customer.phone_number,
                customer.email,
                customer.address,
                str(customer.created_at),
            ),
        )

        connection.commit()
        connection.close()

    @staticmethod
    def find_all() -> list[Customer]:
        """
        Return all customers stored in the database.

        Returns:
            list[Customer]: Customer objects reconstructed from SQLite rows.
        """
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
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
        connection.close()

        return [
            Customer(
                entity_id=row["customer_id"],
                created_at=datetime.fromisoformat(row["created_at"]),
                first_name=row["first_name"],
                last_name=row["last_name"],
                phone_number=row["phone_number"],
                email=row["email"],
                address=row["address"],
            )
            for row in rows
        ]

    @staticmethod
    def delete(entity_id: str) -> None:
        """
        Delete a customer by identifier.

        Args:
            entity_id (str): Customer identifier.
        """
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM customers WHERE customer_id = ?", (entity_id,))
        connection.commit()
        connection.close()
