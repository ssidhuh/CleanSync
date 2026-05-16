"""Repository-style payroll calculations for cleaner weekly earnings."""

from collections import defaultdict
from datetime import datetime, time, timedelta

from src.models.cleaner_payroll import CleanerPayroll
from src.repositories.booking_repository import BookingRepository


class CleanerPayrollRepository:
    """
    Calculates cleaner payroll from completed bookings.

    Payroll is generated from booking data instead of being manually entered,
    reducing duplicated financial data and improving consistency.
    """

    CLEANER_PAY_RATE = 7.0

    @staticmethod
    def find_all() -> list[CleanerPayroll]:
        """Return weekly payroll records grouped by cleaner and week."""
        grouped_payroll: dict[tuple[str, datetime], dict[str, object]] = defaultdict(
            lambda: {
                "cleaner_name": "",
                "week_end": None,
                "completed_bookings": 0,
                "total_hours": 0.0,
            }
        )

        for booking in BookingRepository.find_all():
            if str(booking.status).lower() != "completed":
                continue

            if booking.end_time is None:
                continue

            if booking.end_time <= booking.booking_date:
                continue

            week_start_date = (
                booking.booking_date - timedelta(days=booking.booking_date.weekday())
            ).date()
            week_start = datetime.combine(week_start_date, time.min)
            week_end = week_start + timedelta(days=6, hours=23, minutes=59)

            key = (booking.cleaner.entity_id, week_start)
            duration_hours = (
                booking.end_time - booking.booking_date
            ).total_seconds() / 3600

            grouped_payroll[key]["cleaner_name"] = booking.cleaner.full_name
            grouped_payroll[key]["week_end"] = week_end
            grouped_payroll[key]["completed_bookings"] = (
                int(grouped_payroll[key]["completed_bookings"]) + 1
            )
            grouped_payroll[key]["total_hours"] = (
                float(grouped_payroll[key]["total_hours"]) + duration_hours
            )

        payroll_records: list[CleanerPayroll] = []

        for (cleaner_id, week_start), payroll_data in grouped_payroll.items():
            total_hours = round(float(payroll_data["total_hours"]), 2)
            total_earnings = round(total_hours * CleanerPayrollRepository.CLEANER_PAY_RATE, 2)
            week_end = payroll_data["week_end"]

            if not isinstance(week_end, datetime):
                continue

            payroll_records.append(
                CleanerPayroll(
                    entity_id=f"PAY-{cleaner_id[:8]}-{week_start.strftime('%Y%m%d')}",
                    created_at=datetime.now(),
                    cleaner_name=str(payroll_data["cleaner_name"]),
                    week_start=week_start,
                    week_end=week_end,
                    completed_bookings=int(payroll_data["completed_bookings"]),
                    total_hours=total_hours,
                    hourly_pay_rate=CleanerPayrollRepository.CLEANER_PAY_RATE,
                    total_earnings=total_earnings,
                    payment_status=CleanerPayrollRepository._payment_status(week_end),
                )
            )

        return sorted(
            payroll_records,
            key=lambda payroll: (payroll.week_start, payroll.cleaner_name),
            reverse=True,
        )

    @staticmethod
    def _payment_status(week_end: datetime) -> str:
        """
        Mark finished weekly payroll as paid automatically on Mondays.

        The previous completed work week becomes paid when the application
        is opened on a Monday. Otherwise it remains pending.
        """
        today = datetime.now().date()

        if today.weekday() == 0 and week_end.date() < today:
            return "Paid"

        return "Pending"