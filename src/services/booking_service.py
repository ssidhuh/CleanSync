"""Business logic module for booking operations."""

from src.models.booking import Booking
from src.repositories.booking_repository import BookingRepository


class BookingService:
    """
    Coordinates booking workflows and validation logic.

    Service classes centralise business rules so that
    repositories remain focused only on persistence.
    """

    @staticmethod
    def create_booking(booking: Booking) -> None:
        """
        Process and persist a booking request.

        Args:
            booking (Booking): Booking instance being processed.

        Raises:
            ValueError: Raised when booking details are invalid.
        """
        if not booking.customer.validate_contact_information():
            raise ValueError("Customer contact information is invalid.")

        if not booking.cleaner.is_available:
            raise ValueError("Cleaner is not available for booking.")

        booking.confirm_booking()

        BookingRepository.save_booking(booking)
