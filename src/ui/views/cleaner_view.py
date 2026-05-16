"""Cleaners view for the CleanSync desktop application."""

from __future__ import annotations

import re
from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from src.models.base_entity import BaseEntity
from src.models.cleaner import Cleaner
from src.repositories.cleaner_repository import CleanerRepository
from src.repositories.service_repository import ServiceRepository
from src.ui.theme import APP_COLORS, APP_FONTS


class CleanersView(ctk.CTkFrame):
    """Cleaners page with Base44-style cards and modal form."""

    def __init__(self, parent) -> None:
        super().__init__(parent, fg_color=APP_COLORS["background"])
        self.pack(fill="both", expand=True)

        self.search_entry: ctk.CTkEntry | None = None
        self.cards_frame: ctk.CTkFrame | None = None

        self._build_page()

    def _build_page(self) -> None:
        self._build_header()
        self._build_cards()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(28, 22))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            left,
            text="Cleaners",
            text_color=APP_COLORS["foreground"],
            font=("Inter", 28, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text=f"{len(CleanerRepository.find_all())} team members",
            text_color=APP_COLORS["muted_text"],
            font=APP_FONTS["body"],
        ).pack(anchor="w", pady=(4, 0))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")

        self.search_entry = ctk.CTkEntry(
            right,
            placeholder_text="Search...",
            width=250,
            height=40,
            corner_radius=10,
            border_color=APP_COLORS["border"],
        )
        self.search_entry.pack(side="left", padx=(0, 12))
        self.search_entry.bind("<KeyRelease>", lambda _event: self._refresh_cards())

        ctk.CTkButton(
            right,
            text="+  Add Cleaner",
            width=160,
            height=40,
            corner_radius=10,
            fg_color=APP_COLORS["primary"],
            hover_color=APP_COLORS["primary_hover"],
            font=APP_FONTS["button"],
            command=lambda: self._open_modal(),
        ).pack(side="left")

    def _build_cards(self) -> None:
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        self._refresh_cards()

    def _refresh_cards(self) -> None:
        if self.cards_frame is None:
            return

        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        cleaners = self._filtered_cleaners()

        if not cleaners:
            ctk.CTkLabel(
                self.cards_frame,
                text="No cleaners found. Add your first cleaner using the button above.",
                text_color=APP_COLORS["muted_text"],
                font=APP_FONTS["body"],
            ).pack(pady=60)
            return

        for index, cleaner in enumerate(cleaners):
            self.cards_frame.grid_columnconfigure(index % 3, weight=1)
            self._cleaner_card(cleaner, index // 3, index % 3)

    def _cleaner_card(self, cleaner: Cleaner, row: int, column: int) -> None:
        card = ctk.CTkFrame(
            self.cards_frame,
            fg_color=APP_COLORS["card"],
            corner_radius=16,
            border_width=1,
            border_color=APP_COLORS["border"],
        )
        card.grid(row=row, column=column, sticky="nsew", padx=9, pady=9)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(18, 10))

        initial = cleaner.first_name[:1].upper() if cleaner.first_name else "?"

        ctk.CTkLabel(
            top,
            text=initial,
            width=46,
            height=46,
            fg_color="#e0f2fe",
            text_color=APP_COLORS["primary"],
            corner_radius=23,
            font=("Inter", 18, "bold"),
        ).pack(side="left")

        info = ctk.CTkFrame(top, fg_color="transparent")
        info.pack(side="left", padx=12, fill="x", expand=True)

        ctk.CTkLabel(
            info,
            text=cleaner.full_name,
            text_color=APP_COLORS["foreground"],
            font=("Inter", 14, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            info,
            text=f"€{cleaner.hourly_rate:.2f}/hr",
            text_color=APP_COLORS["muted_text"],
            font=APP_FONTS["small"],
        ).pack(anchor="w", pady=(2, 0))

        status_bg, status_fg = self._status_colours(cleaner.status)

        ctk.CTkLabel(
            top,
            text=cleaner.status,
            text_color=status_fg,
            fg_color=status_bg,
            corner_radius=10,
            width=86,
            height=24,
            font=("Inter", 11, "bold"),
        ).pack(side="right")

        details = ctk.CTkFrame(card, fg_color="transparent")
        details.pack(fill="x", padx=20, pady=(6, 4))

        for text in [
            f"☎  {cleaner.phone_number}",
            f"✉  {cleaner.email}",
            f"⭐  {cleaner.rating:.1f}/5",
        ]:
            ctk.CTkLabel(
                details,
                text=text,
                text_color=APP_COLORS["muted_text"],
                font=APP_FONTS["small"],
            ).pack(anchor="w", pady=2)

        tags = ctk.CTkFrame(card, fg_color="transparent")
        tags.pack(fill="x", padx=20, pady=(8, 16))

        for item in cleaner.specializations.split(","):
            tag_text = item.strip()
            if tag_text:
                ctk.CTkLabel(
                    tags,
                    text=tag_text,
                    text_color=APP_COLORS["muted_text"],
                    fg_color=APP_COLORS["muted"],
                    corner_radius=10,
                    height=24,
                    font=APP_FONTS["small"],
                ).pack(side="left", padx=(0, 6), pady=2)

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(fill="x", padx=18, pady=(0, 18))

        ctk.CTkButton(
            actions,
            text="Edit",
            width=80,
            height=30,
            fg_color=APP_COLORS["secondary"],
            hover_color=APP_COLORS["border"],
            text_color=APP_COLORS["foreground"],
            command=lambda selected=cleaner: self._open_modal(selected),
        ).pack(side="left")

        ctk.CTkButton(
            actions,
            text="Delete",
            width=90,
            height=30,
            fg_color=APP_COLORS["danger"],
            hover_color=APP_COLORS["danger_hover"],
            command=lambda selected=cleaner: self._delete_cleaner(selected),
        ).pack(side="right")

    def _filtered_cleaners(self) -> list[Cleaner]:
        search_text = self.search_entry.get().strip().lower() if self.search_entry else ""
        cleaners = CleanerRepository.find_all()

        if not search_text:
            return cleaners

        return [
            cleaner
            for cleaner in cleaners
            if search_text in cleaner.full_name.lower()
            or search_text in cleaner.email.lower()
            or search_text in cleaner.phone_number.lower()
            or search_text in cleaner.specializations.lower()
            or search_text in cleaner.status.lower()
        ]

    def _open_modal(self, cleaner: Cleaner | None = None) -> None:
        modal = ctk.CTkToplevel(self)
        modal.title("Edit Cleaner" if cleaner else "New Cleaner")
        modal.geometry("520x680")
        modal.resizable(False, False)
        modal.grab_set()

        card = ctk.CTkFrame(modal, fg_color=APP_COLORS["card"], corner_radius=16)
        card.pack(fill="both", expand=True, padx=18, pady=18)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=22, pady=(20, 14))

        ctk.CTkLabel(
            top,
            text="Edit Cleaner" if cleaner else "New Cleaner",
            text_color=APP_COLORS["foreground"],
            font=("Inter", 20, "bold"),
        ).pack(side="left")

        ctk.CTkButton(
            top,
            text="×",
            width=34,
            height=30,
            fg_color="transparent",
            hover_color=APP_COLORS["muted"],
            text_color=APP_COLORS["muted_text"],
            command=modal.destroy,
        ).pack(side="right")

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=22)

        entries: dict[str, ctk.CTkEntry] = {}

        entries["Full Name"] = self._modal_entry(body, "Full Name *", "e.g. John Smith")

        row_one = ctk.CTkFrame(body, fg_color="transparent")
        row_one.pack(fill="x")
        row_one.grid_columnconfigure((0, 1), weight=1)

        entries["Email"] = self._modal_entry_grid(
            row_one,
            "Email *",
            "e.g. john@cleansync.com",
            0,
            0,
        )
        entries["Phone Number"] = self._modal_entry_grid(
            row_one,
            "Phone *",
            "e.g. (+371) 123-4567",
            0,
            1,
        )

        row_two = ctk.CTkFrame(body, fg_color="transparent")
        row_two.pack(fill="x")
        row_two.grid_columnconfigure((0, 1), weight=1)

        entries["Hourly Rate"] = self._modal_entry_grid(
            row_two,
            "Hourly Rate (€) *",
            "e.g. 25.00",
            0,
            0,
        )
        entries["Rating"] = self._modal_entry_grid(
            row_two,
            "Rating (1-5)",
            "e.g. 4.5",
            0,
            1,
        )

        ctk.CTkLabel(
            body,
            text="Status",
            text_color=APP_COLORS["foreground"],
            font=APP_FONTS["small"],
        ).pack(anchor="w", pady=(8, 4))

        status_var = ctk.StringVar(value=cleaner.status if cleaner else "Available")

        ctk.CTkOptionMenu(
            body,
            values=["Available", "On Job", "Off Duty", "Inactive"],
            variable=status_var,
            height=40,
            corner_radius=10,
            fg_color=APP_COLORS["secondary"],
            button_color=APP_COLORS["primary"],
            button_hover_color=APP_COLORS["primary_hover"],
            text_color=APP_COLORS["foreground"],
        ).pack(fill="x")

        ctk.CTkLabel(
            body,
            text="Services Offered *",
            text_color=APP_COLORS["foreground"],
            font=APP_FONTS["small"],
        ).pack(anchor="w", pady=(12, 4))

        available_services = [service.service_name for service in ServiceRepository.find_all()]
        selected_service_var = ctk.StringVar(value="Select service")

        spec_row = ctk.CTkFrame(body, fg_color="transparent")
        spec_row.pack(fill="x")

        service_combo = ctk.CTkComboBox(
            spec_row,
            values=available_services if available_services else ["No services available"],
            variable=selected_service_var,
            state="readonly",
            height=40,
            corner_radius=10,
            border_width=1,
            border_color=APP_COLORS["border"],
            fg_color=APP_COLORS["card"],
            button_color=APP_COLORS["card"],
            button_hover_color=APP_COLORS["muted"],
            text_color=APP_COLORS["foreground"],
            dropdown_fg_color=APP_COLORS["card"],
            dropdown_hover_color=APP_COLORS["accent"],
            dropdown_text_color=APP_COLORS["foreground"],
        )
        service_combo.pack(side="left", fill="x", expand=True, padx=(0, 8))

        specialization_values: list[str] = []

        chips_frame = ctk.CTkFrame(body, fg_color="transparent")
        chips_frame.pack(fill="x", pady=(8, 0))

        def refresh_specialization_chips() -> None:
            for widget in chips_frame.winfo_children():
                widget.destroy()

            for value in specialization_values:
                chip = ctk.CTkFrame(chips_frame, fg_color="#e0f2fe", corner_radius=12)
                chip.pack(side="left", padx=(0, 6), pady=3)

                ctk.CTkLabel(
                    chip,
                    text=value,
                    text_color=APP_COLORS["primary"],
                    font=APP_FONTS["small"],
                ).pack(side="left", padx=(10, 2), pady=4)

                ctk.CTkButton(
                    chip,
                    text="×",
                    width=20,
                    height=20,
                    fg_color="transparent",
                    hover_color=APP_COLORS["border"],
                    text_color=APP_COLORS["primary"],
                    command=lambda selected=value: remove_specialization(selected),
                ).pack(side="left", padx=(0, 6), pady=3)

        def remove_specialization(value: str) -> None:
            if value in specialization_values:
                specialization_values.remove(value)
                refresh_specialization_chips()

        def add_specialization() -> None:
            selected_service = selected_service_var.get().strip()

            if (
                not selected_service
                or selected_service == "Select service"
                or selected_service == "No services available"
            ):
                return

            if selected_service not in specialization_values:
                specialization_values.append(selected_service)

            selected_service_var.set("Select service")
            refresh_specialization_chips()

        ctk.CTkButton(
            spec_row,
            text="Add",
            width=70,
            height=40,
            fg_color=APP_COLORS["secondary"],
            hover_color=APP_COLORS["border"],
            text_color=APP_COLORS["foreground"],
            command=add_specialization,
        ).pack(side="right")

        if cleaner is not None:
            entries["Full Name"].insert(0, cleaner.full_name)
            entries["Email"].insert(0, cleaner.email)
            entries["Phone Number"].insert(0, cleaner.phone_number)
            entries["Hourly Rate"].insert(0, str(cleaner.hourly_rate))
            entries["Rating"].insert(0, str(cleaner.rating))

            specialization_values.extend(
                item.strip()
                for item in cleaner.specializations.split(",")
                if item.strip()
            )
            refresh_specialization_chips()

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.pack(fill="x", padx=22, pady=(18, 22))

        ctk.CTkButton(
            buttons,
            text="Save",
            height=44,
            corner_radius=10,
            fg_color=APP_COLORS["primary"],
            hover_color=APP_COLORS["primary_hover"],
            font=APP_FONTS["button"],
            command=lambda: self._save_cleaner(
                entries,
                specialization_values,
                status_var,
                modal,
                cleaner,
            ),
        ).pack(side="right", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            buttons,
            text="Cancel",
            height=44,
            corner_radius=10,
            fg_color=APP_COLORS["secondary"],
            hover_color=APP_COLORS["border"],
            text_color=APP_COLORS["foreground"],
            font=APP_FONTS["button"],
            command=modal.destroy,
        ).pack(side="left", fill="x", expand=True, padx=(8, 0))

    def _modal_entry(self, parent, label: str, placeholder: str = "") -> ctk.CTkEntry:
        ctk.CTkLabel(
            parent,
            text=label,
            text_color=APP_COLORS["foreground"],
            font=APP_FONTS["small"],
        ).pack(anchor="w", pady=(8, 4))

        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=40,
            corner_radius=10,
            border_color=APP_COLORS["border"],
        )
        entry.pack(fill="x")
        return entry

    def _modal_entry_grid(
        self,
        parent,
        label: str,
        placeholder: str,
        row: int,
        column: int,
    ) -> ctk.CTkEntry:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=column, sticky="ew", padx=(0, 8) if column == 0 else (8, 0))

        ctk.CTkLabel(
            frame,
            text=label,
            text_color=APP_COLORS["foreground"],
            font=APP_FONTS["small"],
        ).pack(anchor="w", pady=(8, 4))

        entry = ctk.CTkEntry(
            frame,
            placeholder_text=placeholder,
            height=40,
            corner_radius=10,
            border_color=APP_COLORS["border"],
        )
        entry.pack(fill="x")
        return entry

    def _save_cleaner(
        self,
        entries: dict[str, ctk.CTkEntry],
        specialization_values: list[str],
        status_var: ctk.StringVar,
        modal: ctk.CTkToplevel,
        existing_cleaner: Cleaner | None,
    ) -> None:
        values = {field: entry.get().strip() for field, entry in entries.items()}
        final_specializations = specialization_values.copy()

        if (
            not values["Full Name"]
            or not values["Email"]
            or not values["Phone Number"]
            or not values["Hourly Rate"]
            or not final_specializations
        ):
            self._error("Please complete all required fields.")
            return

        name_parts = values["Full Name"].split(maxsplit=1)

        if len(name_parts) < 2:
            self._error("Please enter both first and last name.")
            return

        if not name_parts[0].isalpha():
            self._error("First name must contain letters only.")
            return

        if not name_parts[1].replace(" ", "").isalpha():
            self._error("Last name must contain letters only.")
            return

        email = values["Email"].strip().lower()

        if not email.endswith("@cleansync.com"):
            self._error("Cleaner email must use the company domain (@cleansync.com).")
            return

        email_pattern = r"^[A-Za-z0-9._%+-]+@cleansync\.com$"

        if not re.match(email_pattern, email):
            self._error(
                "Please enter a valid CleanSync company email, "
                "e.g. john@cleansync.com."
            )
            return

        cleaned_phone = (
            values["Phone Number"]
            .replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
            .replace("+", "")
        )

        if not cleaned_phone.isdigit():
            self._error("Phone number must contain digits only.")
            return

        if len(cleaned_phone) < 8 or len(cleaned_phone) > 15:
            self._error("Phone number must contain 8–15 digits.")
            return

        try:
            hourly_rate = float(values["Hourly Rate"])
            rating = float(values["Rating"]) if values["Rating"] else 5.0
        except ValueError:
            self._error("Hourly rate and rating must be valid numbers.")
            return

        if hourly_rate <= 0:
            self._error("Hourly rate must be greater than zero.")
            return

        if not 1 <= rating <= 5:
            self._error("Rating must be between 1 and 5.")
            return

        cleaner = Cleaner(
            entity_id=existing_cleaner.entity_id if existing_cleaner else BaseEntity.generate_id(),
            created_at=existing_cleaner.created_at if existing_cleaner else datetime.now(),
            first_name=name_parts[0],
            last_name=name_parts[1],
            email=email,
            phone_number=values["Phone Number"],
            hourly_rate=hourly_rate,
            rating=rating,
            status=status_var.get(),
            specializations=", ".join(final_specializations),
            service_area="",
        )

        CleanerRepository.save_cleaner(cleaner)
        modal.destroy()
        self._refresh_page()

    def _delete_cleaner(self, cleaner: Cleaner) -> None:
        confirmed = messagebox.askyesno("Delete Cleaner", f"Delete {cleaner.full_name}?")

        if not confirmed:
            return

        CleanerRepository.delete(cleaner.entity_id)
        self._refresh_page()

    def _refresh_page(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

        self.search_entry = None
        self.cards_frame = None
        self._build_page()

    @staticmethod
    def _status_colours(status: str) -> tuple[str, str]:
        if status == "Available":
            return "#dcfce7", APP_COLORS["success"]
        if status == "On Job":
            return "#dbeafe", APP_COLORS["primary"]
        if status == "Off Duty":
            return "#fef3c7", "#b45309"
        return "#f1f5f9", APP_COLORS["muted_text"]

    @staticmethod
    def _error(message: str) -> None:
        messagebox.showerror("Validation Error", message)
