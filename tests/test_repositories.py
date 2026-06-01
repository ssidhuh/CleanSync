"""Unit tests for CleanSync entity and service behaviour."""

from datetime import datetime, timedelta

import pytest

from src.models.base_entity import BaseEntity
from src.models.booking import Booking
from src.models.cleaner import Cleaner
from src.models.customer import Customer
from src.models.invoice import Invoice
from src.models.payment import Payment
from src.models.service import CleaningService


def build_customer() -> Customer:
    """Build a reusable customer object for model tests."""
    return Customer(
        entity_id=BaseEntity.generate_id(),
        created_at=datetime.now(),
        first_name="Ava",
        last_name="Stone",
        phone_number="+37122114455",
        email="ava@example.com",
        address="12 Clean Street",
    )


def build_cleaner() -> Cleaner:
    """Build a reusable cleaner object for model tests."""
    return Cleaner(
        entity_id=BaseEntity.generate_id(),
        created_at=datetime.now(),
        first_name="Mila",
        last_name="Reed",
        email="mila@cleansync.com",
        phone_number="+37122998877",
        hourly_rate=18.5,
        rating=4.8,
        status="Available",
        specializations="Standard Home Cleaning, Deep Cleaning",
        service_area="Riga Centre",
    )


def build_service() -> CleaningService:
    """Build a reusable cleaning service object for model tests."""
    return CleaningService(
        entity_id=BaseEntity.generate_id(),
        created_at=datetime.now(),
        service_name="Standard Home Cleaning",
        description="General cleaning for an apartment.",
        duration_hours=2.5,
        base_price=55.0,
        category="Residential",
    )


def build_booking() -> Booking:
    """Build a reusable booking object with related entities."""
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)

    return Booking(
        entity_id=BaseEntity.generate_id(),
        created_at=datetime.now(),
        customer=build_customer(),
        cleaner=build_cleaner(),
        cleaning_service=build_service(),
        booking_date=start_time,
        end_time=end_time,
        address="12 Clean Street",
        total_amount=37.0,
        notes="Test booking",
        status="Pending",
        booking_number="BOOK-TEST",
    )


def test_customer_full_name_and_contact_validation():
    customer = build_customer()

    assert customer.full_name == "Ava Stone"
    assert customer.validate_contact_information() is True
    assert customer.is_active is True


def test_cleaner_availability_and_service_matching():
    cleaner = build_cleaner()

    assert cleaner.is_available is True
    assert cleaner.offers_service("Standard Home Cleaning") is True

    cleaner.mark_unavailable()

    assert cleaner.status == "On Job"
    assert cleaner.is_available is False


def test_service_validation_and_price_calculation():
    service = build_service()

    assert service.validate_service_details() is True
    assert service.calculate_service_cost() == 55.0
    assert service.hourly_equivalent_price == 22.0


def test_booking_schedule_and_total_calculation():
    booking = build_booking()

    assert booking.validate_schedule() is True
    assert booking.duration_hours == 2.0
    assert booking.calculate_total_amount() == 37.0


def test_booking_workflow_methods_update_state():
    booking = build_booking()

    booking.confirm_booking()
    assert booking.status == "Confirmed"
    assert booking.cleaner.status == "On Job"

    booking.complete_booking()
    assert booking.status == "Completed"
    assert booking.cleaner.status == "Available"


def test_invoice_financial_calculations_and_payment_state():
    booking = build_booking()

    invoice = Invoice(
        entity_id=BaseEntity.generate_id(),
        created_at=datetime.now(),
        booking=booking,
        total_amount=0.0,
        payment_status="draft",
        invoice_number="INV-TEST",
        quantity=2,
        unit_price=20.0,
        tax_rate=21.0,
    )

    invoice.refresh_total_amount()

    assert invoice.subtotal == 40.0
    assert invoice.tax_amount == 8.4
    assert invoice.total_amount == 48.4

    invoice.mark_as_paid()
    assert invoice.is_paid is True


def test_payment_workflow_updates_invoice_status():
    booking = build_booking()

    invoice = Invoice(
        entity_id=BaseEntity.generate_id(),
        created_at=datetime.now(),
        booking=booking,
        total_amount=55.0,
        payment_status="draft",
        invoice_number="INV-TEST",
    )

    payment = Payment(
        entity_id=BaseEntity.generate_id(),
        created_at=datetime.now(),
        invoice=invoice,
        amount=55.0,
        payment_date=datetime.now(),
        method="Card",
        reference_number="PAY-TEST",
        status="Pending",
    )

    payment.mark_as_completed()

    assert payment.is_completed is True
    assert invoice.is_paid is True


def test_invalid_cleaner_rate_is_rejected():
    cleaner = build_cleaner()

    with pytest.raises(ValueError, match="Hourly rate must be greater than zero"):
        cleaner.update_hourly_rate(0)
