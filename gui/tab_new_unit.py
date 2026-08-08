"""New Unit tab — mixin for ModMakerGUI."""

import tkinter as tk
from tkinter import ttk, messagebox

from constants import COMMON_PARENTS, CIVS
from unit_template import UnitTemplate

class NewUnitMixin:
    """Provides the New Unit tab: form for creating new unit templates."""

    def _build_tab_new_unit(self):
        frame = self.tab_new_unit
        self._new_unit_vars = {}

        fields = [
            ("filename", "Unit Name (auto-prefixed with civ)", "entry", None),
            ("parent", "Parent Template", "combo", COMMON_PARENTS),
            ("civ", "Civilization", "combo", CIVS),
            ("generic_name", "Generic Name", "entry", None),
            ("specific_name", "Specific Name", "entry", None),
            ("max_health", "Max Health", "entry", None),
            ("food_cost", "Food Cost", "entry", None),
            ("walk_speed", "Walk Speed", "entry", None),
        ]

        form = ttk.Frame(frame, padding=24)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Create New Unit", style="Title.TLabel").pack(anchor="w", pady=(0, 12))

        for name, label_text, wtype, values in fields:
            row = ttk.Frame(form)
            row.pack(fill="x", pady=4)
            ttk.Label(row, text=label_text, width=30, anchor="w").pack(side="left", padx=(0, 8))
            var = tk.StringVar()
            self._new_unit_vars[name] = var
            if wtype == "combo":
                w = ttk.Combobox(row, textvariable=var, values=values or [],
                                 width=40, state="readonly")
            else:
                w = ttk.Entry(row, textvariable=var, width=52)
                # Add helper tooltip text for filename field
                if name == "filename":
                    lbl_hint = ttk.Label(row, text="(final: <civ>_<name>.xml)", style="Dim.TLabel")
                    lbl_hint.pack(side="left", padx=(8, 0))
            w.pack(side="left")

        self._new_unit_vars["max_health"].set("100")
        self._new_unit_vars["food_cost"].set("50")
        self._new_unit_vars["walk_speed"].set("8.5")
        self._new_unit_vars["civ"].set("gaia")
        
        # Auto-generate filename when civ changes
        self._new_unit_vars["civ"].trace_add("write", self._auto_update_filename)
        self._new_unit_vars["filename"].trace_add("write", self._clear_auto_generated)

    def _auto_update_filename(self, *args):
        """Auto-prefix filename with civ name."""
        civ = self._new_unit_vars["civ"].get().strip()
        current = self._new_unit_vars["filename"].get().strip()
        if current and not self._was_auto_generated.get():
            return  # User typed something manually, don't override
        
        # Remove old prefix if exists
        if "_" in current:
            parts = current.split("_", 1)
            if parts[0] in CIVS:
                current = parts[1]
        
        # Create new prefixed filename
        self._new_unit_vars["filename"].set(f"{civ}_{current}" if current else civ)

    def _clear_auto_generated(self, *args):
        """Mark that user manually edited the filename."""
        self._was_auto_generated = {"value": False}

    def _create_new_unit(self):
        if not self.project or not self.project.is_loaded:
            messagebox.showwarning("No Mod", "Create or open a mod first.")
            return

        v = self._new_unit_vars
        filename = v["filename"].get().strip()
        civ = v["civ"].get().strip()
        
        # Validate civ prefix in filename
        if not filename:
            messagebox.showerror("Missing", "Unit name is required.")
            return
        
        if not filename.endswith(".xml"):
            filename += ".xml"
        
        # Ensure filename starts with civ name (enforce naming convention)
        basename = filename[:-4]  # Remove .xml
        if not basename.startswith(f"{civ}_"):
            if basename.startswith(tuple(c + "_" for c in CIVS)):
                # Has a different civ prefix — warn user
                warn_result = messagebox.askokcancel(
                    "Warning",
                    f"Unit name '{basename}' has a different civ prefix than selected '{civ}'.\n\n"
                    f"Should we rename it to '{civ}_{basename}'?",
                    parent=self.root
                )
                if warn_result:
                    basename = f"{civ}_{basename}"
            else:
                # No civ prefix — add it
                basename = f"{civ}_{basename}"
        
        filename = basename + ".xml"
        parent = v["parent"].get().strip()
        if not parent:
            messagebox.showerror("Missing", "Parent template is required.")
            return

        tpl = UnitTemplate.new_blank(parent=parent, filename=filename)
        tpl.civ = civ
        tpl.generic_name = v["generic_name"].get().strip() or "New Unit"
        tpl.specific_name = v["specific_name"].get().strip() or "New Unit"
        if v["max_health"].get().strip():
            tpl.max_health = v["max_health"].get().strip()
        if v["food_cost"].get().strip():
            tpl.food_cost = v["food_cost"].get().strip()
        if v["walk_speed"].get().strip():
            tpl.walk_speed = v["walk_speed"].get().strip()

        rel_path = f"simulation/templates/units/{filename}"
        filepath = self.project.mod_dir / rel_path
        tpl.save(filepath)

        messagebox.showinfo(
            "Created",
            f"New unit created with proper civ naming!\n\n"
            f"Path: {rel_path}\n\n"
            f"The filename now follows the 0 A.D. convention:\n"
            f"<civ>_<unitname>.xml"
        )
        
        self._refresh_template_list()
        self.var_selected_template.set(rel_path)
        self._on_template_select(None)