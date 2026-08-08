"""Asset Browser tab — mixin for ModMakerGUI."""

import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from pathlib import Path
from typing import Optional

from constants import STYLE

class AssetBrowserMixin:
    """Provides the Asset Browser tab: tree view + file preview + import."""

    def _build_tab_assets(self):
        frame = self.tab_assets

        # Enhanced toolbar with better spacing
        toolbar = ttk.Frame(frame, padding=(12, 8), style="Panel.TFrame")
        toolbar.pack(fill="x")

        # Search section
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side="left", padx=(0, 16))
        
        ttk.Label(search_frame, text="🔍", style="TLabel").pack(side="left", padx=(0, 4))
        self.var_filter = tk.StringVar()
        self.var_filter.trace_add("write", self._on_filter_change)
        filter_entry = ttk.Entry(search_frame, textvariable=self.var_filter, width=35)
        filter_entry.pack(side="left")

        # Quick navigation buttons
        nav_frame = ttk.Frame(toolbar)
        nav_frame.pack(side="left", padx=(0, 16))
        
        ttk.Button(nav_frame, text="📄 Templates",
                   command=lambda: self._navigate_to("simulation/templates")).pack(side="left", padx=2)
        ttk.Button(nav_frame, text="🎨 Meshes",
                   command=lambda: self._navigate_to("art/meshes")).pack(side="left", padx=2)
        ttk.Button(nav_frame, text="🖼️ Textures",
                   command=lambda: self._navigate_to("art/textures")).pack(side="left", padx=2)
        ttk.Button(nav_frame, text="🎭 Actors",
                   command=lambda: self._navigate_to("art/actors")).pack(side="left", padx=2)

        # Action buttons
        action_frame = ttk.Frame(toolbar)
        action_frame.pack(side="right")
        
        ttk.Button(action_frame, text="📥 Import", style="Accent.TButton",
                   command=self._import_selected).pack(side="left", padx=2)
        ttk.Button(action_frame, text="✏️ Edit",
                   command=self._edit_selected_file).pack(side="left", padx=2)
        ttk.Button(action_frame, text="🔄 Reload",
                   command=self._reload_tree).pack(side="left", padx=2)

        # Enhanced status bar
        status_frame = ttk.Frame(frame, padding=(12, 6))
        status_frame.pack(fill="x")
        
        self.browser_status = ttk.Label(status_frame, text="Ready", style="Dim.TLabel")
        self.browser_status.pack(side="left")
        
        self.browser_count = ttk.Label(status_frame, text="0 items", style="Muted.TLabel")
        self.browser_count.pack(side="right")

        # Split: tree (left) + preview/editor (right)
        paned = ttk.PanedWindow(frame, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=12, pady=8)

        # Tree panel
        tree_frame = ttk.Frame(paned)
        paned.add(tree_frame, weight=3)

        self.asset_tree = ttk.Treeview(tree_frame, columns=("type", "size"),
                                       show="tree headings", selectmode="extended")
        self.asset_tree.heading("#0", text="Name")
        self.asset_tree.heading("type", text="Type")
        self.asset_tree.heading("size", text="Size")
        self.asset_tree.column("#0", width=300)
        self.asset_tree.column("type", width=60, anchor="center")
        self.asset_tree.column("size", width=80, anchor="e")

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical",
                                    command=self.asset_tree.yview)
        self.asset_tree.configure(yscrollcommand=tree_scroll.set)
        self.asset_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        self.asset_tree.bind("<<TreeviewOpen>>", self._on_tree_expand)
        self.asset_tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.asset_tree.bind("<Double-1>", self._on_tree_double_click)
        self.asset_tree.bind("<Button-3>", self._on_tree_right_click)

        # Preview/editor panel
        preview_frame = ttk.Frame(paned)
        paned.add(preview_frame, weight=2)

        preview_toolbar = ttk.Frame(preview_frame)
        preview_toolbar.pack(fill="x", padx=4, pady=4)
        ttk.Label(preview_toolbar, text="Preview/Edit", style="Header.TLabel").pack(side="left")
        self.btn_save_preview = ttk.Button(preview_toolbar, text="Save Changes",
                                           command=self._save_preview_changes, state="disabled")
        self.btn_save_preview.pack(side="right", padx=4)

        self.preview_text = scrolledtext.ScrolledText(
            preview_frame, bg=STYLE["entry_bg"], fg=STYLE["text"],
            font=("Consolas", 9), wrap="none", state="disabled",
            insertbackground=STYLE["accent"], selectbackground=STYLE["accent"],
            selectforeground="#ffffff", borderwidth=2, relief="solid"
        )
        self.preview_text.pack(fill="both", expand=True, padx=4, pady=(0, 4))

        # Track what file is currently being viewed
        self._current_view_path = None
        self._was_modified = False

    # ── Tree population with folder filtering ───────────────────────────

    def _populate_asset_tree(self, rel_path: str, parent_id: str = ""):
        if not self.asset_source:
            return

        entries = self.asset_source.list_dir(rel_path)
        filter_text = self.var_filter.get().strip().lower()

        for entry in entries:
            name_lower = entry["name"].lower()
            
            # Apply filter (matches files OR folders)
            if filter_text and filter_text not in name_lower:
                continue

            eid = f"{parent_id}/{entry['name']}" if parent_id else entry["name"]
            if entry["type"] == "dir":
                self.asset_tree.insert(parent_id, "end", iid=eid,
                                       text=f"📁 {entry['name']}",
                                       values=("dir", ""), open=False)
                # Don't add dummy for dirs — we'll populate on expand
            else:
                size_str = self._fmt_size(entry["size"])
                ext = entry["name"].rsplit(".", 1)[-1].lower() if "." in entry["name"] else ""
                icon = "📄"
                if ext in ("xml", "json"): icon = "📋"
                elif ext in ("png", "dds", "tga", "jpg"): icon = "🖼️"
                elif ext in ("dae", "pmd", "psa"): icon = "📦"
                elif ext in ("ogg", "mp3", "wav"): icon = "🎵"
                self.asset_tree.insert(parent_id, "end", iid=eid,
                                       text=f"{icon} {entry['name']}",
                                       values=(ext, size_str), open=False)

        self.browser_status.config(text=f"Showing: {rel_path or '(root)'} ({len(entries)} items)")

    def _reload_tree(self):
        """Re-populate the entire tree."""
        for item in self.asset_tree.get_children(""):
            self.asset_tree.delete(item)
        self._populate_asset_tree("")
    
    def _navigate_to(self, path: str):
        """Navigate to a specific path in the asset tree."""
        if not self.asset_source:
            return
        
        # Clear current tree
        for item in self.asset_tree.get_children(""):
            self.asset_tree.delete(item)
        
        # Populate with the target path
        self._populate_asset_tree(path)
        self.browser_status.config(text=f"Navigated to: {path}")

    def _on_tree_expand(self, event):
        node = self.asset_tree.focus()
        if not node:
            return
        rel_path = node  # Keep forward slashes
        for child in self.asset_tree.get_children(node):
            self.asset_tree.delete(child)
        self._populate_asset_tree(rel_path, node)

    def _on_tree_select(self, event):
        node = self.asset_tree.focus()
        if not node:
            return
        values = self.asset_tree.item(node, "values")
        if values and values[0] != "dir" and values[0] != "":
            self._preview_file(node, editable=True)

    def _on_tree_double_click(self, event):
        node = self.asset_tree.focus()
        if not node:
            return
        values = self.asset_tree.item(node, "values")
        if values and values[0] != "dir" and values[0] != "":
            self._preview_file(node, editable=True)

    def _on_tree_right_click(self, event):
        node = self.asset_tree.identify_row(event.y)
        if not node:
            return
        self.asset_tree.selection_set(node)
        values = self.asset_tree.item(node, "values")

        menu = tk.Menu(self.asset_tree, tearoff=0, bg=STYLE["panel"], fg=STYLE["text"],
                       activebackground=STYLE["accent"], activeforeground="#ffffff")
        
        if values and values[0] != "dir" and values[0] != "":
            menu.add_command(label="Preview/Edit", command=lambda: self._preview_file(node, editable=True))
            menu.add_command(label="Import to Mod", command=self._import_selected)
            if self.project and self.project.is_loaded:
                menu.add_command(label="Delete from Mod", command=lambda: self._delete_from_mod(node))
        else:
            menu.add_command(label="Browse Subfolder", command=lambda: self._browse_folder(node))

        menu.tk_popup(event.x_root, event.y_root)

    def _browse_folder(self, folder_node: str):
        """Navigate into a folder (for right-click context menu)."""
        for item in self.asset_tree.get_children(folder_node):
            self.asset_tree.delete(item)
        self.asset_tree.item(folder_node, open=True)
        self._populate_asset_tree(folder_node, folder_node)

    def _preview_file(self, rel_path_id: str, editable: bool = False):
        """Read and display a file in the preview pane."""
        if not self.asset_source:
            return

        self._current_view_path = rel_path_id

        content = self.asset_source.read_text(rel_path_id)
        if content is None:
            content = "(Binary file — cannot preview as text)"

        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", "end")
        self.preview_text.tag_configure("modified", background="#3a3a5c", foreground="#ffffff")
        self.preview_text.insert("1.0", content[:100000])
        
        # Enable editing if it's a text file
        is_editable = content != "(Binary file — cannot preview as text)"
        is_xml_or_json = rel_path_id.endswith((".xml", ".json"))
        
        if editable and is_editable and is_xml_or_json:
            self.preview_text.config(state="normal")
            self.btn_save_preview.config(state="normal")
            self._was_modified = False
        else:
            self.preview_text.config(state="disabled")
            self.btn_save_preview.config(state="disabled")
            self._was_modified = False

    def _save_preview_changes(self):
        """Save edited content back to the asset source (if it's our mod)."""
        if not self._current_view_path:
            return
        
        if not self.project:
            messagebox.showwarning("No Mod", "Create or open a mod first.")
            return

        # Only save files that belong to the mod
        content = self.preview_text.get("1.0", "end")
        rel_path = self._current_view_path
        
        try:
            self.project.add_file(rel_path, content)
            self._was_modified = False
            self.browser_status.config(text=f"Saved: {rel_path}")
            messagebox.showinfo("Saved", f"Changes saved to {rel_path}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def _import_selected(self):
        if not self.project or not self.project.is_loaded:
            messagebox.showwarning("No Mod", "Create or open a mod first.")
            return
        if not self.asset_source:
            messagebox.showwarning("No Game Data", "Set the game data folder first.")
            return

        selected = self.asset_tree.selection()
        if not selected:
            messagebox.showinfo("Import", "Select file(s) in the tree first.")
            return

        imported = 0
        for node_id in selected:
            values = self.asset_tree.item(node_id, "values")
            if not values or values[0] == "dir":
                continue
            
            try:
                if self.asset_source.is_zip:
                    data = self.asset_source.read_bytes(node_id)
                    if data is not None:
                        self.project.add_file(node_id, data)
                        imported += 1
                else:
                    src = self.asset_source.root / node_id
                    if src and src.is_file():
                        self.project.import_from_local(src, self.asset_source)
                        imported += 1
            except Exception as e:
                messagebox.showerror("Import Error", f"{node_id}: {e}")

        if imported:
            self.browser_status.config(text=f"Imported {imported} file(s)")
            self._refresh_template_list()
            self._refresh_summary()
        else:
            messagebox.showinfo("Import", "No files were imported.")

    def _delete_from_mod(self, node_id: str):
        if not self.project:
            return
        
        rel_path = node_id
        if messagebox.askyesno("Delete", f"Delete {rel_path} from mod?"):
            self.project.delete_file(rel_path)
            self._refresh_summary()
            self._refresh_template_list()
            self.browser_status.config(text=f"Deleted: {rel_path}")

    @staticmethod
    def _fmt_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _edit_selected_file(self):
        """Trigger edit mode on selected file."""
        node = self.asset_tree.focus()
        if node:
            self._preview_file(node, editable=True)

    def _on_filter_change(self, *args):
        """Repopulate tree when filter changes."""
        for item in self.asset_tree.get_children(""):
            self.asset_tree.delete(item)
        self._populate_asset_tree("")