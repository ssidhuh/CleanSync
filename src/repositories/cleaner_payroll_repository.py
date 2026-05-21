"""Repository-style payroll calculations for cleaner weekly earnings."""

from collections import defaultdict
from datetime import datetime, time, timedelta

from src.models.cleaner_payroll import CleanerPayroll
from src.repositories.booking_repository import BookingRepository


class CleanerPayrollRepository:
    """
    Calculates cleaner payroll from completed bookings.

    Payroll is generated from bookings to avoid storing duplicate
    financial records that could become inconsistent with booking data.
    """

    CLEANER_PAY_RATE = 7.0
    PAID_STATUS = "Paid"
    PENDING_STATUS = "Pending"

    @classmethod
    def find_all(cls) -> list[CleanerPayroll]:
        """Build weekly payroll objects from completed booking records."""
        grouped_payroll = cls._group_completed_bookings()
        payroll_records = [
            cls._create_payroll_record(cleaner_id, week_start, payroll_data)
            for (cleaner_id, week_start), payroll_data in grouped_payroll.items()
        ]

        return sorted(
            payroll_records,
            key=lambda payroll: (payroll.week_start, payroll.cleaner_name),
            reverse=True,
        )

    @classmethod
    def _group_completed_bookings(cls) -> dict[tuple[str, datetime], dict[str, object]]:
        """Keep grouping rules separate so payroll generation stays testable."""
        grouped_payroll: dict[tuple[str, datetime], dict[str, object]] = defaultdict(
            cls._empty_payroll_group
        )

        for booking in BookingRepository.find_all():
            if not cls._is_payroll_eligible(booking):
                continue

            week_start = cls._week_start_for(booking.booking_date)
            week_end = cls._week_end_for(week_start)
            key = (booking.cleaner.entity_id, week_start)

            grouped_payroll[key]["cleaner_name"] = booking.cleaner.full_name
            grouped_payroll[key]["week_end"] = week_end
            grouped_payroll[key]["completed_bookings"] = (
                int(grouped_payroll[key]["completed_bookings"]) + 1
            )
            grouped_payroll[key]["total_hours"] = (
                float(grouped_payroll[key]["total_hours"]) + booking.duration_hours
            )

        return grouped_payroll

    @staticmethod
    def _empty_payroll_group() -> dict[str, object]:
        """Use one default structure to avoid repeated payroll setup logic."""
        return {
            "cleaner_name": "",
            "week_end": None,
            "completed_bookings": 0,
            "total_hours": 0.0,
        }

    @staticmethod
    def _is_payroll_eligible(booking) -> bool:
        """Keep payroll rules independent from the payroll view."""
        return (
            str(booking.status).lower() == "completed"
            and booking.end_time is not None
            and booking.end_time > booking.booking_date
        )

    @staticmethod
    def _week_start_for(booking_date: datetime) -> datetime:
        """Centralise week-boundary rules for payroll consistency."""
        week_start_date = (
            booking_date - timedelta(days=booking_date.weekday())
        ).date()

        return datetime.combine(week_start_date, time.min)

    @staticmethod
    def _week_end_for(week_start: datetime) -> datetime:
        """Use one week-ending calculation for all payroll records."""
        return week_start + timedelta(days=6, hours=23, minutes=59)

    @classmethod
    def _create_payroll_record(
        cls,
        cleaner_id: str,
        week_start: datetime,
        payroll_data: dict[str, object],
    ) -> CleanerPayroll:
        """Encapsulate payroll object creation inside the repository."""
        week_end = payroll_data["week_end"]

        if not isinstance(week_end, datetime):
            raise ValueError("Payroll week end date is required.")

        total_hours = round(float(payroll_data["total_hours"]), 2)
        total_earnings = round(total_hours * cls.CLEANER_PAY_RATE, 2)

        return CleanerPayroll(
            entity_id=f"PAY-{cleaner_id[:8]}-{week_start.strftime('%Y%m%d')}",
            created_at=datetime.now(),
            cleaner_name=str(payroll_data["cleaner_name"]),
            week_start=week_start,
            week_end=week_end,
            completed_bookings=int(payroll_data["completed_bookings"]),
            total_hours=total_hours,
            hourly_pay_rate=cls.CLEANER_PAY_RATE,
            total_earnings=total_earnings,
            payment_status=cls._payment_status(week_end),
        )

    @classmethod
    def _payment_status(cls, week_end: datetime) -> str:
        """Keep automatic payroll status rules in one place."""
        today = datetime.now().date()

        if today.weekday() == 0 and week_end.date() < today:
            return cls.PAID_STATUS

        return cls.PENDING_STATUS