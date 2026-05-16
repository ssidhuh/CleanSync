"""Repository tests for CleanSync database persistence."""

from datetime import datetime

import pytest

from src.database.database_manager import DatabaseManager
from src.models.base_entity import BaseEntity
from src.models.booking import Booking
from src.models.cleaner import Cleaner
from src.models.customer import Customer
from src.models.invoice import Invoice
from src.models.service import CleaningService
from src.repositories.booking_repository import BookingRepository
from src.repositories.cleaner_repository import CleanerRepository
from src.repositories.customer_repository import CustomerRepository
from src.repositories.invoice_repository import InvoiceRepository
from src.repositories.service_repository import ServiceRepository
from src.services.booking_service import BookingService


@pytest.fixture()
def temporary_database(tmp_path, monkeypatch):
    """Create an isolated SQLite database for each test."""
    database_path = tmp_path / "cleansync_test.db"
    monkeypatch.setattr(DatabaseManager, "DATABASE_PATH", database_path)
    DatabaseManager.initialise_database()
    return database_path


def build_customer() -> Customer:
    """Create a valid customer for persistence tests."""
    return Customer(
        entity_id=BaseEntity.generate_id(),
        created_at=datetime.now(),
        first_name="Ava",
        last_name="Stone",
        phone_number="22114455",
        email="ava@example.com",
        address="12 Clean Street",
    )


def build_booking() -> Booking:
    """Create a valid booking with related entities."""
    customer = build_customer()
    cleaner = Cleaner(
        entity_id=BaseEntity.generate_id(),
        created_at=datetime.now(),
        first_name="Mila",
        last_name="Reed",
        phone_number="22998877",
        service_area="Riga Centre",
        hourly_rate=18.5,
    )
    cleaning_service = CleaningService(
        entity_id=BaseEntity.generate_id(),
        created_at=datetime.now(),
        service_name="Standard Home Cleaning",
        description="General cleaning for an apartment.",
        duration_hours=2.5,
        base_price=55.0,
    )

    return Booking(
        entity_id=BaseEntity.generate_id(),
        created_at=datetime.now(),
        customer=customer,
        cleaner=cleaner,
        cleaning_service=cleaning_service,
        booking_date=datetime(2026, 5, 20, 10, 30),
        status="Pending",
    )


def build_cleaner() -> Cleaner:
    """Create a valid cleaner for persistence tests."""
    return Cleaner(
        entity_id=BaseEntity.generate_id(),
        created_at=datetime.now(),
        first_name="Nora",
        last_name="Field",
        phone_number="22001144",
        service_area="Riga",
        hourly_rate=20.0,
    )


def build_service() -> CleaningService:
    """Create a valid cleaning service for persistence tests."""
    return CleaningService(
        entity_id=BaseEntity.generate_id(),
        created_at=datetime.now(),
        service_name="Deep Cleaning",
        description="Detailed home cleaning.",
        duration_hours=4,
        base_price=95,
    )


def test_customer_can_be_saved_and_loaded(temporary_database):
    """Customers should be saved and reconstructed from SQLite."""
    customer = build_customer()

    CustomerRepository.save_customer(customer)

    stored_customers = CustomerRepository.find_all()

    assert temporary_database.exists()
    assert len(stored_customers) == 1
    assert stored_customers[0].full_name == "Ava Stone"
    assert stored_customers[0].email == "ava@example.com"


def test_customer_can_be_deleted(temporary_database):
    """Deleting a customer should remove it from the database."""
    customer = build_customer()
    CustomerRepository.save_customer(customer)

    CustomerRepository.delete(customer.entity_id)

    assert CustomerRepository.find_all() == []


def test_booking_repository_preserves_class_relationships(temporary_database):
    """Bookings should be saved with their customer, cleaner, and service."""
    booking = build_booking()

    BookingRepository.save_booking(booking)

    stored_bookings = BookingRepository.find_all()

    assert len(stored_bookings) == 1
    assert stored_bookings[0].customer.full_name == "Ava Stone"
    assert stored_bookings[0].cleaner.full_name == "Mila Reed"
    assert stored_bookings[0].cleaning_service.service_name == (
        "Standard Home Cleaning"
    )


def test_cleaner_can_be_saved_and_loaded(temporary_database):
    """Cleaners should be saved with availability and rate information."""
    cleaner = build_cleaner()

    CleanerRepository.save_cleaner(cleaner)

    stored_cleaners = CleanerRepository.find_all()

    assert len(stored_cleaners) == 1
    assert stored_cleaners[0].full_name == "Nora Field"
    assert stored_cleaners[0].hourly_rate == 20.0
    assert stored_cleaners[0].is_available is True


def test_service_can_be_saved_and_loaded(temporary_database):
    """Cleaning services should be saved with price and duration."""
    cleaning_service = build_service()

    ServiceRepository.save_service(cleaning_service)

    stored_services = ServiceRepository.find_all()

    assert len(stored_services) == 1
    assert stored_services[0].service_name == "Deep Cleaning"
    assert stored_services[0].calculate_service_cost() == 95


def test_booking_service_rejects_unavailable_cleaner(temporary_database):
    """Booking validation should reject cleaners already marked unavailable."""
    booking = build_booking()
    booking.cleaner.mark_unavailable()

    with pytest.raises(ValueError, match="Cleaner is not available"):
        BookingService.create_booking(booking)


def test_invoice_can_be_generated_for_booking(temporary_database):
    """Invoices should store amount, status, and booking relationship."""
    booking = build_booking()
    BookingRepository.save_booking(booking)
    invoice = Invoice(
        entity_id=BaseEntity.generate_id(),
        created_at=datetime.now(),
        booking=booking,
        total_amount=booking.cleaning_service.calculate_service_cost(),
        payment_status="Unpaid",
    )

    InvoiceRepository.save_invoice(invoice)

    stored_invoices = InvoiceRepository.find_all()

    assert len(stored_invoices) == 1
    assert stored_invoices[0].payment_status == "Unpaid"
    assert stored_invoices[0].booking.customer.full_name == "Ava Stone"
