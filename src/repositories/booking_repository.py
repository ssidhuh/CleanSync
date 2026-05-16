"""Repository module for booking persistence operations."""

from datetime import datetime

from src.database.database_manager import DatabaseManager
from src.models.booking import Booking
from src.models.cleaner import Cleaner
from src.models.customer import Customer
from src.models.service import CleaningService
from src.repositories.repository_interface import RepositoryInterface


class BookingRepository(RepositoryInterface[Booking]):
    """Handles booking-related database operations."""

    @staticmethod
    def save(entity: Booking) -> None:
        """Persist a booking using the common repository interface."""
        BookingRepository.save_booking(entity)

    @staticmethod
    def save_booking(booking: Booking) -> None:
        """Persist booking information to the database."""
        BookingRepository.save_related_entities(booking)

        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO bookings (
                booking_id,
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                booking.entity_id,
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
        connection.close()

    @staticmethod
    def find_all() -> list[Booking]:
        """Return bookings with their related customer, cleaner, and service data."""
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                b.booking_id,
                b.booking_date,
                b.end_time,
                b.address AS booking_address,
                b.total_amount,
                b.notes,
                b.status,
                b.created_at AS booking_created_at,

                c.customer_id,
                c.first_name AS customer_first_name,
                c.last_name AS customer_last_name,
                c.phone_number AS customer_phone_number,
                c.email AS customer_email,
                c.address,
                c.created_at AS customer_created_at,

                cl.cleaner_id,
                cl.first_name AS cleaner_first_name,
                cl.last_name AS cleaner_last_name,
                cl.email AS cleaner_email,
                cl.phone_number AS cleaner_phone_number,
                cl.hourly_rate,
                cl.rating,
                cl.status AS cleaner_status,
                cl.specializations,
                cl.service_area,
                cl.created_at AS cleaner_created_at,

                s.service_id,
                s.service_name,
                s.description,
                s.duration_hours,
                s.base_price,
                s.created_at AS service_created_at
            FROM bookings b
            JOIN customers c ON b.customer_id = c.customer_id
            JOIN cleaners cl ON b.cleaner_id = cl.cleaner_id
            JOIN cleaning_services s ON b.service_id = s.service_id
            ORDER BY b.booking_date DESC
            """
        )

        rows = cursor.fetchall()
        connection.close()

        bookings: list[Booking] = []

        for row in rows:
            customer = Customer(
                entity_id=row["customer_id"],
                created_at=datetime.fromisoformat(row["customer_created_at"]),
                first_name=row["customer_first_name"],
                last_name=row["customer_last_name"],
                phone_number=row["customer_phone_number"],
                email=row["customer_email"],
                address=row["address"],
            )

            cleaner = Cleaner(
                entity_id=row["cleaner_id"],
                created_at=datetime.fromisoformat(row["cleaner_created_at"]),
                first_name=row["cleaner_first_name"],
                last_name=row["cleaner_last_name"],
                email=row["cleaner_email"],
                phone_number=row["cleaner_phone_number"],
                hourly_rate=row["hourly_rate"],
                rating=row["rating"],
                status=row["cleaner_status"],
                specializations=row["specializations"],
                service_area=row["service_area"],
            )

            service = CleaningService(
                entity_id=row["service_id"],
                created_at=datetime.fromisoformat(row["service_created_at"]),
                service_name=row["service_name"],
                description=row["description"],
                duration_hours=row["duration_hours"],
                base_price=row["base_price"],
            )

            end_time = None
            if row["end_time"]:
                end_time = datetime.fromisoformat(row["end_time"])

            bookings.append(
                Booking(
                    entity_id=row["booking_id"],
                    created_at=datetime.fromisoformat(row["booking_created_at"]),
                    customer=customer,
                    cleaner=cleaner,
                    cleaning_service=service,
                    booking_date=datetime.fromisoformat(row["booking_date"]),
                    end_time=end_time,
                    address=row["booking_address"] or "",
                    total_amount=row["total_amount"] or 0.0,
                    notes=row["notes"] or "",
                    status=row["status"],
                )
            )

        return bookings

    @staticmethod
    def find_by_status(status: str | None = None) -> list[Booking]:
        """
        Return bookings using Python-style method overloading.

        If no status is provided, all bookings are returned.
        If a status is provided, only bookings matching that
        status are returned.
        """
        bookings = BookingRepository.find_all()

        if status is None:
            return bookings

        return [
            booking
            for booking in bookings
            if booking.status.lower() == status.lower()
        ]

    @staticmethod
    def delete(entity_id: str) -> None:
        """
        Delete a booking and its dependent invoice/payment records.

        Payments and invoices are removed first because SQLite prevents
        deleting a booking while dependent records still reference it.
        """
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                SELECT invoice_id
                FROM invoices
                WHERE booking_id = ?
                """,
                (entity_id,),
            )
            invoice_ids = [row["invoice_id"] for row in cursor.fetchall()]

            for invoice_id in invoice_ids:
                cursor.execute(
                    """
                    DELETE FROM payments
                    WHERE invoice_id = ?
                    """,
                    (invoice_id,),
                )

            cursor.execute(
                """
                DELETE FROM invoices
                WHERE booking_id = ?
                """,
                (entity_id,),
            )

            cursor.execute(
                """
                DELETE FROM bookings
                WHERE booking_id = ?
                """,
                (entity_id,),
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    @staticmethod
    def save_related_entities(booking: Booking) -> None:
        """Persist booking dependencies before the booking itself."""
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
                booking.customer.entity_id,
                booking.customer.first_name,
                booking.customer.last_name,
                booking.customer.phone_number,
                booking.customer.email,
                booking.customer.address,
                booking.customer.created_at.isoformat(),
            ),
        )

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
                booking.cleaner.entity_id,
                booking.cleaner.first_name,
                booking.cleaner.last_name,
                booking.cleaner.email,
                booking.cleaner.phone_number,
                booking.cleaner.hourly_rate,
                booking.cleaner.rating,
                booking.cleaner.status,
                booking.cleaner.specializations,
                booking.cleaner.service_area,
                booking.cleaner.created_at.isoformat(),
            ),
        )

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
                booking.cleaning_service.entity_id,
                booking.cleaning_service.service_name,
                booking.cleaning_service.description,
                booking.cleaning_service.duration_hours,
                booking.cleaning_service.base_price,
                booking.cleaning_service.created_at.isoformat(),
            ),
        )

        connection.commit()
        connection.close()
