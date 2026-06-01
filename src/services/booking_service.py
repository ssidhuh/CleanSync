"""Business logic module for booking operations."""

from src.models.booking import Booking
from src.repositories.booking_repository import BookingRepository


class BookingService:
    """
    Coordinates booking workflows before persistence.

    The service layer keeps business decisions separate from both
    the UI layer and the database repository layer.
    """

    @staticmethod
    def create_booking(booking: Booking) -> None:
        """Validate and persist a new booking workflow."""
        BookingService.__validate_booking_for_creation(booking)
        booking.confirm_booking()
        booking.update_total_amount()

        BookingRepository.save_booking(booking)

    @staticmethod
    def update_booking(booking: Booking) -> None:
        """Keep booking updates controlled through the service layer."""
        BookingService.__validate_booking_schedule(booking)
        booking.update_total_amount()

        BookingRepository.save_booking(booking)

    @staticmethod
    def complete_booking(booking: Booking) -> None:
        """Keep completion workflow consistent before saving."""
        booking.complete_booking()
        BookingRepository.save_booking(booking)

    @staticmethod
    def cancel_booking(booking: Booking) -> None:
        """Keep cancellation workflow consistent before saving."""
        booking.cancel_booking()
        BookingRepository.save_booking(booking)

    @staticmethod
    def __validate_booking_for_creation(booking: Booking) -> None:
        """Keep creation rules away from form-specific code."""
        if not booking.customer.validate_contact_information():
            raise ValueError("Customer contact information is invalid.")

        if not booking.cleaner.is_available:
            raise ValueError("Cleaner is not available for booking.")

        BookingService.__validate_booking_schedule(booking)

    @staticmethod
    def __validate_booking_schedule(booking: Booking) -> None:
        """Keep schedule validation reusable across booking workflows."""
        if not booking.validate_schedule():
            raise ValueError("Booking end time must be after start time.")
