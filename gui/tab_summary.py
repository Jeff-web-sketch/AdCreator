"""Summary tab — mixin for ModMakerGUI."""

import os
import zipfile
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

from constants import STYLE
from game_data import GameDataLocator

class SummaryMixin:
    """Provides the Summary tab: list all mod files + delete + build."""

    def _build_tab_summary(self):
        frame = self.tab_summary

        toolbar = ttk.Frame(frame, padding=(8, 8))
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="Refresh", command=self._refresh_summary).pack(side="left")
        ttk.Button(toolbar, text="Build .pyromod", style="Accent.TButton",
                   command=self.action_build).pack(side="right", padx=(0, 8))
        ttk.Button(toolbar, text="Load .pyromod",
                   command=self._load_pyromod_dialog).pack(side="right")

        self.summary_tree = ttk.Treeview(frame, columns=("path",),
                                         show="headings", selectmode="browse")
        self.summary_tree.heading("path", text="File Path")
        self.summary_tree.column("path", width=700)

        sscroll = ttk.Scrollbar(frame, orient="vertical",
                                command=self.summary_tree.yview)
        self.summary_tree.configure(yscrollcommand=sscroll.set)
        self.summary_tree.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        sscroll.pack(side="right", fill="y", pady=8)

        self.summary_tree.bind("<Double-1>", self._on_summary_double_click)
        self.summary_tree.bind("<Button-3>", self._on_summary_right_click)

    def _load_pyromod_dialog(self):
        """Allow user to load a .pyromod file directly."""
        path = filedialog.askopenfilename(
            title="Load .pyromod file",
            filetypes=[("PyroMod files", "*.pyromod"), ("ZIP files", "*.zip")]
        )
        if not path:
            return

        try:
            pyromod_path = Path(path)
            
            # Create temporary extraction dir
            temp_dir = GameDataLocator.get_user_mods_dir() / "temp_loaded_pyromod"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract to temp
            with zipfile.ZipFile(pyromod_path, 'r') as zf:
                zf.extractall(temp_dir)
            
            # Load as normal mod
            self.project = ModProject.load(temp_dir)
            self.settings.last_mod_dir = str(self.project.mod_dir)
            self.settings.add_recent(str(self.project.mod_dir), self.project.info.label)
            self.settings.save()
            self._update_status_bar()
            self._refresh_template_list()
            self._load_mod_info_into_form()
            self._refresh_summary()
            
            # Also refresh asset browser to show mod's own assets
            self._populate_mod_asset_tree()
            
            messagebox.showinfo(
                "Loaded",
                f"Loaded .pyromod file!\n\n"
                f"Mod: {self.project.info.label}\n"
                f"Files extracted to temp location."
            )
            
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def _populate_mod_asset_tree(self):
        """Show the loaded mod's own assets in the asset browser."""
        if not self.project or not self.asset_source:
            return
        
        # Temporarily switch asset_source to mod directory
        old_source = self.asset_source
        from asset_source import LocalAssetSource
        self.asset_source = LocalAssetSource(self.project.mod_dir, is_zip=False)
        
        # Refresh tree
        for item in self.asset_tree.get_children(""):
            self.asset_tree.delete(item)
        self._populate_asset_tree("")
        
        self.browser_status.config(text="Browsing mod assets (switched from game data)")
        
        # Restore original after brief delay (or provide toggle)
        # For now, user can use "Reload" button to switch back

    def _refresh_summary(self):
        for item in self.summary_tree.get_children():
            self.summary_tree.delete(item)
        if not self.project or not self.project.is_loaded:
            return
        files = self.project.list_files()
        for f in files:
            rel = str(f.relative_to(self.project.mod_dir)).replace(os.sep, "/")
            self.summary_tree.insert("", "end", iid=rel, values=(rel,))

    def _on_summary_double_click(self, event):
        sel = self.summary_tree.selection()
        if not sel:
            return
        rel = sel[0]
        filepath = self.project.mod_dir / rel
        if filepath.suffix == ".xml":
            self.var_selected_template.set(rel)
            self._on_template_select(None)
            self.notebook.select(self.tab_units)

    def _on_summary_right_click(self, event):
        sel = self.summary_tree.identify_row(event.y)
        if not sel:
            return
        self.summary_tree.selection_set(sel)

        menu = tk.Menu(self.root, tearoff=0, bg=STYLE["panel"], fg=STYLE["text"],
                       activebackground=STYLE["accent"], activeforeground="#ffffff")
        menu.add_command(label="Delete File", command=lambda: self._delete_file(sel))
        menu.tk_popup(event.x_root, event.y_root)

    def _delete_file(self, rel_path: str):
        if messagebox.askyesno("Delete", f"Delete {rel_path}?"):
            self.project.delete_file(rel_path)
            self._refresh_summary()
            self._refresh_template_list()