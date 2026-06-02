"""Services view for the CleanSync desktop application."""

from __future__ import annotations

from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from src.models.base_entity import BaseEntity
from src.models.service import CleaningService
from src.repositories.service_repository import ServiceRepository
from src.ui.theme import APP_COLORS, APP_FONTS


class ServicesView(ctk.CTkFrame):
    """Services page with service cards and modal form."""

    CARD_WIDTH = 330
    CARD_HEIGHT = 210
    CARD_COLUMN_WIDTH = 350

    def __init__(self, parent) -> None:
        super().__init__(parent, fg_color=APP_COLORS["background"])
        self.pack(fill="both", expand=True)

        self.cards_frame: ctk.CTkScrollableFrame | None = None
        self._build_page()

    def _build_page(self) -> None:
        self._build_header()
        self._build_service_cards()

    def _build_header(self) -> None:
        services = ServiceRepository.find_all()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(28, 22))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            left,
            text="Services",
            text_color=APP_COLORS["foreground"],
            font=("Inter", 28, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text=f"{len(services)} cleaning services",
            text_color=APP_COLORS["muted_text"],
            font=APP_FONTS["body"],
        ).pack(anchor="w", pady=(4, 0))

        ctk.CTkButton(
            header,
            text="+  Add Service",
            width=160,
            height=40,
            corner_radius=10,
            fg_color=APP_COLORS["primary"],
            hover_color=APP_COLORS["primary_hover"],
            font=APP_FONTS["button"],
            command=self._open_modal,
        ).grid(row=0, column=1, sticky="e")

    def _build_service_cards(self) -> None:
        self.cards_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=APP_COLORS["border"],
            scrollbar_button_hover_color=APP_COLORS["muted_text"],
        )
        self.cards_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        self._refresh_cards()

    def _refresh_cards(self) -> None:
        if self.cards_frame is None:
            return

        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        services = ServiceRepository.find_all()

        for column in range(3):
            self.cards_frame.grid_columnconfigure(
                column,
                weight=0,
                minsize=self.CARD_COLUMN_WIDTH,
            )

        if not services:
            ctk.CTkLabel(
                self.cards_frame,
                text="No services yet. Create your first service offering above.",
                text_color=APP_COLORS["muted_text"],
                font=APP_FONTS["body"],
            ).pack(pady=80)
            return

        for index, service in enumerate(services):
            self._service_card(service, index // 3, index % 3)

    def _service_card(self, service: CleaningService, row: int, column: int) -> None:
        card = ctk.CTkFrame(
            self.cards_frame,
            fg_color=APP_COLORS["card"],
            corner_radius=14,
            border_width=1,
            border_color=APP_COLORS["border"],
            width=self.CARD_WIDTH,
            height=self.CARD_HEIGHT,
        )
        card.grid(row=row, column=column, sticky="w", padx=9, pady=9)
        card.grid_propagate(False)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(18, 4))
        top.grid_columnconfigure(0, weight=1)
        top.grid_columnconfigure(1, weight=0)

        ctk.CTkLabel(
            top,
            text=service.service_name,
            text_color=APP_COLORS["foreground"],
            font=("Inter", 16, "bold"),
            wraplength=190,
            justify="left",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            top,
            text=f"€{service.base_price:.0f}",
            text_color=APP_COLORS["primary"],
            font=("Inter", 22, "bold"),
            width=80,
            anchor="e",
        ).grid(row=0, column=1, sticky="e")

        category_chip = ctk.CTkFrame(
            card,
            fg_color=APP_COLORS["card"],
            corner_radius=8,
            border_width=1,
            border_color=APP_COLORS["border"],
        )
        category_chip.pack(anchor="w", padx=20, pady=(2, 8))

        ctk.CTkLabel(
            category_chip,
            text=service.category,
            text_color=APP_COLORS["foreground"],
            font=("Inter", 11, "bold"),
        ).pack(padx=10, pady=3)

        ctk.CTkLabel(
            card,
            text=self._short_text(service.description, 78),
            wraplength=280,
            justify="left",
            text_color=APP_COLORS["muted_text"],
            font=APP_FONTS["small"],
        ).pack(anchor="w", padx=20, pady=(0, 10))

        hourly_price = (
            service.base_price / service.duration_hours
            if service.duration_hours > 0
            else 0
        )

        details = f"◷ {service.duration_hours:.0f}h     €{hourly_price:.0f}/hr"

        ctk.CTkLabel(
            card,
            text=details,
            text_color=APP_COLORS["muted_text"],
            font=APP_FONTS["small"],
        ).pack(anchor="w", padx=20, pady=(0, 8))

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(anchor="e", padx=16, pady=(0, 10))

        ctk.CTkButton(
            actions,
            text="✎",
            width=30,
            height=28,
            fg_color="transparent",
            hover_color=APP_COLORS["muted"],
            text_color=APP_COLORS["foreground"],
            command=lambda selected=service: self._open_modal(selected),
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            actions,
            text="🗑",
            width=30,
            height=28,
            fg_color="transparent",
            hover_color=APP_COLORS["muted"],
            text_color=APP_COLORS["danger"],
            command=lambda selected=service: self._delete_service(selected),
        ).pack(side="left")

    def _open_modal(self, service: CleaningService | None = None) -> None:
        modal = ctk.CTkToplevel(self)
        modal.title("Edit Service" if service else "New Service")
        modal.geometry("460x680")
        modal.resizable(False, False)
        modal.grab_set()

        card = ctk.CTkFrame(modal, fg_color=APP_COLORS["card"], corner_radius=16)
        card.pack(fill="both", expand=True, padx=18, pady=18)

        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=22, pady=(22, 10))
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top,
            text="Edit Service" if service else "New Service",
            text_color=APP_COLORS["foreground"],
            font=("Inter", 20, "bold"),
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            top,
            text="×",
            width=34,
            height=30,
            fg_color="transparent",
            hover_color=APP_COLORS["muted"],
            text_color=APP_COLORS["muted_text"],
            command=modal.destroy,
        ).grid(row=0, column=1, sticky="e")

        body = ctk.CTkScrollableFrame(
            card,
            fg_color="transparent",
            scrollbar_button_color=APP_COLORS["border"],
            scrollbar_button_hover_color=APP_COLORS["muted_text"],
        )
        body.grid(row=1, column=0, sticky="nsew", padx=22)

        name_entry = self._modal_entry(body, "Service Name *")

        ctk.CTkLabel(
            body,
            text="Description",
            text_color=APP_COLORS["foreground"],
            font=APP_FONTS["small"],
        ).pack(anchor="w", pady=(12, 4))

        description_entry = ctk.CTkTextbox(
            body,
            height=70,
            corner_radius=10,
            border_width=1,
            border_color=APP_COLORS["border"],
            fg_color=APP_COLORS["card"],
            text_color=APP_COLORS["foreground"],
        )
        description_entry.pack(fill="x")

        ctk.CTkLabel(
            body,
            text="Category * (select 1 to 3)",
            text_color=APP_COLORS["foreground"],
            font=APP_FONTS["small"],
        ).pack(anchor="w", pady=(12, 4))

        category_options = [
            "Residential",
            "Commercial",
            "Deep Clean",
            "Move In/Out",
            "Post Construction",
            "Specialized",
        ]

        category_vars: dict[str, ctk.BooleanVar] = {}

        category_frame = ctk.CTkFrame(
            body,
            fg_color=APP_COLORS["card"],
            corner_radius=10,
            border_width=1,
            border_color=APP_COLORS["border"],
        )
        category_frame.pack(fill="x")

        for category in category_options:
            category_vars[category] = ctk.BooleanVar(value=False)

            ctk.CTkCheckBox(
                category_frame,
                text=category,
                variable=category_vars[category],
                text_color=APP_COLORS["foreground"],
                font=APP_FONTS["small"],
                fg_color=APP_COLORS["primary"],
                hover_color=APP_COLORS["primary_hover"],
            ).pack(anchor="w", padx=12, pady=3)

        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x", pady=(12, 0))
        row.grid_columnconfigure((0, 1), weight=1)

        price_entry = self._modal_entry_grid(row, "Base Price (€) *", 0, 0)
        duration_entry = self._modal_entry_grid(row, "Duration (hours) *", 0, 1)

        active_var = ctk.BooleanVar(value=True)

        ctk.CTkSwitch(
            body,
            text="Active",
            variable=active_var,
            progress_color=APP_COLORS["primary"],
            button_color=APP_COLORS["card"],
            text_color=APP_COLORS["foreground"],
            font=APP_FONTS["body"],
        ).pack(anchor="w", pady=(18, 8))

        if service is not None:
            name_entry.insert(0, service.service_name)
            description_entry.insert("1.0", service.description)
            price_entry.insert(0, str(service.base_price))
            duration_entry.insert(0, str(service.duration_hours))

            saved_categories = service.category or "Residential"
            for category in saved_categories.split(","):
                cleaned_category = category.strip()
                if cleaned_category in category_vars:
                    category_vars[cleaned_category].set(True)
        else:
            category_vars["Residential"].set(True)

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.grid(row=2, column=0, sticky="ew", padx=22, pady=(12, 22))

        ctk.CTkButton(
            buttons,
            text="Save",
            width=110,
            height=44,
            corner_radius=10,
            fg_color="#9bd3f0",
            hover_color=APP_COLORS["primary"],
            text_color="#ffffff",
            font=APP_FONTS["button"],
            command=lambda: self._save_service(
                modal,
                service,
                name_entry,
                description_entry,
                price_entry,
                duration_entry,
                category_vars,
            ),
        ).pack(side="right")

        ctk.CTkButton(
            buttons,
            text="Cancel",
            width=110,
            height=44,
            corner_radius=10,
            fg_color=APP_COLORS["card"],
            hover_color=APP_COLORS["muted"],
            text_color=APP_COLORS["foreground"],
            border_width=1,
            border_color=APP_COLORS["border"],
            font=APP_FONTS["button"],
            command=modal.destroy,
        ).pack(side="right", padx=(0, 12))

    def _save_service(
        self,
        modal: ctk.CTkToplevel,
        existing_service: CleaningService | None,
        name_entry: ctk.CTkEntry,
        description_entry: ctk.CTkTextbox,
        price_entry: ctk.CTkEntry,
        duration_entry: ctk.CTkEntry,
        category_vars: dict[str, ctk.BooleanVar],
    ) -> None:
        name = name_entry.get().strip()
        description = description_entry.get("1.0", "end").strip()
        price = price_entry.get().strip()
        duration = duration_entry.get().strip()

        if not name or not description or not price or not duration:
            self._error("Please complete all required fields.")
            return

        selected_categories = [
            category
            for category, variable in category_vars.items()
            if variable.get()
        ]

        if len(selected_categories) < 1:
            self._error("Please select at least one category.")
            return

        if len(selected_categories) > 3:
            self._error("Please select no more than three categories.")
            return

        try:
            base_price = float(price)
            duration_hours = float(duration)
        except ValueError:
            self._error("Base price and duration must be valid numbers.")
            return

        if base_price <= 0 or duration_hours <= 0:
            self._error("Base price and duration must be greater than zero.")
            return

        service_to_save = CleaningService(
            entity_id=existing_service.entity_id
            if existing_service
            else BaseEntity.generate_id(),
            created_at=existing_service.created_at if existing_service else datetime.now(),
            service_name=name,
            description=description,
            duration_hours=duration_hours,
            base_price=base_price,
            category=", ".join(selected_categories),
        )

        ServiceRepository.save_service(service_to_save)
        modal.destroy()
        self._refresh_whole_page()

    def _delete_service(self, service: CleaningService) -> None:
        confirmed = messagebox.askyesno(
            "Delete Service",
            f"Delete service '{service.service_name}'?",
        )

        if not confirmed:
            return

        try:
            ServiceRepository.delete(service.entity_id)
        except Exception:
            self._error(
                "This service cannot be deleted because it is linked to existing bookings."
            )
            return

        self._refresh_whole_page()

    def _refresh_whole_page(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

        self.cards_frame = None
        self._build_page()

    def _modal_entry(self, parent, label: str) -> ctk.CTkEntry:
        ctk.CTkLabel(
            parent,
            text=label,
            text_color=APP_COLORS["foreground"],
            font=APP_FONTS["small"],
        ).pack(anchor="w", pady=(8, 4))

        entry = ctk.CTkEntry(
            parent,
            height=40,
            corner_radius=10,
            border_color=APP_COLORS["border"],
        )
        entry.pack(fill="x")
        return entry

    def _modal_entry_grid(self, parent, label: str, row: int, column: int) -> ctk.CTkEntry:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(
            row=row,
            column=column,
            sticky="ew",
            padx=(0, 8) if column == 0 else (8, 0),
        )

        ctk.CTkLabel(
            frame,
            text=label,
            text_color=APP_COLORS["foreground"],
            font=APP_FONTS["small"],
        ).pack(anchor="w", pady=(0, 4))

        entry = ctk.CTkEntry(
            frame,
            height=40,
            corner_radius=10,
            border_color=APP_COLORS["border"],
        )
        entry.pack(fill="x")
        return entry

    @staticmethod
    def _short_text(text: str, limit: int) -> str:
        if len(text) <= limit:
            return text
        return text[:limit].rstrip() + "..."

    @staticmethod
    def _error(message: str) -> None:
        messagebox.showerror("Validation Error", message)
