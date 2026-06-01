"""Repository module for booking persistence operations."""

from datetime import datetime

from mysql.connector import IntegrityError

from src.database.database_manager import DatabaseManager
from src.models.booking import Booking
from src.repositories.cleaner_repository import CleanerRepository
from src.repositories.customer_repository import CustomerRepository
from src.repositories.repository_interface import RepositoryInterface
from src.repositories.service_repository import ServiceRepository


class BookingRepository(RepositoryInterface[Booking]):
    """Handles booking database operations."""

    @staticmethod
    def save(entity: Booking) -> None:
        """Persist a booking using the common repository interface."""
        BookingRepository.save_booking(entity)

    @staticmethod
    def _ensure_booking_numbers() -> None:
        """Generate booking numbers for older bookings that do not have one."""

        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT booking_id, booking_number
            FROM bookings
            ORDER BY created_at
            """
        )

        rows = cursor.fetchall()

        counter = 1

        for row in rows:
            if not row["booking_number"]:
                cursor.execute(
                    """
                    UPDATE bookings
                    SET booking_number = %s
                    WHERE booking_id = %s
                    """,
                    (f"BOOK-{counter:04d}", row["booking_id"]),
                )

            counter += 1

        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def save_booking(booking: Booking) -> None:
        """Save booking information to the database."""

        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO bookings (
                booking_id,
                booking_number,
                customer_id,
                cleaner_id,
                service_id,
                booking_date,
                end_time,
                address,
                total_amount,
                notes,
                status,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                booking_number = VALUES(booking_number),
                customer_id = VALUES(customer_id),
                cleaner_id = VALUES(cleaner_id),
                service_id = VALUES(service_id),
                booking_date = VALUES(booking_date),
                end_time = VALUES(end_time),
                address = VALUES(address),
                total_amount = VALUES(total_amount),
                notes = VALUES(notes),
                status = VALUES(status)
            """,
            (
                booking.entity_id,
                booking.booking_number,
                booking.customer.entity_id,
                booking.cleaner.entity_id,
                booking.cleaning_service.entity_id,
                booking.booking_date.isoformat(),
                booking.end_time.isoformat() if booking.end_time else "",
                booking.address,
                booking.total_amount,
                booking.notes,
                booking.status,
                booking.created_at.isoformat(),
            ),
        )

        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def find_all() -> list[Booking]:
        """Return all bookings stored in the database."""

        BookingRepository._ensure_booking_numbers()

        customers = {
            customer.entity_id: customer
            for customer in CustomerRepository.find_all()
        }

        cleaners = {
            cleaner.entity_id: cleaner
            for cleaner in CleanerRepository.find_all()
        }

        services = {
            service.entity_id: service
            for service in ServiceRepository.find_all()
        }

        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                booking_id,
                booking_number,
                customer_id,
                cleaner_id,
                service_id,
                booking_date,
                end_time,
                address,
                total_amount,
                notes,
                status,
                created_at
            FROM bookings
            ORDER BY booking_date DESC
            """
        )

        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        bookings: list[Booking] = []

        for row in rows:
            customer = customers.get(row["customer_id"])
            cleaner = cleaners.get(row["cleaner_id"])
            service = services.get(row["service_id"])

            if customer is None or cleaner is None or service is None:
                continue

            end_time = None

            if row["end_time"]:
                end_time = datetime.fromisoformat(row["end_time"])

            booking = Booking(
                entity_id=row["booking_id"],
                created_at=datetime.fromisoformat(row["created_at"]),
                customer=customer,
                cleaner=cleaner,
                cleaning_service=service,
                booking_date=datetime.fromisoformat(row["booking_date"]),
                end_time=end_time,
                address=row["address"] or "",
                total_amount=row["total_amount"] or 0.0,
                notes=row["notes"] or "",
                status=row["status"],
                booking_number=row["booking_number"] or "",
            )

            bookings.append(booking)

        return bookings

    @staticmethod
    def delete(entity_id: str) -> None:
        """Delete a booking with its related invoices and payments."""

        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                DELETE payments
                FROM payments
                INNER JOIN invoices ON payments.invoice_id = invoices.invoice_id
                WHERE invoices.booking_id = %s
                """,
                (entity_id,),
            )

            cursor.execute(
                "DELETE FROM invoices WHERE booking_id = %s",
                (entity_id,),
            )

            cursor.execute(
                "DELETE FROM bookings WHERE booking_id = %s",
                (entity_id,),
            )

            connection.commit()

        except IntegrityError as error:
            connection.rollback()
            raise ValueError(
                "This booking could not be deleted because related records still exist."
            ) from error

        finally:
            cursor.close()
            connection.close()
