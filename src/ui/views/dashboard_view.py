"""Dashboard view for the CleanSync desktop application."""

from __future__ import annotations

from datetime import date

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src.repositories.booking_repository import BookingRepository
from src.repositories.cleaner_repository import CleanerRepository
from src.repositories.customer_repository import CustomerRepository
from src.repositories.invoice_repository import InvoiceRepository
from src.repositories.payment_repository import PaymentRepository
from src.ui.theme import APP_COLORS, APP_FONTS


class DashboardView(ctk.CTkFrame):
    """Dashboard page showing business statistics and recent activity."""

    ACTIVE_BOOKING_STATUSES = {
        "pending",
        "confirmed",
        "assigned",
        "in_progress",
        "in progress",
    }

    def __init__(self, parent) -> None:
        super().__init__(parent, fg_color=APP_COLORS["background"])
        self.pack(fill="both", expand=True)

        self.customers = CustomerRepository.find_all()
        self.cleaners = CleanerRepository.find_all()
        self.bookings = BookingRepository.find_all()
        self.invoices = InvoiceRepository.find_all()
        self.payments = PaymentRepository.find_all()

        self._build_page()

    def _build_page(self) -> None:
        """Build all dashboard sections."""
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=APP_COLORS["background"],
            scrollbar_button_color=APP_COLORS["border"],
            scrollbar_button_hover_color=APP_COLORS["muted_text"],
        )
        self.scroll_frame.pack(fill="both", expand=True)

        self._build_header()
        self._build_stat_cards()
        self._build_charts_section()
        self._build_bottom_section()

    def _paid_payment_total(self) -> float:
        total = 0.0

        for invoice in self.invoices:
            invoice_status = str(invoice.payment_status).strip().lower()

            if invoice_status == "paid":
                total += float(invoice.total_amount or 0)

        return total

    def _booking_status(self, booking) -> str:
        return str(getattr(booking, "status", "")).strip().lower()

    def _is_active_booking(self, booking) -> bool:
        return self._booking_status(booking) in self.ACTIVE_BOOKING_STATUSES

    def _is_cancelled_booking(self, booking) -> bool:
        return self._booking_status(booking) == "cancelled"

    def _invoice_has_cancelled_booking(self, invoice) -> bool:
        invoice_booking = getattr(invoice, "booking", None)

        if invoice_booking is not None:
            return self._is_cancelled_booking(invoice_booking)

        invoice_booking_id = getattr(invoice, "booking_id", None)

        for booking in self.bookings:
            booking_id = getattr(booking, "entity_id", None)

            if booking_id == invoice_booking_id:
                return self._is_cancelled_booking(booking)

        return False

    def _active_customer_count(self) -> int:
        active_customer_ids = set()

        for booking in self.bookings:
            if not self._is_active_booking(booking):
                continue

            booking_customer = getattr(booking, "customer", None)
            customer_id = getattr(booking_customer, "entity_id", None)

            if customer_id is None:
                customer_id = getattr(booking, "customer_id", None)

            if customer_id is None and booking_customer is not None:
                customer_id = booking_customer.full_name

            if customer_id is not None:
                active_customer_ids.add(customer_id)

        return len(active_customer_ids)

    def _unpaid_invoice_total(self) -> float:
        return sum(
            float(invoice.total_amount or 0)
            for invoice in self.invoices
            if str(invoice.payment_status).strip().lower() != "paid"
            and not self._invoice_has_cancelled_booking(invoice)
        )

    def _monthly_revenue_data(self) -> dict[str, float]:
        monthly_revenue = {
            "Jan": 0.0,
            "Feb": 0.0,
            "Mar": 0.0,
            "Apr": 0.0,
            "May": 0.0,
            "Jun": 0.0,
            "Jul": 0.0,
            "Aug": 0.0,
            "Sep": 0.0,
            "Oct": 0.0,
            "Nov": 0.0,
            "Dec": 0.0,
        }

        for invoice in self.invoices:
            invoice_status = str(invoice.payment_status).strip().lower()

            if invoice_status != "paid":
                continue

            invoice_date = getattr(invoice, "created_at", None)

            if invoice_date is None:
                continue

            month = invoice_date.strftime("%b")
            monthly_revenue[month] += float(invoice.total_amount or 0)

        return monthly_revenue

    def _cleaner_job_count(self, cleaner) -> int:
        job_count = 0

        for booking in self.bookings:
            if self._is_cancelled_booking(booking):
                continue

            booking_cleaner = getattr(booking, "cleaner", None)

            if booking_cleaner is cleaner:
                job_count += 1
                continue

            if getattr(booking_cleaner, "entity_id", None) == cleaner.entity_id:
                job_count += 1

        return job_count

    def _team_performance_data(self) -> list[dict]:
        performance = []

        for cleaner in self.cleaners:
            if not cleaner.is_active:
                continue

            performance.append(
                {
                    "name": cleaner.full_name,
                    "initial": cleaner.first_name[:1].upper(),
                    "jobs": self._cleaner_job_count(cleaner),
                    "rating": cleaner.rating,
                }
            )

        return sorted(
            performance,
            key=lambda item: (item["jobs"], item["rating"]),
            reverse=True,
        )[:4]

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(26, 18))

        ctk.CTkLabel(
            header,
            text="Dashboard",
            text_color=APP_COLORS["foreground"],
            font=("Inter", 28, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Overview of your cleaning business",
            text_color=APP_COLORS["muted_text"],
            font=APP_FONTS["body"],
        ).pack(anchor="w", pady=(4, 0))

    def _build_stat_cards(self) -> None:
        cards = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        cards.pack(fill="x", padx=30, pady=(0, 22))

        total_revenue = self._paid_payment_total()
        active_customers = self._active_customer_count()

        free_cleaners = len(
            [cleaner for cleaner in self.cleaners if cleaner.is_available]
        )
        on_job_cleaners = len(self.cleaners) - free_cleaners

        active_bookings = len(
            [booking for booking in self.bookings if self._is_active_booking(booking)]
        )

        today_bookings = len(
            [
                booking
                for booking in self.bookings
                if booking.booking_date.date() == date.today()
            ]
        )

        unpaid_total = self._unpaid_invoice_total()

        stats = [
            ("Total Customers", len(self.customers), "👤", f"{active_customers} active"),
            (
                "Active Cleaners",
                free_cleaners,
                "🧢",
                f"{on_job_cleaners} on job · {free_cleaners} free",
            ),
            ("Active Bookings", active_bookings, "🗓️", f"{today_bookings} today"),
            (
                "Total Revenue",
                f"€{total_revenue:,.2f}",
                "€",
                f"€{unpaid_total:,.2f} unpaid",
            ),
        ]

        for index, (title, value, icon, subtitle) in enumerate(stats):
            cards.grid_columnconfigure(index, weight=1)
            self._stat_card(cards, title, value, icon, subtitle, index)

    def _stat_card(
        self,
        parent,
        title: str,
        value,
        icon: str,
        subtitle: str,
        column: int,
    ) -> None:
        card = ctk.CTkFrame(
            parent,
            fg_color=APP_COLORS["card"],
            corner_radius=16,
            border_width=1,
            border_color=APP_COLORS["border"],
        )
        card.grid(row=0, column=column, sticky="ew", padx=8)

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=18, pady=(16, 4))

        ctk.CTkLabel(
            top_row,
            text=title,
            text_color=APP_COLORS["muted_text"],
            font=APP_FONTS["small"],
        ).pack(side="left")

        ctk.CTkLabel(top_row, text=icon, font=("Inter", 22)).pack(side="right")

        ctk.CTkLabel(
            card,
            text=str(value),
            text_color=APP_COLORS["foreground"],
            font=("Inter", 27, "bold"),
        ).pack(anchor="w", padx=18)

        ctk.CTkLabel(
            card,
            text=subtitle,
            text_color=APP_COLORS["primary"],
            font=("Inter", 12, "bold"),
        ).pack(anchor="w", padx=18, pady=(2, 14))

    def _build_charts_section(self) -> None:
        section = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        section.pack(fill="x", padx=30, pady=(0, 22))
        section.grid_columnconfigure(0, weight=2)
        section.grid_columnconfigure(1, weight=1)

        revenue_card = self._basic_card(section, "Revenue Overview", show_arrow=True)
        revenue_card.grid(row=0, column=0, sticky="nsew", padx=(0, 11))
        self._build_revenue_chart(revenue_card)

        status_card = self._basic_card(section, "Booking Status")
        status_card.grid(row=0, column=1, sticky="nsew", padx=(11, 0))
        self._build_status_chart(status_card)

    def _build_revenue_chart(self, parent) -> None:
        monthly_revenue = self._monthly_revenue_data()

        labels = list(monthly_revenue.keys())
        values = list(monthly_revenue.values())

        figure = Figure(figsize=(6.2, 2.8), dpi=90)
        figure.patch.set_facecolor(APP_COLORS["card"])
        axis = figure.add_subplot(111)
        axis.set_facecolor(APP_COLORS["card"])

        bars = axis.bar(
            labels,
            values,
            color="#0ea5e9",
            edgecolor="#0b8fc9",
            linewidth=1,
        )

        axis.set_ylabel("Revenue (€)")
        axis.tick_params(axis="x", labelsize=8)
        axis.tick_params(axis="y", labelsize=8)

        max_value = max(values) if values else 0
        axis.set_ylim(0, max(max_value * 1.25, 100))

        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.spines["left"].set_color("#dbe3ea")
        axis.spines["bottom"].set_color("#dbe3ea")
        axis.grid(axis="y", alpha=0.22)

        annotation = axis.annotate(
            "",
            xy=(0, 0),
            xytext=(0, 12),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            color=APP_COLORS["foreground"],
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#dbe3ea"),
        )
        annotation.set_visible(False)

        def on_motion(event) -> None:
            visible = False

            if event.inaxes == axis:
                for bar, label, value in zip(bars, labels, values):
                    contains, _info = bar.contains(event)

                    if contains:
                        annotation.xy = (
                            bar.get_x() + bar.get_width() / 2,
                            bar.get_height(),
                        )
                        annotation.set_text(f"{label}: €{value:.2f}")
                        annotation.set_visible(True)
                        visible = True
                        break

            if not visible:
                annotation.set_visible(False)

            canvas.draw_idle()

        figure.tight_layout()

        canvas = FigureCanvasTkAgg(figure, master=parent)
        canvas.draw()
        canvas.mpl_connect("motion_notify_event", on_motion)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=(4, 14))

    def _build_status_chart(self, parent) -> None:
        status_counts: dict[str, int] = {}

        for booking in self.bookings:
            status = str(booking.status).title()
            status_counts[status] = status_counts.get(status, 0) + 1

        if not status_counts:
            ctk.CTkLabel(
                parent,
                text="No bookings yet",
                text_color=APP_COLORS["muted_text"],
                font=APP_FONTS["body"],
            ).pack(pady=60)
            return

        labels = list(status_counts.keys())
        values = list(status_counts.values())

        status_colours = {
            "Pending": "#f59e0b",
            "Confirmed": "#0ea5e9",
            "Assigned": "#0ea5e9",
            "In Progress": "#8b5cf6",
            "Completed": "#10b981",
            "Cancelled": "#ef4444",
        }

        colours = [status_colours.get(label, "#94a3b8") for label in labels]

        figure = Figure(figsize=(3.2, 2.8), dpi=90)
        figure.patch.set_facecolor(APP_COLORS["card"])
        axis = figure.add_subplot(111)
        axis.set_facecolor(APP_COLORS["card"])

        wedges, _texts, autotexts = axis.pie(
            values,
            labels=labels,
            autopct="%1.0f%%",
            startangle=90,
            colors=colours,
            wedgeprops={"linewidth": 1, "edgecolor": "white"},
            textprops={"fontsize": 8, "color": APP_COLORS["foreground"]},
        )

        for text in autotexts:
            text.set_color("white")
            text.set_fontsize(8)
            text.set_fontweight("bold")

        axis.axis("equal")

        annotation = axis.annotate(
            "",
            xy=(0, 0),
            xytext=(0, 12),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            color=APP_COLORS["foreground"],
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#dbe3ea"),
        )
        annotation.set_visible(False)

        def on_motion(event) -> None:
            visible = False

            if event.inaxes == axis:
                for wedge, label, value in zip(wedges, labels, values):
                    contains, _info = wedge.contains(event)

                    if contains:
                        annotation.xy = (event.xdata, event.ydata)
                        annotation.set_text(f"{label}: {value}")
                        annotation.set_visible(True)
                        visible = True
                        break

            if not visible:
                annotation.set_visible(False)

            canvas.draw_idle()

        figure.tight_layout()

        canvas = FigureCanvasTkAgg(figure, master=parent)
        canvas.draw()
        canvas.mpl_connect("motion_notify_event", on_motion)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=(4, 14))

    def _build_bottom_section(self) -> None:
        section = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        section.pack(fill="both", expand=True, padx=30, pady=(0, 28))
        section.grid_columnconfigure(0, weight=2)
        section.grid_columnconfigure(1, weight=1)

        recent_card = self._basic_card(section, "Recent Bookings")
        recent_card.grid(row=0, column=0, sticky="nsew", padx=(0, 11))
        self._build_recent_bookings(recent_card)

        team_card = self._basic_card(section, "⭐ Team Performance")
        team_card.grid(row=0, column=1, sticky="nsew", padx=(11, 0))
        self._build_team_performance(team_card)

    def _build_recent_bookings(self, card) -> None:
        recent_bookings = self.bookings[-8:]

        if not recent_bookings:
            ctk.CTkLabel(
                card,
                text="No bookings yet. Create a booking to see recent activity here.",
                text_color=APP_COLORS["muted_text"],
                font=APP_FONTS["body"],
            ).pack(pady=44)
            return

        for booking in reversed(recent_bookings):
            self._booking_row(card, booking)

    def _build_team_performance(self, parent) -> None:
        performance_data = self._team_performance_data()

        if not performance_data:
            ctk.CTkLabel(
                parent,
                text="No cleaner performance data yet.",
                text_color=APP_COLORS["muted_text"],
                font=APP_FONTS["body"],
            ).pack(pady=44)
            return

        max_jobs = max(item["jobs"] for item in performance_data) or 1

        for item in performance_data:
            self._team_performance_row(parent, item, max_jobs)

    def _team_performance_row(self, parent, item: dict, max_jobs: int) -> None:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=8)

        ctk.CTkLabel(
            row,
            text=item["initial"],
            width=28,
            height=28,
            fg_color="#dff4fb",
            text_color=APP_COLORS["primary"],
            corner_radius=14,
            font=("Inter", 11, "bold"),
        ).pack(side="left", padx=(0, 10))

        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)

        top = ctk.CTkFrame(info, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(
            top,
            text=item["name"],
            text_color=APP_COLORS["foreground"],
            font=("Inter", 12, "bold"),
        ).pack(side="left")

        ctk.CTkLabel(
            top,
            text=f"{item['jobs']} jobs",
            text_color=APP_COLORS["muted_text"],
            font=APP_FONTS["small"],
        ).pack(side="right", padx=(0, 8))

        progress = ctk.CTkProgressBar(
            info,
            height=6,
            progress_color=APP_COLORS["accent"],
            fg_color=APP_COLORS["muted"],
        )
        progress.pack(fill="x", pady=(4, 0))
        progress.set(item["jobs"] / max_jobs)

        ctk.CTkLabel(
            row,
            text=f"⭐ {item['rating']:.1f}",
            text_color=APP_COLORS["foreground"],
            font=("Inter", 11, "bold"),
        ).pack(side="right", padx=(8, 0))

    def _booking_row(self, parent, booking) -> None:
        row = ctk.CTkFrame(parent, fg_color=APP_COLORS["muted"], corner_radius=14)
        row.pack(fill="x", padx=18, pady=7)

        initials = "".join(
            part[0].upper()
            for part in booking.customer.full_name.split()
            if part
        )[:2]

        ctk.CTkLabel(
            row,
            text=initials,
            width=42,
            height=42,
            fg_color=APP_COLORS["primary"],
            text_color=APP_COLORS["primary_text"],
            corner_radius=21,
            font=("Inter", 13, "bold"),
        ).pack(side="left", padx=(14, 12), pady=10)

        details = ctk.CTkFrame(row, fg_color="transparent")
        details.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            details,
            text=booking.customer.full_name,
            text_color=APP_COLORS["foreground"],
            font=("Inter", 13, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            details,
            text=(
                f"{booking.cleaning_service.service_name} • "
                f"{booking.booking_date.strftime('%d %b %Y')}"
            ),
            text_color=APP_COLORS["muted_text"],
            font=APP_FONTS["small"],
        ).pack(anchor="w", pady=(2, 0))

        right = ctk.CTkFrame(row, fg_color="transparent")
        right.pack(side="right", padx=14)

        amount = booking.total_amount or booking.cleaning_service.calculate_service_cost()

        ctk.CTkLabel(
            right,
            text=f"€{amount:.2f}",
            text_color=APP_COLORS["foreground"],
            font=("Inter", 13, "bold"),
        ).pack(anchor="e")

        ctk.CTkLabel(
            right,
            text=str(booking.status).title(),
            text_color=APP_COLORS["primary"],
            font=APP_FONTS["small"],
        ).pack(anchor="e", pady=(2, 0))

    def _basic_card(self, parent, title: str, show_arrow: bool = False) -> ctk.CTkFrame:
        outer = ctk.CTkFrame(
            parent,
            fg_color=APP_COLORS["card"],
            corner_radius=16,
            border_width=1,
            border_color=APP_COLORS["border"],
        )

        title_row = ctk.CTkFrame(outer, fg_color="transparent")
        title_row.pack(fill="x", padx=18, pady=(16, 8))

        ctk.CTkLabel(
            title_row,
            text=title,
            text_color=APP_COLORS["foreground"],
            font=APP_FONTS["subheading"],
        ).pack(side="left")

        if show_arrow:
            ctk.CTkLabel(
                title_row,
                text="↗",
                text_color=APP_COLORS["primary"],
                font=("Inter", 16, "bold"),
            ).pack(side="left", padx=(8, 0))

        return outer
