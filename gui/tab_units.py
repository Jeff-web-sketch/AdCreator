"""Unit Editor tab — mixin for ModMakerGUI."""

import os
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from constants import STYLE, CIVS
from unit_template import UnitTemplate


class UnitEditorMixin:
    """Provides the Unit Editor tab: template selector + form editor + XML preview."""

    def _build_tab_units(self):
        frame = self.tab_units

        sel_frame = ttk.Frame(frame, padding=(8, 8))
        sel_frame.pack(fill="x")

        ttk.Label(sel_frame, text="Template:", style="TLabel").pack(side="left", padx=(0, 4))
        self.var_selected_template = tk.StringVar()
        self.combo_templates = ttk.Combobox(sel_frame, textvariable=self.var_selected_template,
                                            state="readonly", width=50)
        self.combo_templates.pack(side="left", padx=(0, 8))
        self.combo_templates.bind("<<ComboboxSelected>>", self._on_template_select)

        ttk.Button(sel_frame, text="Reload List",
                   command=self._refresh_template_list).pack(side="left", padx=4)
        ttk.Button(sel_frame, text="Import from Game",
                   command=self._import_template_dialog).pack(side="left", padx=4)
        ttk.Button(sel_frame, text="Save", style="Accent.TButton",
                   command=self._save_current_template).pack(side="right")

        canvas = tk.Canvas(frame, bg=STYLE["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.form_container = ttk.Frame(canvas)
        self.form_container.bind("<Configure>",
                                 lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.form_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=(0, 8))
        scrollbar.pack(side="right", fill="y", pady=(0, 8))

        self._build_unit_form(self.form_container)

    def _build_unit_form(self, parent):
        self._var_widgets = {}

        sections = [
            ("Entity", [
                ("parent_template", "Parent Template", "entry", None),
            ]),
            ("Identity", [
                ("civ", "Civilization", "combo", CIVS),
                ("generic_name", "Generic Name", "entry", None),
                ("specific_name", "Specific Name", "entry", None),
                ("visible_classes", "Visible Classes (tokens)", "entry", None),
                ("icon", "Icon Path", "entry", None),
            ]),
            ("Health", [
                ("max_health", "Max Health", "entry", None),
            ]),
            ("Cost", [
                ("food_cost", "Food", "entry", None),
                ("wood_cost", "Wood", "entry", None),
                ("stone_cost", "Stone", "entry", None),
                ("metal_cost", "Metal", "entry", None),
            ]),
            ("Movement", [
                ("walk_speed", "Walk Speed", "entry", None),
                ("run_speed", "Run Speed", "entry", None),
            ]),
            ("Armor (Resistance)", [
                ("hack_armor", "Hack Armor", "entry", None),
                ("pierce_armor", "Pierce Armor", "entry", None),
            ]),
            ("Melee Attack", [
                ("melee_hack", "Hack Damage", "entry", None),
                ("melee_pierce", "Pierce Damage", "entry", None),
                ("melee_crush", "Crush Damage", "entry", None),
                ("melee_range", "Max Range", "entry", None),
            ]),
            ("Ranged Attack", [
                ("ranged_pierce", "Pierce Damage", "entry", None),
                ("ranged_hack", "Hack Damage", "entry", None),
                ("ranged_crush", "Crush Damage", "entry", None),
                ("ranged_range", "Max Range", "entry", None),
                ("ranged_repeat", "Repeat Time (ms)", "entry", None),
            ]),
            ("Visual", [
                ("actor", "Actor (Model Reference)", "entry", None),
            ]),
        ]

        row = 0
        for section_name, fields in sections:
            ttk.Label(parent, text=section_name, style="Title.TLabel").grid(
                row=row, column=0, columnspan=2, sticky="w", padx=8, pady=(12, 4))
            row += 1
            for prop_name, label_text, widget_type, combo_values in fields:
                ttk.Label(parent, text=label_text).grid(
                    row=row, column=0, sticky="w", padx=(16, 8), pady=2)
                var = tk.StringVar()
                if widget_type == "combo":
                    w = ttk.Combobox(parent, textvariable=var, values=combo_values or [],
                                     width=30, state="readonly")
                else:
                    w = ttk.Entry(parent, textvariable=var, width=32)
                w.grid(row=row, column=1, sticky="ew", padx=8, pady=2)
                self._var_widgets[prop_name] = var
                row += 1
            parent.grid_columnconfigure(1, weight=1)

        # Raw XML preview
        row += 1
        ttk.Label(parent, text="Raw XML", style="Title.TLabel").grid(
            row=row, column=0, columnspan=2, sticky="w", padx=8, pady=(12, 4))
        row += 1
        self.raw_xml_text = scrolledtext.ScrolledText(
            parent, height=12, bg=STYLE["entry_bg"], fg=STYLE["text"],
            font=("Consolas", 9), wrap="none", state="disabled",
            insertbackground=STYLE["text"], selectbackground=STYLE["accent"],
            selectforeground="#ffffff", borderwidth=0
        )
        self.raw_xml_text.grid(row=row, column=0, columnspan=2, sticky="nsew", padx=8, pady=(0, 12))
        parent.grid_rowconfigure(row, weight=1)

        row += 1
        ttk.Button(parent, text="Apply Form Values to XML", style="Accent.TButton",
                   command=self._apply_form_to_template).grid(
            row=row, column=0, columnspan=2, pady=8)

    # ── Template list / import dialog ──────────────────────────────────

    def _refresh_template_list(self):
        if not self.project or not self.project.is_loaded:
            self.combo_templates["values"] = []
            return
        templates = self.project.list_files("simulation/templates")
        names = [str(f.relative_to(self.project.mod_dir)).replace(os.sep, "/")
                 for f in templates if f.suffix == ".xml"]
        self.combo_templates["values"] = names

    def _import_template_dialog(self):
        if not self.project or not self.project.is_loaded:
            messagebox.showwarning("No Mod", "Create or open a mod first.")
            return
        if not self.asset_source:
            messagebox.showwarning("No Game Data", "Set the game data folder.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Import Unit Template from Game")
        dialog.geometry("500x500")
        dialog.configure(bg=STYLE["bg"])
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Search unit templates:", style="Title.TLabel").pack(pady=8)

        search_var = tk.StringVar()
        search_var.trace_add("write", lambda *_: self._update_import_list(dialog, search_var))
        ttk.Entry(dialog, textvariable=search_var, width=40).pack(pady=4)

        listbox = tk.Listbox(dialog, bg=STYLE["entry_bg"], fg=STYLE["text"],
                             font=("Consolas", 9), selectbackground=STYLE["accent"],
                             selectforeground="#ffffff", borderwidth=0, height=20)
        listbox.pack(fill="both", expand=True, padx=12, pady=8)
        dialog._listbox = listbox
        dialog._templates_cache = self.asset_source.list_unit_templates()

        def do_import():
            sel = listbox.curselection()
            if not sel:
                return
            src = dialog._templates_cache[sel[0]]
            try:
                rel = self.project.import_from_local(src, self.asset_source)
                messagebox.showinfo("Import", f"Imported: {rel}")
                self._refresh_template_list()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(dialog, text="Import Selected", style="Accent.TButton",
                   command=do_import).pack(pady=8)
        self._update_import_list(dialog, search_var)

    def _update_import_list(self, dialog, search_var):
        q = search_var.get().strip().lower()
        templates = dialog._templates_cache
        dialog._listbox.delete(0, "end")
        for t in templates:
            name = str(t.relative_to(self.asset_source.root)).replace(os.sep, "/")
            if q and q not in name.lower():
                continue
            dialog._listbox.insert("end", name)

    # ── Template selection & form loading ───────────────────────────────

    def _on_template_select(self, event):
        name = self.var_selected_template.get()
        if not name:
            return
        filepath = self.project.mod_dir / name
        if not filepath.is_file():
            return
        try:
            self.current_template = UnitTemplate.from_file(filepath)
            self.current_template_path = filepath
            self._load_template_into_form()
        except ET.ParseError as e:
            messagebox.showerror("XML Error", str(e))

    def _load_template_into_form(self):
        tpl = self.current_template
        if not tpl:
            return
        props = [
            "parent_template", "civ", "generic_name", "specific_name",
            "visible_classes", "icon", "max_health",
            "food_cost", "wood_cost", "stone_cost", "metal_cost",
            "walk_speed", "run_speed",
            "hack_armor", "pierce_armor",
            "melee_hack", "melee_pierce", "melee_crush", "melee_range",
            "ranged_pierce", "ranged_hack", "ranged_crush", "ranged_range", "ranged_repeat",
            "actor",
        ]
        for prop in props:
            if prop in self._var_widgets:
                val = getattr(tpl, prop)
                self._var_widgets[prop].set(str(val) if val is not None else "")

        self.raw_xml_text.config(state="normal")
        self.raw_xml_text.delete("1.0", "end")
        self.raw_xml_text.insert("1.0", tpl.to_string())
        self.raw_xml_text.config(state="disabled")

    def _apply_form_to_template(self):
        tpl = self.current_template
        if not tpl:
            messagebox.showwarning("No Template", "Select or import a template first.")
            return

        mapping = {
            "parent_template": "parent_template", "civ": "civ",
            "generic_name": "generic_name", "specific_name": "specific_name",
            "visible_classes": "visible_classes", "icon": "icon",
            "max_health": "max_health",
            "food_cost": "food_cost", "wood_cost": "wood_cost",
            "stone_cost": "stone_cost", "metal_cost": "metal_cost",
            "walk_speed": "walk_speed", "run_speed": "run_speed",
            "hack_armor": "hack_armor", "pierce_armor": "pierce_armor",
            "melee_hack": "melee_hack", "melee_pierce": "melee_pierce",
            "melee_crush": "melee_crush", "melee_range": "melee_range",
            "ranged_pierce": "ranged_pierce", "ranged_hack": "ranged_hack",
            "ranged_crush": "ranged_crush", "ranged_range": "ranged_range",
            "ranged_repeat": "ranged_repeat",
            "actor": "actor",
        }

        for var_key, prop_name in mapping.items():
            val = self._var_widgets[var_key].get()
            if val:
                setattr(tpl, prop_name, val)

        self.raw_xml_text.config(state="normal")
        self.raw_xml_text.delete("1.0", "end")
        self.raw_xml_text.insert("1.0", tpl.to_string())
        self.raw_xml_text.config(state="disabled")

        messagebox.showinfo("Applied", "Form values applied to XML.\nClick Save to write to disk.")

    def _save_current_template(self):
        if not self.current_template or not self.current_template_path:
            messagebox.showwarning("No Template", "Nothing to save.")
            return
        self.current_template.save(self.current_template_path)
        messagebox.showinfo("Saved", f"Saved: {self.current_template_path}")