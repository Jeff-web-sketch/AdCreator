"""Mod Info tab — mixin for ModMakerGUI."""

import tkinter as tk
from tkinter import ttk, messagebox

from constants import STYLE

class ModInfoMixin:
    """Provides the Mod Info tab: edit mod.json metadata."""

    def _build_tab_modinfo(self):
        frame = self.tab_modinfo
        self._modinfo_vars = {}

        # Main container with card-style design
        main_container = ttk.Frame(frame, padding=24)
        main_container.pack(fill="both", expand=True)

        # Header section
        ttk.Label(main_container, text="Mod Metadata", style="Title.TLabel").pack(anchor="w", pady=(0, 8))
        ttk.Label(main_container, text="Configure your mod's basic information and dependencies", 
                 style="Dim.TLabel").pack(anchor="w", pady=(0, 20))

        # Card for form fields
        form_card = ttk.Frame(main_container, style="Card.TFrame", padding=20, relief="raised", borderwidth=2)
        form_card.pack(fill="both", expand=True)

        fields = [
            ("name", "Mod Name (internal)", "The technical identifier for your mod"),
            ("label", "Display Label", "The user-friendly name shown in game"),
            ("version", "Version", "Semantic versioning (e.g., 1.0.0)"),
            ("description", "Description", "Detailed description of your mod"),
            ("dependencies", "Dependencies", "Comma-separated mod dependencies"),
        ]

        for name, label_text, help_text in fields:
            # Field container
            field_container = ttk.Frame(form_card)
            field_container.pack(fill="x", pady=(12, 8))
            
            # Label with help text
            label_frame = ttk.Frame(field_container)
            label_frame.pack(fill="x", pady=(0, 4))
            
            ttk.Label(label_frame, text=label_text, style="Header.TLabel").pack(side="left")
            ttk.Label(label_frame, text=f"  • {help_text}", style="Muted.TLabel").pack(side="left")
            
            var = tk.StringVar()
            self._modinfo_vars[name] = var
            
            if name == "description":
                w = tk.Text(field_container, height=5, width=60, bg=STYLE["entry_bg"],
                            fg=STYLE["text"], font=("Segoe UI", 11),
                            insertbackground=STYLE["accent"], borderwidth=2,
                            relief="solid", selectbackground=STYLE["accent"], 
                            selectforeground="#ffffff", padx=8, pady=6)
                w.pack(side="left", fill="both", expand=True)
                self._modinfo_desc_widget = w
            else:
                w = ttk.Entry(field_container, textvariable=var, width=60)
                w.pack(side="left", fill="x", expand=True)
            self._modinfo_vars[name] = var

        # Default dependencies
        if "dependencies" in self._modinfo_vars:
            self._modinfo_vars["dependencies"].set("0ad=0.28.0")

        # Action buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill="x", pady=(20, 0))
        
        ttk.Button(button_frame, text="Save Mod Info", style="Accent.TButton",
                   command=self._save_mod_info).pack(side="left")
        ttk.Button(button_frame, text="Reset", command=self._load_mod_info_into_form).pack(side="left", padx=(8, 0))

    def _load_mod_info_into_form(self):
        if not self.project or not self.project.is_loaded:
            return
        info = self.project.info
        self._modinfo_vars["name"].set(info.name)
        self._modinfo_vars["label"].set(info.label)
        self._modinfo_vars["version"].set(info.version)
        self._modinfo_vars["dependencies"].set(", ".join(info.dependencies))
        self._modinfo_desc_widget.delete("1.0", "end")
        self._modinfo_desc_widget.insert("1.0", info.description)

    def _save_mod_info(self):
        if not self.project or not self.project.is_loaded:
            return
        info = self.project.info
        info.name = self._modinfo_vars["name"].get().strip()
        info.label = self._modinfo_vars["label"].get().strip()
        info.version = self._modinfo_vars["version"].get().strip()
        info.description = self._modinfo_desc_widget.get("1.0", "end").strip()
        deps_str = self._modinfo_vars["dependencies"].get().strip()
        info.dependencies = [d.strip() for d in deps_str.split(",") if d.strip()]
        self.project.save_info()
        messagebox.showinfo("Saved", "Mod metadata saved.")