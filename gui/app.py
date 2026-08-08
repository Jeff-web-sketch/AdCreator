"""Main GUI application — combines all tab mixins into one window."""

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
    """Main GUI application for the 0 A.D. Mod Maker."""

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

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Base styles
        style.configure(".", background=STYLE["bg"], foreground=STYLE["text"],
                        font=("Segoe UI", 11))
        style.configure("TFrame", background=STYLE["bg"])
        style.configure("Panel.TFrame", background=STYLE["panel"], relief="raised", borderwidth=1)
        style.configure("Card.TFrame", background=STYLE["card"], relief="raised", borderwidth=2)
        
        # Label styles with improved typography
        style.configure("TLabel", background=STYLE["bg"], foreground=STYLE["text"],
                        font=("Segoe UI", 11))
        style.configure("Dim.TLabel", background=STYLE["bg"], foreground=STYLE["text_dim"],
                        font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=STYLE["bg"], foreground=STYLE["text_muted"],
                        font=("Segoe UI", 9))
        style.configure("Title.TLabel", background=STYLE["bg"], foreground=STYLE["accent"],
                         font=("Segoe UI", 18, "bold"))
        style.configure("Subtitle.TLabel", background=STYLE["bg"], foreground=STYLE["text"],
                         font=("Segoe UI", 14, "bold"))
        style.configure("Header.TLabel", background=STYLE["panel"], foreground=STYLE["text"],
                         font=("Segoe UI", 12, "bold"))
        style.configure("CardHeader.TLabel", background=STYLE["card"], foreground=STYLE["accent"],
                         font=("Segoe UI", 13, "bold"))
        
        # Button styles with high visibility
        style.configure("TButton", background=STYLE["panel_light"], foreground=STYLE["text"],
                         borderwidth=2, relief="raised", padding=(14, 8), font=("Segoe UI", 10, "bold"))
        style.map("TButton",
                  background=[("active", STYLE["accent"]), ("pressed", STYLE["accent_hover"])],
                  foreground=[("active", "#ffffff"), ("pressed", "#ffffff")])
        
        style.configure("Accent.TButton", background=STYLE["accent"], foreground="#ffffff",
                         font=("Segoe UI", 11, "bold"), padding=(18, 10), relief="raised",
                         borderwidth=2)
        style.map("Accent.TButton",
                  background=[("active", STYLE["accent_hover"]),
                              ("pressed", STYLE["accent_hover"])],
                  foreground=[("active", "#ffffff"), ("pressed", "#ffffff")])
        
        style.configure("Success.TButton", background=STYLE["success"], foreground="#1a1a2a",
                         font=("Segoe UI", 11, "bold"), padding=(18, 10), relief="raised",
                         borderwidth=2)
        style.configure("Warning.TButton", background=STYLE["warning"], foreground="#1a1a2a",
                         font=("Segoe UI", 11, "bold"), padding=(18, 10), relief="raised",
                         borderwidth=2)
        
        # Notebook (tab) styles
        style.configure("TNotebook", background=STYLE["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=STYLE["panel"],
                         foreground=STYLE["text_dim"], padding=(20, 12),
                         font=("Segoe UI", 11, "bold"), borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", STYLE["accent"])],
                  foreground=[("selected", "#ffffff")])
        
        # Entry and input styles with high visibility
        style.configure("TEntry", fieldbackground=STYLE["entry_bg"],
                         foreground=STYLE["text"], insertcolor=STYLE["accent"],
                         borderwidth=2, relief="solid", font=("Segoe UI", 11), padding=6)
        style.map("TEntry",
                  bordercolor=[("focus", STYLE["accent"])])
        
        style.configure("TCombobox", fieldbackground=STYLE["entry_bg"],
                         foreground=STYLE["text"], background=STYLE["panel_light"],
                         borderwidth=2, relief="solid", font=("Segoe UI", 11), padding=6)
        style.map("TCombobox",
                  fieldbackground=[("readonly", STYLE["entry_bg"])],
                  selectbackground=[("readonly", STYLE["accent"])],
                  selectforeground=[("readonly", "#ffffff")],
                  bordercolor=[("focus", STYLE["accent"])])
        
        # Treeview styles with high visibility
        style.configure("Treeview", background=STYLE["entry_bg"],
                         foreground=STYLE["text"], fieldbackground=STYLE["entry_bg"],
                         borderwidth=2, relief="solid", font=("Consolas", 10), rowheight=28)
        style.configure("Treeview.Heading", background=STYLE["panel"],
                         foreground=STYLE["text"], font=("Segoe UI", 10, "bold"),
                         borderwidth=1, relief="raised")
        style.map("Treeview",
                  background=[("selected", STYLE["accent"])],
                  foreground=[("selected", "#ffffff")])
        
        # Scrollbar styles
        style.configure("TScrollbar", background=STYLE["panel"], troughcolor=STYLE["bg"],
                         bordercolor=STYLE["bg"], arrowsize=16)
        style.map("TScrollbar",
                  background=[("active", STYLE["panel_light"])])
        
        # Text widget styles with high visibility
        style.configure("TText", background=STYLE["entry_bg"], foreground=STYLE["text"],
                         borderwidth=2, relief="solid", font=("Consolas", 11), padding=8, 
                         insertbackground=STYLE["accent"])
        style.map("TText",
                  bordercolor=[("focus", STYLE["accent"])])
        
        # Progress bar styles
        style.configure("TProgressbar", background=STYLE["accent"], troughcolor=STYLE["panel"],
                         borderwidth=0, thickness=8)
        
        # Separator styles
        style.configure("TSeparator", background=STYLE["divider"])

    def _build_menubar(self):
        menubar = tk.Menu(self.root, bg=STYLE["panel"], fg=STYLE["text"],
                          activebackground=STYLE["accent"], activeforeground="#ffffff",
                          borderwidth=0, font=("Segoe UI", 10))

        file_menu = tk.Menu(menubar, tearoff=0, bg=STYLE["panel"], fg=STYLE["text"],
                            activebackground=STYLE["accent"], activeforeground="#ffffff")
        file_menu.add_command(label="New Mod…", command=self.action_new_mod, accelerator="Ctrl+N")
        file_menu.add_command(label="Open Mod…", command=self.action_open_mod, accelerator="Ctrl+O")
        file_menu.add_command(label="Load Recent", command=self.action_show_recent, accelerator="Ctrl+R")
        file_menu.add_separator()
        file_menu.add_command(label="Load .pyromod…", command=self._load_pyromod_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Set Game Data Folder…", command=self.action_set_game_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Build .pyromod", command=self.action_build, accelerator="Ctrl+B")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0, bg=STYLE["panel"], fg=STYLE["text"],
                            activebackground=STYLE["accent"], activeforeground="#ffffff")
        help_menu.add_command(label="About", command=self.action_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)
        self.root.bind("<Control-n>", lambda e: self.action_new_mod())
        self.root.bind("<Control-o>", lambda e: self.action_open_mod())
        self.root.bind("<Control-r>", lambda e: self.action_show_recent())
        self.root.bind("<Control-b>", lambda e: self.action_build())

    def _build_layout(self):
        # Enhanced status bar with better styling
        status_frame = ttk.Frame(self.root, padding=(16, 10), style="Panel.TFrame")
        status_frame.pack(fill="x")

        # Game status with icon
        game_status_frame = ttk.Frame(status_frame)
        game_status_frame.pack(side="left")
        
        self.lbl_game_status = ttk.Label(game_status_frame, text="🔍 Detecting 0 A.D.…",
                                         style="Dim.TLabel", font=("Segoe UI", 10))
        self.lbl_game_status.pack(side="left", padx=(0, 4))
        
        # Separator
        ttk.Separator(status_frame, orient="vertical").pack(side="left", fill="y", padx=12)
        
        # Mod status
        mod_status_frame = ttk.Frame(status_frame)
        mod_status_frame.pack(side="left")
        
        self.lbl_mod_status = ttk.Label(mod_status_frame, text="No mod loaded",
                                        style="Dim.TLabel", font=("Segoe UI", 10))
        self.lbl_mod_status.pack(side="left")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.tab_assets = ttk.Frame(self.notebook)
        self.tab_units = ttk.Frame(self.notebook)
        self.tab_new_unit = ttk.Frame(self.notebook)
        self.tab_modinfo = ttk.Frame(self.notebook)
        self.tab_summary = ttk.Frame(self.notebook)
        self.tab_recent = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_assets, text="  � Assets  ")
        self.notebook.add(self.tab_units, text="  ⚔️ Units  ")
        self.notebook.add(self.tab_new_unit, text="  ✨ New Unit  ")
        self.notebook.add(self.tab_modinfo, text="  🔧 Settings  ")
        self.notebook.add(self.tab_summary, text="  � Overview  ")
        self.notebook.add(self.tab_recent, text="  � Recent  ")

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
            # Save for next time
            self.settings.game_data_path = str(path)
            self.settings.game_data_is_zip = is_zip
            self.settings.save()
            
            # Enhanced success status
            source_type = "ZIP archive" if is_zip else "folder"
            self.lbl_game_status.config(
                text=f"🎮 0 A.D. detected ({source_type})",
                foreground=STYLE["success"],
                font=("Segoe UI", 10, "bold"))
        else:
            self.lbl_game_status.config(
                text="⚠️ 0 A.D. not found — Set game data folder in File menu",
                foreground=STYLE["warning"],
                font=("Segoe UI", 10))

    def _set_asset_source(self, path: Path, is_zip: bool):
        try:
            self.asset_source = LocalAssetSource(path, is_zip=is_zip)
            if is_zip:
                self.lbl_game_status.config(
                    text=f"🎮 0 A.D. loaded: {path.name} (ZIP)",
                    foreground=STYLE["success"],
                    font=("Segoe UI", 10, "bold"))
            else:
                try:
                    install_dir = path.parent.parent.parent.parent
                except Exception:
                    install_dir = path
                self.lbl_game_status.config(
                    text=f"🎮 0 A.D. loaded: {install_dir.name}",
                    foreground=STYLE["success"],
                    font=("Segoe UI", 10, "bold"))
            self._populate_asset_tree("")

            self.settings.game_data_path = str(path)
            self.settings.game_data_is_zip = is_zip
            self.settings.save()

        except Exception as e:
            self.lbl_game_status.config(
                text=f"⚠ Error loading 0 A.D.: {e}",
                foreground=STYLE["error"])

    def _update_status_bar(self):
        if self.project and self.project.is_loaded:
            # Enhanced status with visual indicator
            status_text = f"✅ {self.project.info.label} v{self.project.info.version}"
            self.lbl_mod_status.config(
                text=status_text,
                foreground=STYLE["success"],
                font=("Segoe UI", 10, "bold"))
        else:
            self.lbl_mod_status.config(
                text="⚪ No mod loaded", 
                foreground=STYLE["text_dim"],
                font=("Segoe UI", 10))

    def action_new_mod(self, *_):
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Mod")
        dialog.geometry("480x450")
        dialog.configure(bg=STYLE["bg"])
        dialog.transient(self.root)
        dialog.grab_set()

        # Enhanced dialog header
        header_frame = ttk.Frame(dialog, padding=(24, 20))
        header_frame.pack(fill="x")
        
        ttk.Label(header_frame, text="✨ Create New Mod", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header_frame, text="Set up your new mod project", style="Dim.TLabel").pack(anchor="w", pady=(4, 0))

        # Form container
        form_frame = ttk.Frame(dialog, padding=(24, 0))
        form_frame.pack(fill="both", expand=True)

        fields = {}
        for name, label, default in [
            ("label", "Display Name", ""),
            ("name", "Internal Name", ""),
            ("version", "Version", "1.0.0"),
            ("description", "Description", ""),
        ]:
            field_container = ttk.Frame(form_frame)
            field_container.pack(fill="x", pady=(8, 4))
            
            ttk.Label(field_container, text=label, style="Header.TLabel").pack(anchor="w", pady=(0, 4))
            
            var = tk.StringVar()
            if name == "description":
                w = tk.Text(field_container, height=4, width=50, bg=STYLE["entry_bg"],
                           fg=STYLE["text"], font=("Segoe UI", 11),
                           insertbackground=STYLE["accent"], borderwidth=2,
                           relief="solid", padx=8, pady=6)
                w.pack(fill="x", expand=True)
                fields[name] = w
            else:
                w = ttk.Entry(field_container, textvariable=var, width=50)
                w.pack(fill="x", expand=True)
                if default:
                    var.set(default)
                fields[name] = var

        def do_create():
            label = fields["label"].get().strip() if isinstance(fields["label"], tk.StringVar) else ""
            name = fields["name"].get().strip() if isinstance(fields["name"], tk.StringVar) else ""
            version = fields["version"].get().strip() if isinstance(fields["version"], tk.StringVar) else "1.0.0"
            desc = fields["description"].get("1.0", "end").strip() if isinstance(fields["description"], tk.Text) else ""

            if not label or not name:
                messagebox.showerror("Missing", "Display Name and Internal Name are required.")
                return

            try:
                mods_dir = GameDataLocator.get_user_mods_dir()
                mods_dir.mkdir(parents=True, exist_ok=True)
                self.project = ModProject(mods_dir / name)
                self.project.create(
                    name=name, label=label, description=desc, version=version,
                    dependencies=["0ad=0.28.0"]
                )
                self.settings.last_mod_dir = str(self.project.mod_dir)
                self.settings.save()
                self._update_status_bar()
                self._refresh_template_list()
                self._load_mod_info_into_form()
                self._refresh_summary()
                messagebox.showinfo("Created", f"Mod '{label}' created successfully!")
                dialog.destroy()
                self.notebook.select(self.tab_summary)
            except FileExistsError:
                messagebox.showerror("Exists", f"A mod named '{name}' already exists.")

        # Button container
        button_frame = ttk.Frame(dialog, padding=(24, 20))
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Cancel",
                   command=dialog.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(button_frame, text="✨ Create Mod", style="Accent.TButton",
                   command=do_create).pack(side="right")

    def action_open_mod(self, *_):
        initial = self.settings.last_mod_dir
        if not initial or not Path(initial).is_dir():
            initial = str(GameDataLocator.get_user_mods_dir())

        path = filedialog.askdirectory(
            initialdir=initial,
            title="Select a mod folder"
        )
        if not path:
            return

        try:
            self.project = ModProject.load(Path(path))
            self.settings.last_mod_dir = str(self.project.mod_dir)
            self.settings.add_recent(str(self.project.mod_dir), self.project.info.label)
            self.settings.save()
            self._update_status_bar()
            self._refresh_template_list()
            self._load_mod_info_into_form()
            self._refresh_summary()
            messagebox.showinfo("Opened", f"Mod '{self.project.info.label}' loaded.")
        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e))

    def action_set_game_folder(self):
        folder_path = filedialog.askdirectory(
            title="Select 0 A.D. Installation Folder (or Cancel to pick public.zip)",
            initialdir=os.environ.get("ZEROAD_ROOT", "")
        )

        if folder_path:
            base = Path(folder_path)

            if GameDataLocator.validate_public_folder(base):
                self._set_asset_source(base, is_zip=False)
                return

            public_folder = base / GameDataLocator.REL_PUBLIC
            if GameDataLocator.validate_public_folder(public_folder):
                self._set_asset_source(public_folder, is_zip=False)
                return

            zip_in_folder = base / GameDataLocator.PUBLIC_ZIP_NAME
            if zip_in_folder.is_file() and GameDataLocator.validate_public_zip(zip_in_folder):
                self._set_asset_source(zip_in_folder, is_zip=True)
                return

            public_subdir = base / "public"
            if GameDataLocator.validate_public_folder(public_subdir):
                self._set_asset_source(public_subdir, is_zip=False)
                return

        zip_path = filedialog.askopenfilename(
            title="Select public.zip file",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )

        if zip_path:
            path = Path(zip_path)
            if GameDataLocator.validate_public_zip(path):
                self._set_asset_source(path, is_zip=True)
            else:
                messagebox.showerror(
                    "Invalid",
                    "This does not appear to be a valid 0 A.D. public.zip file.\n\n"
                    "Expected structure: simulation/, art/, audio/, gui/, maps/"
                )

    def action_build(self, *_):
        if not self.project or not self.project.is_loaded:
            messagebox.showwarning("No Mod", "Create or open a mod first.")
            return

        default_name = f"{self.project.info.name}.pyromod"
        initial_dir = str(GameDataLocator.get_user_mods_dir())
        path = filedialog.asksaveasfilename(
            initialfile=default_name,
            defaultextension=".pyromod",
            filetypes=[("PyroMod files", "*.pyromod"), ("ZIP files", "*.zip"), ("All files", "*.*")],
            initialdir=initial_dir
        )
        if not path:
            return

        try:
            result = self.project.build_pyromod(Path(path))
            size_kb = result.stat().st_size / 1024
            messagebox.showinfo(
                "Built!",
                f"Mod packaged successfully!\n\n"
                f"Location: {result}\n"
                f"Size: {size_kb:.1f} KB\n\n"
                f"Drag the .pyromod onto pyrogenesis.exe or install via in-game Mod Manager."
            )
        except Exception as e:
            messagebox.showerror("Build Error", str(e))

    def action_about(self):
        messagebox.showinfo(
            "About",
            "0 A.D. Mod Maker — GUI Edition\n"
            "v1.0.0\n\n"
            "Browse and modify 0 A.D. game assets\n"
            "Import unit templates, textures, and models\n"
            "Edit unit stats, create new units\n"
            "Package everything into a .pyromod file\n\n"
            "For the 0 A.D. modding community.\n"
            "MIT License"
        )

    def action_show_recent(self, *_):
        """Switch to Recent Projects tab."""
        self._refresh_recent_list()
        self.notebook.select(self.tab_recent)

    # ── Shutdown ────────────────────────────────────────────────────────

    def _on_close(self):
        """Save settings and quit."""
        # Save window dimensions
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # Only save if dimensions are reasonable (not minimized or iconified)
        if width >= WindowDefaults.MIN_WIDTH and height >= WindowDefaults.MIN_HEIGHT:
            self.settings.set("window_width", width)
            self.settings.set("window_height", height)
        
        # Save any pending changes
        self.settings.save()
        
        # Close any open asset source handles
        if hasattr(self, 'asset_source') and self.asset_source:
            try:
                if hasattr(self.asset_source, 'close'):
                    self.asset_source.close()
            except Exception as e:
                logger.warning(f"Error closing asset source: {e}")
        
        # Destroy the window
        self.root.destroy()

# ── Entry point ──────────────────────────────────────────────────────────

def run():
    """Start the GUI application."""
    root = tk.Tk()
    app = ModMakerGUI(root)
    root.mainloop()