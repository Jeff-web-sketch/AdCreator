"""Recent Projects tab — shows recently opened mods with quick load."""

import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

from constants import STYLE
from mod_project import ModProject

class RecentProjectsMixin:
    """Provides the Recent Projects tab."""

    def _build_tab_recent(self):
        frame = self.tab_recent

        # Enhanced header
        header_frame = ttk.Frame(frame, padding=(16, 12))
        header_frame.pack(fill="x")
        
        ttk.Label(header_frame, text="🕒 Recent Projects", style="Title.TLabel").pack(side="left")
        ttk.Label(header_frame, text="Quickly access your recently worked-on mods", 
                 style="Dim.TLabel").pack(side="left", padx=(12, 0))

        # Toolbar
        toolbar = ttk.Frame(frame, padding=(12, 8), style="Panel.TFrame")
        toolbar.pack(fill="x")
        
        ttk.Button(toolbar, text="🔄 Refresh", command=self._refresh_recent_list).pack(side="left", padx=2)
        ttk.Button(toolbar, text="🗑️ Clear All",
                   command=self._clear_all_recent).pack(side="right", padx=2)

        # Enhanced treeview with card styling
        tree_card = ttk.Frame(frame, style="Card.TFrame", padding=16, relief="raised", borderwidth=2)
        tree_card.pack(fill="both", expand=True, padx=12, pady=8)
        
        cols = ("label", "path", "opened")
        self.recent_tree = ttk.Treeview(tree_card, columns=cols, show="headings", selectmode="browse")
        self.recent_tree.heading("label", text="📁 Mod Name")
        self.recent_tree.heading("path", text="📍 Location")
        self.recent_tree.heading("opened", text="📅 Last Opened")
        self.recent_tree.column("label", width=200)
        self.recent_tree.column("path", width=400)
        self.recent_tree.column("opened", width=140)

        scroll = ttk.Scrollbar(tree_card, orient="vertical", command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=scroll.set)
        self.recent_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Double-click to load
        self.recent_tree.bind("<Double-1>", self._on_recent_double_click)
        self.recent_tree.bind("<Button-3>", self._on_recent_right_click)

        # Action buttons
        btn_frame = ttk.Frame(frame, padding=(12, 8))
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="📂 Load Selected", style="Accent.TButton",
                   command=self._load_recent_selected).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="🔍 Locate Missing",
                   command=self._locate_missing_selected).pack(side="left", padx=8)

        self._refresh_recent_list()

    def _refresh_recent_list(self):
        """Populate recent projects tree from settings."""
        for item in self.recent_tree.get_children():
            self.recent_tree.delete(item)

        for entry in self.settings.recent_projects:
            # Check if path exists
            path = entry.get("path", "")
            exists = Path(path).is_dir() and (Path(path) / "mod.json").exists()

            timestamp = entry.get("timestamp", 0)
            date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp)) if timestamp > 0 else "Unknown"

            iid = path
            self.recent_tree.insert("", "end", iid=iid, values=(
                entry.get("label", "Unknown"),
                path,
                date_str
            ))
            # Gray out if missing
            if not exists:
                self.recent_tree.item(iid, tags=("missing",))
        self.recent_tree.tag_configure("missing", foreground=STYLE["text_dim"])

    def _on_recent_double_click(self, event):
        sel = self.recent_tree.selection()
        if sel:
            self._load_recent_by_path(sel[0])

    def _on_recent_right_click(self, event):
        sel = self.recent_tree.identify_row(event.y)
        if not sel:
            return
        self.recent_tree.selection_set(sel)

        menu = tk.Menu(self.root, tearoff=0, bg=STYLE["panel"], fg=STYLE["text"],
                       activebackground=STYLE["accent"], activeforeground="#ffffff")
        menu.add_command(label="Load", command=self._load_recent_selected)
        menu.add_command(label="Remove from List", command=lambda: self._remove_from_recent(sel))
        menu.tk_popup(event.x_root, event.y_root)

    def _load_recent_selected(self):
        sel = self.recent_tree.selection()
        if sel:
            self._load_recent_by_path(sel[0])

    def _load_recent_by_path(self, path):
        """Load a mod from a known path."""
        try:
            if not Path(path).is_dir():
                self._locate_missing_after_load(path)
                return
            
            self.project = ModProject.load(Path(path))
            self.settings.last_mod_dir = str(self.project.mod_dir)
            self.settings.add_recent(str(self.project.mod_dir), self.project.info.label)
            self.settings.save()
            self._update_status_bar()
            self._refresh_template_list()
            self._load_mod_info_into_form()
            self._refresh_summary()
            messagebox.showinfo("Loaded", f"Mod '{self.project.info.label}' loaded successfully.")
        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e))

    def _locate_missing_after_load(self, path):
        """Offer to locate a missing mod."""
        result = messagebox.askyesno(
            "Missing",
            f"This mod was previously at:\n{path}\n\nBut the path no longer exists.\n\n"
            f"Do you want to locate it now?"
        )
        
        if result:
            new_path = filedialog.askdirectory(
                title="Locate the mod",
                initialdir=path
            )
            
            if new_path:
                try:
                    self.project = ModProject.load(Path(new_path))
                    # Update recent list entry
                    self.settings.remove_recent(path)
                    self.settings.add_recent(str(self.project.mod_dir), self.project.info.label)
                    self.settings.save()
                    self._update_status_bar()
                    self._refresh_template_list()
                    self._load_mod_info_into_form()
                    self._refresh_summary()
                    self._refresh_recent_list()
                    messagebox.showinfo("Loaded", f"Mod located and loaded successfully!")
                except FileNotFoundError as e:
                    messagebox.showerror("Error", str(e))

    def _locate_missing_selected(self):
        """For when user clicks 'Locate Missing' button."""
        sel = self.recent_tree.selection()
        if sel:
            self._locate_missing_after_load(sel[0])

    def _remove_from_recent(self, path):
        self.settings.remove_recent(path)
        self._refresh_recent_list()

    def _clear_all_recent(self):
        if messagebox.askyesno("Clear", "Remove all entries from recent projects list?"):
            self.settings.data["recent_projects"] = []
            self.settings.save()
            self._refresh_recent_list()