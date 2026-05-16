"""Dashboard view for the CleanSync desktop application."""

from __future__ import annotations

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
        self._build_recent_bookings()

    def _paid_payment_total(self) -> float:
        total = 0.0

        for payment in self.payments:
            status = str(
                getattr(payment, "status", getattr(payment, "payment_status", ""))
            ).lower()

            if status in {"completed", "paid"}:
                total += float(getattr(payment, "amount", 0) or 0)

        if total > 0:
            return total

        for invoice in self.invoices:
            total += float(getattr(invoice, "total_amount", 0) or 0)

        if total > 0:
            return total

        for booking in self.bookings:
            total += float(
                getattr(booking, "total_amount", 0)
                or getattr(booking.cleaning_service, "base_price", 0)
                or 0
            )

        return total

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

        added_revenue = False

        for payment in self.payments:
            status = str(
                getattr(payment, "status", getattr(payment, "payment_status", ""))
            ).lower()

            if status not in {"completed", "paid"}:
                continue

            payment_date = getattr(payment, "payment_date", None) or getattr(
                payment, "created_at", None
            )

            if payment_date is None:
                continue

            month = payment_date.strftime("%b")
            monthly_revenue[month] += float(getattr(payment, "amount", 0) or 0)
            added_revenue = True

        if added_revenue:
            return monthly_revenue

        for invoice in self.invoices:
            invoice_date = getattr(invoice, "created_at", None)

            if invoice_date is None:
                continue

            month = invoice_date.strftime("%b")
            monthly_revenue[month] += float(getattr(invoice, "total_amount", 0) or 0)
            added_revenue = True

        if added_revenue:
            return monthly_revenue

        for booking in self.bookings:
            booking_date = getattr(booking, "booking_date", None)

            if booking_date is None:
                continue

            amount = (
                getattr(booking, "total_amount", 0)
                or getattr(booking.cleaning_service, "base_price", 0)
                or 0
            )

            month = booking_date.strftime("%b")
            monthly_revenue[month] += float(amount)

        return monthly_revenue

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

        active_cleaners = len(
            [cleaner for cleaner in self.cleaners if cleaner.is_available]
        )

        active_bookings = len(
            [
                booking
                for booking in self.bookings
                if str(booking.status).lower()
                in {"pending", "confirmed", "assigned", "in_progress", "in progress"}
            ]
        )

        stats = [
            ("Total Customers", len(self.customers), "👤"),
            ("Active Cleaners", active_cleaners, "🧢"),
            ("Active Bookings", active_bookings, "🗓️"),
            ("Total Revenue", f"€{total_revenue:,.2f}", "€"),
        ]

        for index, (title, value, icon) in enumerate(stats):
            cards.grid_columnconfigure(index, weight=1)
            self._stat_card(cards, title, value, icon, index)

    def _stat_card(self, parent, title: str, value, icon: str, column: int) -> None:
        card = ctk.CTkFrame(
            parent,
            fg_color=APP_COLORS["card"],
            corner_radius=16,
            border_width=1,
            border_color=APP_COLORS["border"],
        )
        card.grid(row=0, column=column, sticky="ew", padx=8)

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=18, pady=(16, 6))

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
        ).pack(anchor="w", padx=18, pady=(0, 18))

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

    def _build_recent_bookings(self) -> None:
        card = self._basic_card(self.scroll_frame, "Recent Bookings")
        card.pack(fill="both", expand=True, padx=30, pady=(0, 28))

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