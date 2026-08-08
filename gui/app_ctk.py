"""Main GUI application using CustomTkinter for modern styling."""

import os
import sys
import logging
import customtkinter as ctk
from tkinter import messagebox, filedialog
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

from constants import STYLE
from settings import AppSettings
from game_data import GameDataLocator
from asset_source import LocalAssetSource
from mod_project import ModProject
from unit_template import UnitTemplate
from gui.tab_assets import AssetBrowserMixin
from gui.tab_units import UnitEditorMixin
from gui.tab_new_unit import NewUnitMixin
from gui.tab_modinfo import ModInfoMixin
from gui.tab_summary import SummaryMixin
from gui.tab_recent import RecentProjectsMixin

class WindowDefaults:
    """Default window dimensions and constraints."""
    MIN_WIDTH = 900
    MIN_HEIGHT = 600
    DEFAULT_WIDTH = 1100
    DEFAULT_HEIGHT = 720

class ModMakerGUI(AssetBrowserMixin, UnitEditorMixin, NewUnitMixin,
                  ModInfoMixin, SummaryMixin, RecentProjectsMixin):
    """Main GUI application for the 0 A.D. Mod Maker using CustomTkinter."""

    def __init__(self, root: ctk.CTk):
        self.root = root
        self.settings = AppSettings()
        self.asset_source: Optional[LocalAssetSource] = None
        self.project: Optional[ModProject] = None
        self.current_template: Optional[UnitTemplate] = None
        self.current_template_path: Optional[Path] = None
        self._var_widgets = {}

        self._setup_window()
        self._setup_appearance()
        self._build_layout()
        self._auto_detect_game()

        # Save settings when the window closes
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_window(self):
        self.root.title("0 A.D. Mod Maker")
        w = self.settings.get("window_width", WindowDefaults.DEFAULT_WIDTH)
        h = self.settings.get("window_height", WindowDefaults.DEFAULT_HEIGHT)
        self.root.geometry(f"{w}x{h}")
        self.root.minsize(WindowDefaults.MIN_WIDTH, WindowDefaults.MIN_HEIGHT)

    def _setup_appearance(self):
        """Setup CustomTkinter appearance theme."""
        ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

    def _build_layout(self):
        # Status bar with CustomTkinter
        status_frame = ctk.CTkFrame(self.root, height=50, corner_radius=0)
        status_frame.pack(fill="x", side="bottom")

        self.lbl_game_status = ctk.CTkLabel(status_frame, text="🔍 Detecting 0 A.D.…",
                                           font=("Segoe UI", 12))
        self.lbl_game_status.pack(side="left", padx=20, pady=10)
        
        self.lbl_mod_status = ctk.CTkLabel(status_frame, text="No mod loaded",
                                          font=("Segoe UI", 12))
        self.lbl_mod_status.pack(side="right", padx=20, pady=10)

        # Tabview using CustomTkinter
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_assets = self.tabview.add("Assets")
        self.tab_units = self.tabview.add("Units")
        self.tab_new_unit = self.tabview.add("New Unit")
        self.tab_modinfo = self.tabview.add("Settings")
        self.tab_summary = self.tabview.add("Overview")
        self.tab_recent = self.tabview.add("Recent")

        self._build_tab_assets()
        self._build_tab_units()
        self._build_tab_new_unit()
        self._build_tab_modinfo()
        self._build_tab_summary()
        self._build_tab_recent()

    def _auto_detect_game(self):
        result = GameDataLocator.find_public_folder()
        if result:
            path, is_zip = result
            self._set_asset_source(path, is_zip=is_zip)
            self.settings.game_data_path = str(path)
            self.settings.game_data_is_zip = is_zip
            self.settings.save()
            
            source_type = "ZIP archive" if is_zip else "folder"
            self.lbl_game_status.configure(text=f"🎮 0 A.D. detected ({source_type})",
                                        text_color="#4ade80")
        else:
            self.lbl_game_status.configure(text="⚠️ 0 A.D. not found — Set game data folder",
                                        text_color="#fbbf24")

    def _set_asset_source(self, path: Path, is_zip: bool):
        try:
            self.asset_source = LocalAssetSource(path, is_zip=is_zip)
            if is_zip:
                self.lbl_game_status.configure(text=f"🎮 0 A.D. loaded: {path.name} (ZIP)",
                                            text_color="#4ade80")
            else:
                try:
                    install_dir = path.parent.parent.parent.parent
                except Exception as e:
                    logger.warning(f"Error navigating path hierarchy: {e}")
                    install_dir = path
                self.lbl_game_status.configure(text=f"🎮 0 A.D. loaded: {install_dir.name}",
                                            text_color="#4ade80")
            self._populate_asset_tree("")

            self.settings.game_data_path = str(path)
            self.settings.game_data_is_zip = is_zip
            self.settings.save()
        except FileNotFoundError as e:
            messagebox.showerror("Error", f"Failed to load game data: {e}")

    def _update_status_bar(self):
        if self.project and self.project.is_loaded:
            status_text = f"✅ {self.project.info.label} v{self.project.info.version}"
            self.lbl_mod_status.configure(text=status_text, text_color="#4ade80")
        else:
            self.lbl_mod_status.configure(text="⚪ No mod loaded", text_color="#a0a0b0")

    def _on_close(self):
        """Save settings and quit."""
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        if width >= WindowDefaults.MIN_WIDTH and height >= WindowDefaults.MIN_HEIGHT:
            self.settings.set("window_width", width)
            self.settings.set("window_height", height)
        
        self.settings.save()
        
        if hasattr(self, 'asset_source') and self.asset_source:
            try:
                self.asset_source.__del__()
            except:
                pass
        
        self.root.destroy()

    # Placeholder methods for tab mixins that need updating
    def _populate_asset_tree(self, rel_path: str):
        pass
        
    def _refresh_template_list(self):
        pass
        
    def _load_mod_info_into_form(self):
        pass
        
    def _refresh_summary(self):
        pass

    # Action methods
    def action_new_mod(self, *_):
        messagebox.showinfo("Info", "New Mod functionality - to be implemented with CustomTkinter")

    def action_open_mod(self, *_):
        messagebox.showinfo("Info", "Open Mod functionality - to be implemented with CustomTkinter")

    def action_show_recent(self, *_):
        messagebox.showinfo("Info", "Recent Projects functionality - to be implemented with CustomTkinter")

    def action_set_game_folder(self, *_):
        messagebox.showinfo("Info", "Set Game Folder functionality - to be implemented with CustomTkinter")

    def action_build(self, *_):
        messagebox.showinfo("Info", "Build functionality - to be implemented with CustomTkinter")

    def action_about(self, *_):
        messagebox.showinfo("About", "0 A.D. Mod Maker\n\nBuilt with CustomTkinter for modern UI")

    def _load_pyromod_dialog(self):
        messagebox.showinfo("Info", "Load Pyromod functionality - to be implemented with CustomTkinter")


def run():
    """Entry point for the GUI application."""
    root = ctk.CTk()
    app = ModMakerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run()