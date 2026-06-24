"""
GUI application for managing crowd monitoring system configuration.
Allows users to easily configure all parameters and run the system.
With MAC-based license protection.
"""

import json
import os
import platform
import signal
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
from dataclasses import asdict
from pathlib import Path
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Any, Optional

APP_DIR = Path(__file__).resolve().parent
if Path.cwd() != APP_DIR:
    os.chdir(APP_DIR)

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

AUTH_DIR = APP_DIR / 'auth'
if str(AUTH_DIR) not in sys.path:
    sys.path.insert(0, str(AUTH_DIR))

from auth.license_manager import LicenseManager
from config import MonitoringConfig


class ScrollableCanvas(tk.Canvas):
    """Canvas that keeps embedded form content full-width and mouse-wheel scrollable."""

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._window_items = []
        self.bind("<Configure>", self._resize_window_items)
        self.bind("<Enter>", self._bind_mousewheel)
        self.bind("<Leave>", self._unbind_mousewheel)

    def create_window(self, *args, **kwargs):
        item = super().create_window(*args, **kwargs)
        if kwargs.get("window") is not None:
            self._window_items.append(item)
            self.itemconfigure(item, width=max(1, self.winfo_width()))
        return item

    def _resize_window_items(self, event):
        for item in self._window_items:
            self.itemconfigure(item, width=max(1, event.width))

    def _bind_mousewheel(self, _event):
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<Button-4>", self._on_mousewheel)
        self.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, _event):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if not self.bbox("all"):
            return

        if getattr(event, "num", None) == 4:
            units = -1
        elif getattr(event, "num", None) == 5:
            units = 1
        else:
            delta = getattr(event, "delta", 0)
            units = -int(delta / 120) if abs(delta) >= 120 else (-1 if delta > 0 else 1)

        self.yview_scroll(units, "units")


def _install_classic_tk_widgets(bg_color: str, panel_color: str, text_color: str, disabled_text_color: str):
    """Use classic Tk widgets when Apple's deprecated ttk renderer mispaints in dark mode."""
    if getattr(ttk, "_stampede_classic_widgets_installed", False):
        return

    uses_dark_palette = text_color.lower() in {"#ffffff", "#f2f2f2", "white"}
    button_color = "#303030" if uses_dark_palette else "#e6e6e6"
    active_button_color = "#3a3a3a" if uses_dark_palette else "#d9e8ff"
    selected_button_color = "#444444" if uses_dark_palette else "#ffffff"
    border_color = "#4a4a4a" if uses_dark_palette else "#b8b8b8"

    class ClassicFrame(tk.Frame):
        def __init__(self, master=None, **kwargs):
            kwargs.setdefault("bg", bg_color)
            super().__init__(master, **kwargs)

    class ClassicLabel(tk.Label):
        def __init__(self, master=None, **kwargs):
            kwargs.setdefault("bg", bg_color)
            kwargs.setdefault("fg", text_color)
            super().__init__(master, **kwargs)

    class ClassicButton(tk.Button):
        def __init__(self, master=None, **kwargs):
            kwargs.pop("style", None)
            kwargs.setdefault("bg", button_color)
            kwargs.setdefault("fg", text_color)
            kwargs.setdefault("activebackground", active_button_color)
            kwargs.setdefault("activeforeground", text_color)
            kwargs.setdefault("disabledforeground", disabled_text_color)
            kwargs.setdefault("relief", tk.RAISED)
            kwargs.setdefault("borderwidth", 1)
            super().__init__(master, **kwargs)

    class ClassicEntry(tk.Entry):
        def __init__(self, master=None, **kwargs):
            kwargs.setdefault("bg", panel_color)
            kwargs.setdefault("fg", text_color)
            kwargs.setdefault("insertbackground", text_color)
            kwargs.setdefault("disabledforeground", disabled_text_color)
            kwargs.setdefault("relief", tk.SUNKEN)
            super().__init__(master, **kwargs)

    class ClassicSpinbox(tk.Spinbox):
        def __init__(self, master=None, **kwargs):
            kwargs.setdefault("bg", panel_color)
            kwargs.setdefault("fg", text_color)
            kwargs.setdefault("insertbackground", text_color)
            kwargs.setdefault("disabledforeground", disabled_text_color)
            kwargs.setdefault("buttonbackground", button_color)
            kwargs.setdefault("relief", tk.SUNKEN)
            super().__init__(master, **kwargs)

    class ClassicScale(tk.Scale):
        def __init__(self, master=None, **kwargs):
            kwargs.setdefault("bg", bg_color)
            kwargs.setdefault("fg", text_color)
            kwargs.setdefault("troughcolor", panel_color)
            kwargs.setdefault("highlightthickness", 0)
            kwargs.setdefault("showvalue", False)
            kwargs.setdefault("resolution", -1)
            super().__init__(master, **kwargs)

    class ClassicCheckbutton(tk.Checkbutton):
        def __init__(self, master=None, **kwargs):
            kwargs.setdefault("bg", bg_color)
            kwargs.setdefault("fg", text_color)
            kwargs.setdefault("activebackground", bg_color)
            kwargs.setdefault("activeforeground", text_color)
            kwargs.setdefault("disabledforeground", disabled_text_color)
            kwargs.setdefault("selectcolor", panel_color)
            super().__init__(master, **kwargs)

    class ClassicScrollbar(tk.Scrollbar):
        def __init__(self, master=None, **kwargs):
            kwargs.setdefault("bg", button_color)
            kwargs.setdefault("troughcolor", bg_color)
            kwargs.setdefault("activebackground", active_button_color)
            super().__init__(master, **kwargs)

    class ClassicSeparator(tk.Frame):
        def __init__(self, master=None, orient="horizontal", **kwargs):
            kwargs.setdefault("bg", border_color)
            if orient == "vertical":
                kwargs.setdefault("width", 1)
            else:
                kwargs.setdefault("height", 1)
            super().__init__(master, **kwargs)

    class ClassicCombobox(tk.Menubutton):
        def __init__(self, master=None, values=(), width=None, state="normal", **kwargs):
            self.variable = tk.StringVar()
            self._values = tuple()
            self._selection_callbacks = []
            kwargs.setdefault("bg", panel_color)
            kwargs.setdefault("fg", text_color)
            kwargs.setdefault("activebackground", active_button_color)
            kwargs.setdefault("activeforeground", text_color)
            kwargs.setdefault("disabledforeground", disabled_text_color)
            kwargs.setdefault("relief", tk.SUNKEN)
            kwargs.setdefault("anchor", tk.W)
            kwargs.setdefault("indicatoron", True)
            kwargs["textvariable"] = self.variable
            if width is not None:
                kwargs["width"] = width
            super().__init__(master, **kwargs)
            self.menu = tk.Menu(self, tearoff=0, bg=panel_color, fg=text_color, activebackground=active_button_color)
            super().configure(menu=self.menu)
            self.configure(values=values, state=state)

        def _set_values(self, values):
            self._values = tuple(str(value) for value in values)
            self.menu.delete(0, tk.END)
            for value in self._values:
                self.menu.add_command(label=value, command=lambda selected=value: self._select(selected))

        def _select(self, value):
            self.variable.set(value)
            event = tk.Event()
            event.widget = self
            for callback in self._selection_callbacks:
                callback(event)

        def bind(self, sequence=None, func=None, add=None):
            if sequence == '<<ComboboxSelected>>' and func is not None:
                self._selection_callbacks.append(func)
                return None
            return super().bind(sequence, func, add)

        def configure(self, cnf=None, **kwargs):
            if cnf:
                kwargs.update(cnf)
            if "values" in kwargs:
                self._set_values(kwargs.pop("values"))
            if kwargs.get("state") == "readonly":
                kwargs["state"] = tk.NORMAL
            return super().configure(**kwargs)

        config = configure

        def __getitem__(self, key):
            if key == "values":
                return self._values
            return super().__getitem__(key)

        def current(self, index):
            self.variable.set(self._values[index])

        def set(self, value):
            self.variable.set(str(value))

        def get(self):
            return self.variable.get()

    class ClassicNotebook(tk.Frame):
        def __init__(self, master=None, **kwargs):
            kwargs.setdefault("bg", bg_color)
            super().__init__(master, **kwargs)
            self._tab_bar = tk.Frame(self, bg=bg_color)
            self._tab_bar.place(x=0, y=0, relwidth=1)
            self._tabs = []
            self._selected = None
            self.bind("<Configure>", lambda _event: self._layout_pages())
            self._tab_bar.bind("<Configure>", lambda _event: self._layout_pages())

        def add(self, child, text=""):
            tab_index = len(self._tabs)
            button = tk.Button(
                self._tab_bar,
                text=text,
                bg=button_color,
                fg=text_color,
                activebackground=active_button_color,
                activeforeground=text_color,
                relief=tk.RAISED,
                borderwidth=1,
                command=lambda frame=child: self.select(frame),
            )
            button.grid(row=0, column=tab_index, sticky="w", padx=(0, 2), pady=(0, 2))
            child.place(x=-20000, y=-20000, width=1, height=1)
            self._tabs.append((child, button))
            if self._selected is None:
                self.select(child)
            else:
                self.select(self._selected)

        def select(self, child=None):
            if child is None:
                return str(self._selected) if self._selected is not None else ""

            if isinstance(child, str):
                child = self.nametowidget(child)

            self._selected = child
            for frame, button in self._tabs:
                button.configure(
                    relief=tk.SUNKEN if frame is child else tk.RAISED,
                    bg=selected_button_color if frame is child else button_color,
                )
                if frame is not child:
                    frame.place_configure(x=-20000, y=-20000, width=1, height=1)

            self._layout_pages()
            for grandchild in child.winfo_children():
                if isinstance(grandchild, tk.Canvas):
                    grandchild.yview_moveto(0)
                    break

        def _layout_pages(self):
            tab_height = max(1, self._tab_bar.winfo_reqheight())
            width = max(1, self.winfo_width())
            height = max(1, self.winfo_height() - tab_height)
            self._tab_bar.place_configure(x=0, y=0, width=width, height=tab_height)

            for frame, _button in self._tabs:
                if frame is self._selected:
                    frame.place_configure(x=0, y=tab_height, width=width, height=height)
                    frame.lift()
                else:
                    frame.place_configure(x=-20000, y=-20000, width=1, height=1)
                    frame.lower()

            self._tab_bar.lift()

        def tabs(self):
            return [str(frame) for frame, _ in self._tabs]

    ttk.Frame = ClassicFrame
    ttk.Label = ClassicLabel
    ttk.Button = ClassicButton
    ttk.Entry = ClassicEntry
    ttk.Spinbox = ClassicSpinbox
    ttk.Scale = ClassicScale
    ttk.Checkbutton = ClassicCheckbutton
    ttk.Scrollbar = ClassicScrollbar
    ttk.Separator = ClassicSeparator
    ttk.Combobox = ClassicCombobox
    ttk.Notebook = ClassicNotebook
    ttk._stampede_classic_widgets_installed = True


class ConfigurationGUI:
    """GUI for configuring and running the crowd monitoring system"""

    def __init__(self, root: tk.Tk):
        """
        Initialize the configuration GUI.

        Args:
            root: Root tkinter window
        """
        self.root = root
        self.root.title("Crowd Monitoring System - Configuration Manager")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = min(1000, max(760, screen_width - 80))
        window_height = min(800, max(560, screen_height - 120))
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.minsize(760, 520)
        self._setup_style()

        # Initialize license manager with correct path
        self.license_manager = LicenseManager(str(AUTH_DIR / 'license.dat'))

        # Check license before showing UI
        if not self._check_license():
            self.root.destroy()
            return

        # Configuration storage
        self.config = MonitoringConfig()
        self.config_widgets: Dict[str, tk.Widget] = {}
        self.current_monitor = None  # Reference to running monitor
        self.monitor_thread: Optional[threading.Thread] = None
        self.monitor_process: Optional[subprocess.Popen] = None
        self.monitor_config_path: Optional[str] = None
        self.stop_requested = False  # Flag to signal monitor to stop

        # Camera detection state
        self.available_cameras: list = []
        self.cameras_detected: bool = False
        self.detecting_cameras: bool = False

        # Setup UI
        self._setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Load defaults immediately, then defer startup I/O until after Tk paints.
        self._load_config_to_ui()
        self.root.after(250, self._finish_startup)

    def _check_license(self) -> bool:
        """
        Check if a valid license exists.

        Returns:
            True if license is valid, False otherwise
        """
        is_valid, message = self.license_manager.validate_license()

        if is_valid:
            # Show license info in status
            license_info = self.license_manager.get_license_info()
            if license_info:
                days = license_info.get('days_remaining', 0)

                if days < 30:
                    messagebox.showwarning(
                        "License Expiring Soon",
                        f"Your license will expire in {days} days. Please renew soon."
                    )
            return True
        else:
            # Show license dialog
            messagebox.showwarning("License Required", message)

            # Use the license manager's activation dialog
            result = self.license_manager.show_activation_dialog(self.root)

            if not result:
                messagebox.showerror(
                    "License Required",
                    "A valid license is required to use this application."
                )
                return False

            return True

    def _setup_style(self):
        """Use deterministic light colors so macOS dark mode does not hide widgets."""
        self.use_classic_widgets = (
                os.getenv("STAMPEDE_CLASSIC_TK") == "1"
                or (platform.system() == "Darwin" and tk.TkVersion < 8.6)
        )

        if self.use_classic_widgets:
            self.bg_color = "#1f1f1f"
            self.panel_color = "#303030"
            self.text_color = "#f2f2f2"
            self.disabled_text_color = "#8c8c8c"
        else:
            self.bg_color = "#f2f2f2"
            self.panel_color = "#ffffff"
            self.text_color = "#1f1f1f"
            self.disabled_text_color = "#7a7a7a"

        self.root.configure(bg=self.bg_color)
        if self.use_classic_widgets:
            _install_classic_tk_widgets(
                self.bg_color,
                self.panel_color,
                self.text_color,
                self.disabled_text_color,
            )
            print("Using classic Tk widgets for deprecated Apple Tk renderer")

        style = ttk.Style(self.root)
        if platform.system() == "Darwin" and "clam" in style.theme_names():
            try:
                style.theme_use("clam")
            except tk.TclError:
                pass

        style.configure(".", background=self.bg_color, foreground=self.text_color)
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.text_color)
        style.configure("TCheckbutton", background=self.bg_color, foreground=self.text_color)
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background="#d8d8d8",
            foreground=self.text_color,
            padding=(10, 5),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", self.panel_color), ("active", "#e6e6e6")],
            foreground=[("selected", self.text_color), ("disabled", self.disabled_text_color)],
        )
        style.configure("TButton", background="#e6e6e6", foreground=self.text_color, padding=(8, 4))
        style.map(
            "TButton",
            background=[("active", "#d9e8ff"), ("disabled", "#e0e0e0")],
            foreground=[("disabled", self.disabled_text_color)],
        )
        style.configure("Accent.TButton", background="#0f62fe", foreground="#ffffff")
        style.map(
            "Accent.TButton",
            background=[("active", "#0353e9"), ("disabled", "#b8c1d1")],
            foreground=[("disabled", "#f0f0f0")],
        )
        style.configure("TEntry", fieldbackground=self.panel_color, foreground=self.text_color)
        style.configure("TSpinbox", fieldbackground=self.panel_color, foreground=self.text_color)
        style.configure("TCombobox", fieldbackground=self.panel_color, foreground=self.text_color)
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", self.panel_color)],
            foreground=[("readonly", self.text_color), ("disabled", self.disabled_text_color)],
        )
        style.configure("Horizontal.TScale", background=self.bg_color)

    def _create_canvas(self, parent: tk.Widget) -> tk.Canvas:
        """Create a canvas that does not inherit macOS' dark system background."""
        return ScrollableCanvas(parent, background=self.bg_color, highlightthickness=0, borderwidth=0)

    def _finish_startup(self):
        """Run startup work after the configuration window has had a chance to paint."""
        self._load_system_config()
        self._load_config_to_ui()
        self._schedule_license_check()
        self.root.after(750, self._detect_cameras_async)

    def _get_resource_path(self, relative_path: str) -> Path:
        """Resolve resource paths without importing detector/YOLO during GUI startup."""
        try:
            base_path = Path(sys._MEIPASS)  # type: ignore[attr-defined]
        except AttributeError:
            base_path = APP_DIR

        resource_path = base_path / relative_path
        if resource_path.exists():
            return resource_path

        if getattr(sys, 'frozen', False):
            resource_path = Path(sys.executable).resolve().parent / relative_path
            if resource_path.exists():
                return resource_path

        packaged_resource_path = APP_DIR / "auth" / "CrowdMonitor_Package_Windows" / relative_path
        if packaged_resource_path.exists():
            return packaged_resource_path

        return Path(relative_path)

    def _load_system_config(self):
        """Load system configuration from system_conf.json if it exists"""
        try:
            config_path = self._get_resource_path('system_conf.json')

            if config_path.exists():
                with open(config_path, 'r') as f:
                    config_dict = json.load(f)

                # Update config object with loaded values
                for key, value in config_dict.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)

                self.status_var.set(f"Loaded configuration from system_conf.json")
                print(f"✓ Loaded system configuration from: {config_path}")
            else:
                print("ℹ system_conf.json not found, using default configuration")
        except Exception as e:
            print(f"⚠ Warning: Could not load system_conf.json: {e}")
            # Continue with defaults - this is not a critical error

    def _schedule_license_check(self):
        """Schedule periodic license validation"""
        # Check license every 5 minutes
        is_valid, message = self.license_manager.validate_license()

        if not is_valid:
            messagebox.showerror("License Invalid",
                                 f"License validation failed: {message}\n\nApplication will close.")
            self.root.destroy()
            return

        # Schedule next check
        self.root.after(300000, self._schedule_license_check)  # 5 minutes

    def _setup_ui(self):
        """Setup the user interface"""
        # Create main container with scrollbar
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        # Create tabs
        self._create_video_tab()
        self._create_grid_tab()
        self._create_detection_tab()
        self._create_tracking_tab()
        self._create_smoothing_tab()
        self._create_visualization_tab()
        self._create_interactive_tab()
        self._create_calibration_tab()

        # Button frame at bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # Control buttons
        ttk.Button(button_frame, text="Load Config", command=self._load_config_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Config", command=self._save_config_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_to_defaults).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="License Info", command=self._show_license_info).pack(side=tk.LEFT, padx=5)

        # Spacer
        ttk.Frame(button_frame).pack(side=tk.LEFT, expand=True)

        # Run button (prominent) - Initially disabled until cameras detected
        self.run_button = ttk.Button(button_frame, text="▶ Run Monitor",
                                     command=self._run_monitor, style="Accent.TButton",
                                     state=tk.DISABLED)
        self.run_button.pack(side=tk.RIGHT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="⏹ Stop Monitor",
                                      command=self._stop_monitor, state=tk.DISABLED)
        self.stop_button.pack(side=tk.RIGHT, padx=5)

        # Status bar with license info
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))

        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var,
                               relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # License status
        license_info = self.license_manager.get_license_info()
        if license_info:
            days = license_info.get('days_remaining', 0)
            license_text = f"Licensed | {days} days remaining"
        else:
            license_text = "License: Unknown"

        self.license_status_var = tk.StringVar(value=license_text)
        license_status = ttk.Label(status_frame, textvariable=self.license_status_var,
                                   relief=tk.SUNKEN, anchor=tk.E, width=30)
        license_status.pack(side=tk.RIGHT)

    def _create_video_tab(self):
        """Create video source settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Video Source")

        # Create scrollable frame
        canvas = self._create_canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Video Source
        row = 0
        ttk.Label(scrollable_frame, text="Video Source Settings", font=("", 10, "bold")).grid(row=row, column=0,
                                                                                              columnspan=3, sticky=tk.W,
                                                                                              pady=(10, 5))

        row += 1
        ttk.Label(scrollable_frame, text="Video Source:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        source_frame = ttk.Frame(scrollable_frame)
        source_frame.grid(row=row, column=1, sticky=tk.W, pady=5)

        # Camera dropdown
        self.config_widgets['source'] = ttk.Combobox(source_frame, width=35, state='readonly')
        self.config_widgets['source'].pack(side=tk.LEFT, padx=5)
        self.config_widgets['source'].bind('<<ComboboxSelected>>', self._on_camera_selected)

        # Detect cameras button
        self.detect_button = ttk.Button(source_frame, text="Detect Cameras", command=self._detect_cameras_async)
        self.detect_button.pack(side=tk.LEFT, padx=2)

        # Browse for video file button
        ttk.Button(source_frame, text="Browse File", command=self._browse_video_source).pack(side=tk.LEFT, padx=2)

        # Status label
        self.camera_status_label = ttk.Label(scrollable_frame, text="Detecting cameras...", foreground="blue")
        self.camera_status_label.grid(row=row, column=2, sticky=tk.W, padx=10)

        row += 1
        ttk.Label(scrollable_frame, text="Model Path:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        model_frame = ttk.Frame(scrollable_frame)
        model_frame.grid(row=row, column=1, sticky=tk.W, pady=5)
        self.config_widgets['model_path'] = ttk.Entry(model_frame, width=30)
        self.config_widgets['model_path'].pack(side=tk.LEFT, padx=5)
        ttk.Button(model_frame, text="Browse", command=self._browse_model_path).pack(side=tk.LEFT)
        ttk.Label(scrollable_frame, text="Path to YOLO model file").grid(row=row, column=2, sticky=tk.W, padx=10)

        # Camera Settings
        row += 1
        ttk.Separator(scrollable_frame, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky=tk.EW,
                                                                  pady=10)

        row += 1
        ttk.Label(scrollable_frame, text="Camera Settings", font=("", 10, "bold")).grid(row=row, column=0, columnspan=3,
                                                                                        sticky=tk.W, pady=(10, 5))

        row += 1
        ttk.Label(scrollable_frame, text="Camera Width:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['camera_width'] = ttk.Spinbox(scrollable_frame, from_=320, to=3840, width=15)
        self.config_widgets['camera_width'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="pixels").grid(row=row, column=2, sticky=tk.W, padx=10)

        row += 1
        ttk.Label(scrollable_frame, text="Camera Height:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['camera_height'] = ttk.Spinbox(scrollable_frame, from_=240, to=2160, width=15)
        self.config_widgets['camera_height'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="pixels").grid(row=row, column=2, sticky=tk.W, padx=10)

        row += 1
        ttk.Label(scrollable_frame, text="Camera FPS:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['camera_fps'] = ttk.Spinbox(scrollable_frame, from_=1, to=120, width=15)
        self.config_widgets['camera_fps'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="frames per second").grid(row=row, column=2, sticky=tk.W, padx=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_grid_tab(self):
        """Create grid and spatial settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Grid & Spatial")

        canvas = self._create_canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        row = 0
        ttk.Label(scrollable_frame, text="Grid Settings", font=("", 10, "bold")).grid(row=row, column=0, columnspan=3,
                                                                                      sticky=tk.W, pady=(10, 5))

        row += 1
        ttk.Label(scrollable_frame, text="Cell Width:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['cell_width'] = ttk.Spinbox(scrollable_frame, from_=0.1, to=10.0, increment=0.1, width=15)
        self.config_widgets['cell_width'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="meters").grid(row=row, column=2, sticky=tk.W, padx=10)

        row += 1
        ttk.Label(scrollable_frame, text="Cell Height:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['cell_height'] = ttk.Spinbox(scrollable_frame, from_=0.1, to=10.0, increment=0.1, width=15)
        self.config_widgets['cell_height'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="meters").grid(row=row, column=2, sticky=tk.W, padx=10)

        row += 1
        ttk.Label(scrollable_frame, text="Person Radius:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['person_radius'] = ttk.Spinbox(scrollable_frame, from_=0.1, to=10.0, increment=0.1,
                                                           width=15)
        self.config_widgets['person_radius'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="meters (for capacity calculation)").grid(row=row, column=2, sticky=tk.W,
                                                                                   padx=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_detection_tab(self):
        """Create detection settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Detection")

        canvas = self._create_canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        row = 0
        ttk.Label(scrollable_frame, text="Detection Settings", font=("", 10, "bold")).grid(row=row, column=0,
                                                                                           columnspan=3, sticky=tk.W,
                                                                                           pady=(10, 5))

        row += 1
        ttk.Label(scrollable_frame, text="Detect Every N Frames:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['detect_every'] = ttk.Spinbox(scrollable_frame, from_=1, to=30, width=15)
        self.config_widgets['detect_every'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="Higher = faster, less accurate").grid(row=row, column=2, sticky=tk.W, padx=10)

        row += 1
        ttk.Label(scrollable_frame, text="Confidence Threshold:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['confidence_threshold'] = ttk.Scale(scrollable_frame, from_=0.0, to=1.0,
                                                                orient=tk.HORIZONTAL, length=200)
        self.config_widgets['confidence_threshold'].grid(row=row, column=1, sticky=tk.W, pady=5)
        self.confidence_label = ttk.Label(scrollable_frame, text="0.35")
        self.confidence_label.grid(row=row, column=2, sticky=tk.W, padx=10)
        self.config_widgets['confidence_threshold'].configure(
            command=lambda v: self.confidence_label.configure(text=f"{float(v):.2f}"))

        row += 1
        ttk.Label(scrollable_frame, text="Min BBox Area:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['min_bbox_area'] = ttk.Spinbox(scrollable_frame, from_=100, to=10000, increment=100,
                                                           width=15)
        self.config_widgets['min_bbox_area'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="pixels (filter small detections)").grid(row=row, column=2, sticky=tk.W,
                                                                                  padx=10)

        row += 1
        ttk.Separator(scrollable_frame, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky=tk.EW,
                                                                  pady=10)

        row += 1
        ttk.Label(scrollable_frame, text="YOLO Model Settings", font=("", 10, "bold")).grid(row=row, column=0,
                                                                                            columnspan=3, sticky=tk.W,
                                                                                            pady=(10, 5))

        row += 1
        ttk.Label(scrollable_frame, text="YOLO Image Size:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['yolo_imgsz'] = ttk.Combobox(scrollable_frame, values=[320, 416, 512, 640, 800, 1024],
                                                         width=15)
        self.config_widgets['yolo_imgsz'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="pixels (higher = slower, more accurate)").grid(row=row, column=2, sticky=tk.W,
                                                                                         padx=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_tracking_tab(self):
        """Create tracking settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Tracking")

        canvas = self._create_canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        row = 0
        ttk.Label(scrollable_frame, text="Tracking Settings", font=("", 10, "bold")).grid(row=row, column=0,
                                                                                          columnspan=3, sticky=tk.W,
                                                                                          pady=(10, 5))

        row += 1
        self.config_widgets['use_deepsort'] = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text="Use DeepSort Tracker",
                        variable=self.config_widgets['use_deepsort']).grid(row=row, column=0, columnspan=2, sticky=tk.W,
                                                                           padx=10, pady=5)
        ttk.Label(scrollable_frame, text="Requires DeepSort library").grid(row=row, column=2, sticky=tk.W, padx=10)

        row += 1
        ttk.Label(scrollable_frame, text="Max Age:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['max_age'] = ttk.Spinbox(scrollable_frame, from_=1, to=300, width=15)
        self.config_widgets['max_age'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="frames to keep track without detection").grid(row=row, column=2, sticky=tk.W,
                                                                                        padx=10)

        row += 1
        ttk.Label(scrollable_frame, text="N Init:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['n_init'] = ttk.Spinbox(scrollable_frame, from_=1, to=10, width=15)
        self.config_widgets['n_init'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="frames to confirm new track").grid(row=row, column=2, sticky=tk.W, padx=10)

        row += 1
        ttk.Separator(scrollable_frame, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky=tk.EW,
                                                                  pady=10)

        row += 1
        ttk.Label(scrollable_frame, text="Centroid Tracker Settings", font=("", 10, "bold")).grid(row=row, column=0,
                                                                                                  columnspan=3,
                                                                                                  sticky=tk.W,
                                                                                                  pady=(10, 5))

        row += 1
        ttk.Label(scrollable_frame, text="Distance Threshold:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['centroid_distance_threshold'] = ttk.Spinbox(scrollable_frame, from_=10, to=500,
                                                                         increment=10, width=15)
        self.config_widgets['centroid_distance_threshold'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="pixels (max distance for same person)").grid(row=row, column=2, sticky=tk.W,
                                                                                       padx=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_smoothing_tab(self):
        """Create smoothing and alert settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Smoothing & Alerts")

        canvas = self._create_canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        row = 0
        ttk.Label(scrollable_frame, text="Smoothing Settings", font=("", 10, "bold")).grid(row=row, column=0,
                                                                                           columnspan=3, sticky=tk.W,
                                                                                           pady=(10, 5))

        row += 1
        ttk.Label(scrollable_frame, text="EMA Alpha:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['ema_alpha'] = ttk.Scale(scrollable_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL,
                                                     length=200)
        self.config_widgets['ema_alpha'].grid(row=row, column=1, sticky=tk.W, pady=5)
        self.ema_label = ttk.Label(scrollable_frame, text="0.4")
        self.ema_label.grid(row=row, column=2, sticky=tk.W, padx=10)
        self.config_widgets['ema_alpha'].configure(command=lambda v: self.ema_label.configure(text=f"{float(v):.2f}"))

        row += 1
        ttk.Label(scrollable_frame, text="Expected FPS:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['fps'] = ttk.Spinbox(scrollable_frame, from_=1, to=120, width=15)
        self.config_widgets['fps'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="for timing calculations").grid(row=row, column=2, sticky=tk.W, padx=10)

        row += 1
        ttk.Label(scrollable_frame, text="Hysteresis Time:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['hysteresis_time'] = ttk.Spinbox(scrollable_frame, from_=0.1, to=10.0, increment=0.1,
                                                             width=15)
        self.config_widgets['hysteresis_time'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="seconds (alert debounce time)").grid(row=row, column=2, sticky=tk.W, padx=10)

        row += 1
        ttk.Separator(scrollable_frame, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky=tk.EW,
                                                                  pady=10)

        row += 1
        ttk.Label(scrollable_frame, text="Alert Thresholds", font=("", 10, "bold")).grid(row=row, column=0,
                                                                                         columnspan=3, sticky=tk.W,
                                                                                         pady=(10, 5))

        row += 1
        ttk.Label(scrollable_frame, text="Alert Clear Offset:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['alert_clear_offset'] = ttk.Scale(scrollable_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL,
                                                              length=200)
        self.config_widgets['alert_clear_offset'].grid(row=row, column=1, sticky=tk.W, pady=5)
        self.alert_offset_label = ttk.Label(scrollable_frame, text="0.5")
        self.alert_offset_label.grid(row=row, column=2, sticky=tk.W, padx=10)
        self.config_widgets['alert_clear_offset'].configure(
            command=lambda v: self.alert_offset_label.configure(text=f"{float(v):.2f}"))

        row += 1
        ttk.Label(scrollable_frame, text="Warning Threshold:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['occupancy_warning_threshold'] = ttk.Scale(scrollable_frame, from_=0.0, to=1.0,
                                                                       orient=tk.HORIZONTAL, length=200)
        self.config_widgets['occupancy_warning_threshold'].grid(row=row, column=1, sticky=tk.W, pady=5)
        self.warning_label = ttk.Label(scrollable_frame, text="0.8")
        self.warning_label.grid(row=row, column=2, sticky=tk.W, padx=10)
        self.config_widgets['occupancy_warning_threshold'].configure(
            command=lambda v: self.warning_label.configure(text=f"{float(v):.2f}"))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_visualization_tab(self):
        """Create visualization settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Visualization")

        canvas = self._create_canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        row = 0
        ttk.Label(scrollable_frame, text="Display Settings", font=("", 10, "bold")).grid(row=row, column=0,
                                                                                         columnspan=3, sticky=tk.W,
                                                                                         pady=(10, 5))

        row += 1
        ttk.Label(scrollable_frame, text="Max Bird's Eye Pixels:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['max_birdseye_pixels'] = ttk.Spinbox(scrollable_frame, from_=300, to=2000, increment=50,
                                                                 width=15)
        self.config_widgets['max_birdseye_pixels'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="pixels").grid(row=row, column=2, sticky=tk.W, padx=10)

        row += 1
        ttk.Label(scrollable_frame, text="Grid Line Thickness:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['grid_line_thickness'] = ttk.Spinbox(scrollable_frame, from_=1, to=10, width=15)
        self.config_widgets['grid_line_thickness'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="pixels").grid(row=row, column=2, sticky=tk.W, padx=10)

        row += 1
        ttk.Label(scrollable_frame, text="BBox Thickness:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['bbox_thickness'] = ttk.Spinbox(scrollable_frame, from_=1, to=10, width=15)
        self.config_widgets['bbox_thickness'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="pixels").grid(row=row, column=2, sticky=tk.W, padx=10)

        row += 1
        ttk.Label(scrollable_frame, text="Info Panel Height:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['info_panel_height'] = ttk.Spinbox(scrollable_frame, from_=50, to=300, increment=10,
                                                               width=15)
        self.config_widgets['info_panel_height'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="pixels").grid(row=row, column=2, sticky=tk.W, padx=10)

        row += 1
        ttk.Separator(scrollable_frame, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky=tk.EW,
                                                                  pady=10)

        row += 1
        ttk.Label(scrollable_frame, text="Font Sizes", font=("", 10, "bold")).grid(row=row, column=0, columnspan=3,
                                                                                   sticky=tk.W, pady=(10, 5))

        font_settings = [
            ('font_size_large', 'Large', 0.8),
            ('font_size_medium', 'Medium', 0.6),
            ('font_size_small', 'Small', 0.5),
            ('font_size_tiny', 'Tiny', 0.4),
            ('font_size_birdseye', "Bird's Eye", 0.35)
        ]

        for key, label, default in font_settings:
            row += 1
            ttk.Label(scrollable_frame, text=f"{label} Font:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
            self.config_widgets[key] = ttk.Spinbox(scrollable_frame, from_=0.1, to=2.0, increment=0.05, width=15)
            self.config_widgets[key].grid(row=row, column=1, sticky=tk.W, pady=5)
            ttk.Label(scrollable_frame, text="scale").grid(row=row, column=2, sticky=tk.W, padx=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_interactive_tab(self):
        """Create interactive features tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Interactive")

        canvas = self._create_canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        row = 0
        ttk.Label(scrollable_frame, text="Interactive Features", font=("", 10, "bold")).grid(row=row, column=0,
                                                                                             columnspan=3, sticky=tk.W,
                                                                                             pady=(10, 5))

        row += 1
        self.config_widgets['enable_screenshots'] = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text="Enable Screenshots (press 's')",
                        variable=self.config_widgets['enable_screenshots']).grid(row=row, column=0, columnspan=3,
                                                                                 sticky=tk.W, padx=10, pady=5)

        row += 1
        self.config_widgets['enable_grid_adjustment'] = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text="Enable Grid Adjustment (press 'g')",
                        variable=self.config_widgets['enable_grid_adjustment']).grid(row=row, column=0, columnspan=3,
                                                                                     sticky=tk.W, padx=10, pady=5)

        row += 1
        ttk.Separator(scrollable_frame, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky=tk.EW,
                                                                  pady=10)

        row += 1
        ttk.Label(scrollable_frame, text="Display Options", font=("", 10, "bold")).grid(row=row, column=0, columnspan=3,
                                                                                        sticky=tk.W, pady=(10, 5))

        row += 1
        ttk.Label(scrollable_frame, text="FPS Counter Window:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['fps_counter_window'] = ttk.Spinbox(scrollable_frame, from_=10, to=120, width=15)
        self.config_widgets['fps_counter_window'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="frames to average").grid(row=row, column=2, sticky=tk.W, padx=10)

        row += 1
        ttk.Label(scrollable_frame, text="Split View Divisor:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['split_view_divisor'] = ttk.Spinbox(scrollable_frame, from_=2, to=4, width=15)
        self.config_widgets['split_view_divisor'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="(2 = half size, 3 = third size)").grid(row=row, column=2, sticky=tk.W,
                                                                                 padx=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_calibration_tab(self):
        """Create calibration settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Calibration")

        canvas = self._create_canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        row = 0
        ttk.Label(scrollable_frame, text="Calibration Area Dimensions", font=("", 10, "bold")).grid(row=row, column=0,
                                                                                                    columnspan=3,
                                                                                                    sticky=tk.W,
                                                                                                    pady=(10, 5))

        row += 1
        info_label = ttk.Label(scrollable_frame, text="Set the real-world dimensions of the calibrated area",
                               foreground="gray")
        info_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, padx=10, pady=(0, 10))

        row += 1
        ttk.Label(scrollable_frame, text="Area Width:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['calibration_area_width'] = ttk.Spinbox(scrollable_frame, from_=1.0, to=100.0,
                                                                    increment=0.5, width=15)
        self.config_widgets['calibration_area_width'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="meters (horizontal)").grid(row=row, column=2, sticky=tk.W, padx=10)

        row += 1
        ttk.Label(scrollable_frame, text="Area Height:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['calibration_area_height'] = ttk.Spinbox(scrollable_frame, from_=1.0, to=100.0,
                                                                     increment=0.5, width=15)
        self.config_widgets['calibration_area_height'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="meters (vertical)").grid(row=row, column=2, sticky=tk.W, padx=10)

        row += 1
        self.config_widgets['auto_calibration'] = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text="Use preset dimensions (skip manual input during calibration)",
                        variable=self.config_widgets['auto_calibration']).grid(row=row, column=0, columnspan=3,
                                                                               sticky=tk.W, padx=10, pady=10)

        row += 1
        ttk.Separator(scrollable_frame, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky=tk.EW,
                                                                  pady=10)

        row += 1
        ttk.Label(scrollable_frame, text="Calibration Display Settings", font=("", 10, "bold")).grid(row=row, column=0,
                                                                                                     columnspan=3,
                                                                                                     sticky=tk.W,
                                                                                                     pady=(10, 5))

        row += 1
        ttk.Label(scrollable_frame, text="Point Radius:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['calibration_point_radius'] = ttk.Spinbox(scrollable_frame, from_=3, to=20, width=15)
        self.config_widgets['calibration_point_radius'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="pixels").grid(row=row, column=2, sticky=tk.W, padx=10)

        row += 1
        ttk.Label(scrollable_frame, text="Line Thickness:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.config_widgets['calibration_line_thickness'] = ttk.Spinbox(scrollable_frame, from_=1, to=10, width=15)
        self.config_widgets['calibration_line_thickness'].grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Label(scrollable_frame, text="pixels").grid(row=row, column=2, sticky=tk.W, padx=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _detect_cameras_async(self):
        """Start camera detection in a background thread"""
        if self.detecting_cameras:
            return

        self.detecting_cameras = True
        self.cameras_detected = False

        # Update UI
        self.camera_status_label.config(text="Detecting cameras...", foreground="blue")
        self.detect_button.config(state=tk.DISABLED)
        self.run_button.config(state=tk.DISABLED)
        self.config_widgets['source'].config(state='disabled')

        # Start detection in background thread
        detection_thread = threading.Thread(target=self._detect_cameras_thread, daemon=True)
        detection_thread.start()

    def _detect_cameras_thread(self):
        """Background thread for camera detection"""
        try:
            if platform.system() == "Darwin" and not getattr(sys, 'frozen', False):
                self.available_cameras = self._detect_available_cameras_process(max_cameras=10)
            else:
                self.available_cameras = self._detect_available_cameras(max_cameras=10)

            # Update UI on main thread
            try:
                self.root.after(0, self._on_cameras_detected)
            except tk.TclError:
                pass

        except Exception as e:
            try:
                self.root.after(0, lambda: self._on_camera_detection_error(str(e)))
            except tk.TclError:
                pass

    def _detect_available_cameras_process(self, max_cameras: int) -> list:
        """Detect cameras outside the Tk process on macOS to avoid Cocoa event-loop conflicts."""
        script = r'''
import json
import platform

import cv2


def open_video_capture(source):
    avfoundation = getattr(cv2, "CAP_AVFOUNDATION", None)
    if isinstance(source, int) and platform.system() == "Darwin" and avfoundation is not None:
        cap = cv2.VideoCapture(source, avfoundation)
        if cap.isOpened():
            return cap
        cap.release()
    return cv2.VideoCapture(source)


cameras = []
for index in range(MAX_CAMERAS):
    cap = None
    try:
        cap = open_video_capture(index)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cameras.append({
                    "index": index,
                    "name": f"Camera {index} ({width}x{height})",
                    "width": width,
                    "height": height,
                })
    except Exception:
        pass
    finally:
        if cap is not None:
            cap.release()

print(json.dumps(cameras))
'''.replace("MAX_CAMERAS", str(max_cameras))

        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=str(APP_DIR),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
            raise RuntimeError(message)
        return json.loads(result.stdout.strip() or "[]")

    def _detect_available_cameras(self, max_cameras: int) -> list:
        """Detect camera sources without importing the monitor/YOLO stack."""
        import cv2

        def open_video_capture(source):
            avfoundation = getattr(cv2, "CAP_AVFOUNDATION", None)
            if isinstance(source, int) and platform.system() == "Darwin" and avfoundation is not None:
                cap = cv2.VideoCapture(source, avfoundation)
                if cap.isOpened():
                    return cap
                cap.release()
            return cv2.VideoCapture(source)

        available_cameras = []
        for index in range(max_cameras):
            cap = None
            try:
                cap = open_video_capture(index)
                if cap.isOpened():
                    ret, _ = cap.read()
                    if ret:
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        available_cameras.append({
                            'index': index,
                            'name': f"Camera {index} ({width}x{height})",
                            'width': width,
                            'height': height,
                        })
            except Exception:
                continue
            finally:
                if cap is not None:
                    cap.release()

        return available_cameras

    def _on_cameras_detected(self):
        """Called when camera detection completes successfully"""
        self.detecting_cameras = False
        self.cameras_detected = True

        # Update camera dropdown
        camera_options = []
        for cam in self.available_cameras:
            camera_options.append(f"{cam['index']} - {cam['name']}")

        # Add option for video file
        camera_options.append("Video File (Browse)")

        self.config_widgets['source'].config(values=camera_options, state='readonly')

        # Select first camera by default if available
        if self.available_cameras:
            self.config_widgets['source'].current(0)
            self.camera_status_label.config(
                text=f"✓ {len(self.available_cameras)} camera(s) detected",
                foreground="green"
            )
            self.run_button.config(state=tk.NORMAL)
        else:
            self.camera_status_label.config(
                text="⚠ No cameras found. Use 'Browse File' for video.",
                foreground="orange"
            )

        self.detect_button.config(state=tk.NORMAL)

    def _on_camera_detection_error(self, error_msg: str):
        """Called when camera detection fails"""
        self.detecting_cameras = False
        self.cameras_detected = False

        self.camera_status_label.config(
            text=f"✗ Detection failed: {error_msg}",
            foreground="red"
        )
        self.detect_button.config(state=tk.NORMAL)
        self.config_widgets['source'].config(state='readonly')

        messagebox.showerror("Camera Detection Error", f"Failed to detect cameras:\n{error_msg}")

    def _on_camera_selected(self, event):
        """Called when user selects a camera from dropdown"""
        selection = self.config_widgets['source'].get()

        if selection == "Video File (Browse)":
            self._browse_video_source()
        elif selection:
            # Enable run button if a camera is selected
            self.run_button.config(state=tk.NORMAL)

    def _browse_video_source(self):
        """Browse for video source file"""
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        )
        if filename:
            # Add the file to dropdown and select it
            current_values = list(self.config_widgets['source']['values'])
            file_option = f"File: {filename}"

            # Remove any previous file selections
            current_values = [v for v in current_values if not v.startswith("File:")]
            current_values.append(file_option)

            self.config_widgets['source'].config(values=current_values, state='readonly')
            self.config_widgets['source'].set(file_option)

            self.camera_status_label.config(text="✓ Video file selected", foreground="green")
            self.run_button.config(state=tk.NORMAL)
            self.cameras_detected = True

    def _browse_model_path(self):
        """Browse for model file"""
        filename = filedialog.askopenfilename(
            title="Select YOLO Model",
            filetypes=[("PyTorch models", "*.pt"), ("All files", "*.*")]
        )
        if filename:
            self.config_widgets['model_path'].delete(0, tk.END)
            self.config_widgets['model_path'].insert(0, filename)

    def _load_config_to_ui(self):
        """Load configuration values into UI widgets"""
        # Video source - will be set after camera detection completes
        # Don't set source here since it needs to match dropdown values
        self._set_widget_value('model_path', self.config.model_path)
        self._set_widget_value('camera_width', self.config.camera_width)
        self._set_widget_value('camera_height', self.config.camera_height)
        self._set_widget_value('camera_fps', self.config.camera_fps)

        # Grid
        self._set_widget_value('cell_width', self.config.cell_width)
        self._set_widget_value('cell_height', self.config.cell_height)
        self._set_widget_value('person_radius', self.config.person_radius)

        # Detection
        self._set_widget_value('detect_every', self.config.detect_every)
        self._set_widget_value('confidence_threshold', self.config.confidence_threshold)
        self._set_widget_value('min_bbox_area', self.config.min_bbox_area)
        self._set_widget_value('yolo_imgsz', self.config.yolo_imgsz)

        # Tracking
        self._set_widget_value('use_deepsort', self.config.use_deepsort)
        self._set_widget_value('max_age', self.config.max_age)
        self._set_widget_value('n_init', self.config.n_init)
        self._set_widget_value('centroid_distance_threshold', self.config.centroid_distance_threshold)

        # Smoothing
        self._set_widget_value('ema_alpha', self.config.ema_alpha)
        self._set_widget_value('fps', self.config.fps)
        self._set_widget_value('hysteresis_time', self.config.hysteresis_time)
        self._set_widget_value('alert_clear_offset', self.config.alert_clear_offset)
        self._set_widget_value('occupancy_warning_threshold', self.config.occupancy_warning_threshold)

        # Visualization
        self._set_widget_value('max_birdseye_pixels', self.config.max_birdseye_pixels)
        self._set_widget_value('grid_line_thickness', self.config.grid_line_thickness)
        self._set_widget_value('bbox_thickness', self.config.bbox_thickness)
        self._set_widget_value('info_panel_height', self.config.info_panel_height)
        self._set_widget_value('font_size_large', self.config.font_size_large)
        self._set_widget_value('font_size_medium', self.config.font_size_medium)
        self._set_widget_value('font_size_small', self.config.font_size_small)
        self._set_widget_value('font_size_tiny', self.config.font_size_tiny)
        self._set_widget_value('font_size_birdseye', self.config.font_size_birdseye)

        # Interactive
        self._set_widget_value('enable_screenshots', self.config.enable_screenshots)
        self._set_widget_value('enable_grid_adjustment', self.config.enable_grid_adjustment)
        self._set_widget_value('fps_counter_window', self.config.fps_counter_window)
        self._set_widget_value('split_view_divisor', self.config.split_view_divisor)

        # Calibration
        self._set_widget_value('calibration_area_width', self.config.calibration_area_width)
        self._set_widget_value('calibration_area_height', self.config.calibration_area_height)
        self._set_widget_value('auto_calibration', self.config.auto_calibration)
        self._set_widget_value('calibration_point_radius', self.config.calibration_point_radius)
        self._set_widget_value('calibration_line_thickness', self.config.calibration_line_thickness)

    def _set_widget_value(self, key: str, value: Any):
        """Set widget value based on widget type"""
        if key not in self.config_widgets:
            return

        widget = self.config_widgets[key]

        if isinstance(widget, tk.BooleanVar):
            widget.set(value)
        elif isinstance(widget, ttk.Combobox):
            # For combobox, try to set value directly
            widget.set(str(value))
        elif isinstance(widget, (ttk.Entry, ttk.Spinbox)):
            widget.delete(0, tk.END)
            widget.insert(0, str(value))
        elif isinstance(widget, ttk.Scale):
            widget.set(value)

    def _get_widget_value(self, key: str) -> Any:
        """Get value from widget based on widget type"""
        if key not in self.config_widgets:
            return None

        widget = self.config_widgets[key]

        if isinstance(widget, tk.BooleanVar):
            return widget.get()
        elif isinstance(widget, (ttk.Entry, ttk.Spinbox, ttk.Combobox)):
            return widget.get()
        elif isinstance(widget, ttk.Scale):
            return widget.get()

        return None

    def _collect_config_from_ui(self) -> MonitoringConfig:
        """Collect configuration from UI widgets"""

        # Helper to convert values
        def to_int(val):
            try:
                return int(float(val))
            except:
                return 0

        def to_float(val):
            try:
                return float(val)
            except:
                return 0.0

        # Parse video source from dropdown selection
        source_selection = self._get_widget_value('source')
        if source_selection.startswith("File:"):
            # Extract file path
            source = source_selection.replace("File:", "").strip()
        elif " - " in source_selection:
            # Extract camera index (format: "0 - Camera 0 (1280x720)")
            source = int(source_selection.split(" - ")[0])
        else:
            # Fallback to raw value
            source = source_selection

        config = MonitoringConfig(
            # Video
            source=source,
            model_path=self._get_widget_value('model_path'),
            camera_width=to_int(self._get_widget_value('camera_width')),
            camera_height=to_int(self._get_widget_value('camera_height')),
            camera_fps=to_int(self._get_widget_value('camera_fps')),

            # Grid
            cell_width=to_float(self._get_widget_value('cell_width')),
            cell_height=to_float(self._get_widget_value('cell_height')),
            person_radius=to_float(self._get_widget_value('person_radius')),

            # Detection
            detect_every=to_int(self._get_widget_value('detect_every')),
            confidence_threshold=to_float(self._get_widget_value('confidence_threshold')),
            min_bbox_area=to_int(self._get_widget_value('min_bbox_area')),
            yolo_imgsz=to_int(self._get_widget_value('yolo_imgsz')),

            # Tracking
            use_deepsort=self._get_widget_value('use_deepsort'),
            max_age=to_int(self._get_widget_value('max_age')),
            n_init=to_int(self._get_widget_value('n_init')),
            centroid_distance_threshold=to_float(self._get_widget_value('centroid_distance_threshold')),

            # Smoothing
            ema_alpha=to_float(self._get_widget_value('ema_alpha')),
            fps=to_float(self._get_widget_value('fps')),
            hysteresis_time=to_float(self._get_widget_value('hysteresis_time')),
            alert_clear_offset=to_float(self._get_widget_value('alert_clear_offset')),
            occupancy_warning_threshold=to_float(self._get_widget_value('occupancy_warning_threshold')),

            # Visualization
            max_birdseye_pixels=to_int(self._get_widget_value('max_birdseye_pixels')),
            grid_line_thickness=to_int(self._get_widget_value('grid_line_thickness')),
            bbox_thickness=to_int(self._get_widget_value('bbox_thickness')),
            info_panel_height=to_int(self._get_widget_value('info_panel_height')),
            font_size_large=to_float(self._get_widget_value('font_size_large')),
            font_size_medium=to_float(self._get_widget_value('font_size_medium')),
            font_size_small=to_float(self._get_widget_value('font_size_small')),
            font_size_tiny=to_float(self._get_widget_value('font_size_tiny')),
            font_size_birdseye=to_float(self._get_widget_value('font_size_birdseye')),

            # Interactive
            enable_screenshots=self._get_widget_value('enable_screenshots'),
            enable_grid_adjustment=self._get_widget_value('enable_grid_adjustment'),
            fps_counter_window=to_int(self._get_widget_value('fps_counter_window')),
            split_view_divisor=to_int(self._get_widget_value('split_view_divisor')),

            # Calibration
            calibration_area_width=to_float(self._get_widget_value('calibration_area_width')),
            calibration_area_height=to_float(self._get_widget_value('calibration_area_height')),
            auto_calibration=self._get_widget_value('auto_calibration'),
            calibration_point_radius=to_int(self._get_widget_value('calibration_point_radius')),
            calibration_line_thickness=to_int(self._get_widget_value('calibration_line_thickness')),

            # Backend streaming
            websocket_enabled=True,
            websocket_request_enabled=True,
            websocket_log_flow=True,
            websocket_url=self.config.websocket_url,
            websocket_device_id=self.config.websocket_device_id,
            websocket_mac_address=self.config.websocket_mac_address,
            websocket_device_name=self.config.websocket_device_name,
            websocket_location=self.config.websocket_location,
            websocket_debounce_seconds=self.config.websocket_debounce_seconds,
        )

        return config

    def _save_config_file(self):
        """Save configuration to JSON file"""
        filename = filedialog.asksaveasfilename(
            title="Save Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            config = self._collect_config_from_ui()
            config_dict = {
                'source': config.source,
                'model_path': config.model_path,
                'camera_width': config.camera_width,
                'camera_height': config.camera_height,
                'camera_fps': config.camera_fps,
                'cell_width': config.cell_width,
                'cell_height': config.cell_height,
                'person_radius': config.person_radius,
                'detect_every': config.detect_every,
                'confidence_threshold': config.confidence_threshold,
                'min_bbox_area': config.min_bbox_area,
                'yolo_imgsz': config.yolo_imgsz,
                'use_deepsort': config.use_deepsort,
                'max_age': config.max_age,
                'n_init': config.n_init,
                'centroid_distance_threshold': config.centroid_distance_threshold,
                'ema_alpha': config.ema_alpha,
                'fps': config.fps,
                'hysteresis_time': config.hysteresis_time,
                'alert_clear_offset': config.alert_clear_offset,
                'occupancy_warning_threshold': config.occupancy_warning_threshold,
                'max_birdseye_pixels': config.max_birdseye_pixels,
                'grid_line_thickness': config.grid_line_thickness,
                'bbox_thickness': config.bbox_thickness,
                'info_panel_height': config.info_panel_height,
                'font_size_large': config.font_size_large,
                'font_size_medium': config.font_size_medium,
                'font_size_small': config.font_size_small,
                'font_size_tiny': config.font_size_tiny,
                'font_size_birdseye': config.font_size_birdseye,
                'enable_screenshots': config.enable_screenshots,
                'enable_grid_adjustment': config.enable_grid_adjustment,
                'fps_counter_window': config.fps_counter_window,
                'split_view_divisor': config.split_view_divisor,
                'calibration_area_width': config.calibration_area_width,
                'calibration_area_height': config.calibration_area_height,
                'auto_calibration': config.auto_calibration,
                'calibration_point_radius': config.calibration_point_radius,
                'calibration_line_thickness': config.calibration_line_thickness,
                'websocket_enabled': config.websocket_enabled,
                'websocket_request_enabled': config.websocket_request_enabled,
                'websocket_log_flow': config.websocket_log_flow,
                'websocket_url': config.websocket_url,
                'websocket_device_id': config.websocket_device_id,
                'websocket_mac_address': config.websocket_mac_address,
                'websocket_device_name': config.websocket_device_name,
                'websocket_location': config.websocket_location,
                'websocket_debounce_seconds': config.websocket_debounce_seconds
            }

            with open(filename, 'w') as f:
                json.dump(config_dict, f, indent=4)

            self.status_var.set(f"Configuration saved to {filename}")
            messagebox.showinfo("Success", f"Configuration saved successfully to:\n{filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration:\n{str(e)}")

    def _load_config_file(self):
        """Load configuration from JSON file"""
        filename = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            with open(filename, 'r') as f:
                config_dict = json.load(f)

            # Update config object
            for key, value in config_dict.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)

            # Update UI (except source which needs special handling)
            self._load_config_to_ui()

            # Handle source separately
            if 'source' in config_dict:
                loaded_source = config_dict['source']
                # Check if it matches any detected camera
                source_found = False
                if isinstance(loaded_source, int) and self.available_cameras:
                    for i, cam in enumerate(self.available_cameras):
                        if cam['index'] == loaded_source:
                            self.config_widgets['source'].current(i)
                            source_found = True
                            break

                if not source_found:
                    # It's a file path or undetected camera
                    if isinstance(loaded_source, str) and not loaded_source.isdigit():
                        # File path
                        current_values = list(self.config_widgets['source']['values'])
                        file_option = f"File: {loaded_source}"
                        current_values = [v for v in current_values if not v.startswith("File:")]
                        current_values.append(file_option)
                        self.config_widgets['source'].config(values=current_values)
                        self.config_widgets['source'].set(file_option)
                        self.cameras_detected = True
                        self.run_button.config(state=tk.NORMAL)

            self.status_var.set(f"Configuration loaded from {filename}")
            messagebox.showinfo("Success", f"Configuration loaded successfully from:\n{filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration:\n{str(e)}")

    def _reset_to_defaults(self):
        """Reset configuration to defaults"""
        if messagebox.askyesno("Confirm Reset", "Reset all settings to default values?"):
            self.config = MonitoringConfig()
            self._load_config_to_ui()
            self.status_var.set("Configuration reset to defaults")

    def _show_license_info(self):
        """Show detailed license information"""
        license_info = self.license_manager.get_license_info()

        if not license_info:
            messagebox.showerror("Error", "Could not load license information")
            return

        info_text = f"""License Information:

MAC Address: {license_info.get('mac_address', 'Unknown')}
Username: {license_info.get('username', 'Unknown')}
Created: {license_info.get('created', 'Unknown')}
Expires: {license_info.get('expires', 'Unknown')}
Days Remaining: {license_info.get('days_remaining', 0)}
Status: {'Valid' if license_info.get('is_valid') else 'Expired'}
"""
        messagebox.showinfo("License Information", info_text)

    def _run_monitor(self):
        """Run the monitoring system"""
        if self._monitor_is_running():
            messagebox.showwarning("Monitor Running", "The monitoring system is already running.")
            return

        # Check if cameras are detected or video file selected
        if not self.cameras_detected:
            messagebox.showwarning(
                "No Video Source",
                "Please wait for camera detection to complete or select a video file."
            )
            return

        # Validate license before running
        is_valid, message = self.license_manager.validate_license()
        if not is_valid:
            messagebox.showerror("License Error", f"Cannot run: {message}")
            return

        try:
            # Collect configuration
            config = self._collect_config_from_ui()

            # Reset stop flag
            self.stop_requested = False

            # Update UI
            self.run_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_var.set("Monitoring system running...")

            if platform.system() == "Darwin":
                self._run_monitor_process(config)
            else:
                # Run monitor in a separate thread to keep GUI responsive
                self.monitor_thread = threading.Thread(target=self._run_monitor_thread, args=(config,), daemon=True)
                self.monitor_thread.start()

        except Exception as e:
            self.monitor_process = None
            self._cleanup_monitor_config()
            messagebox.showerror("Error", f"Failed to start monitoring system:\n{str(e)}")
            self.run_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def _monitor_is_running(self) -> bool:
        """Return True when a monitor thread or child process is active."""
        if self.monitor_process is not None and self.monitor_process.poll() is None:
            return True
        return self.monitor_thread is not None and self.monitor_thread.is_alive()

    def _run_monitor_process(self, config: MonitoringConfig):
        """Run monitor in a child process so OpenCV owns the macOS main thread."""
        self._cleanup_monitor_config()
        self.monitor_config_path = self._write_monitor_config(config)

        command = [
            sys.executable,
            str(APP_DIR / "main.py"),
            "--config-file",
            self.monitor_config_path,
        ]
        self.monitor_process = subprocess.Popen(command, cwd=str(APP_DIR))

        watcher = threading.Thread(
            target=self._wait_for_monitor_process,
            args=(self.monitor_process,),
            daemon=True,
        )
        watcher.start()

    def _write_monitor_config(self, config: MonitoringConfig) -> str:
        """Write a temporary JSON config consumed by the monitor process."""
        fd, path = tempfile.mkstemp(prefix="stampede-monitor-", suffix=".json")
        with os.fdopen(fd, 'w') as f:
            json.dump(asdict(config), f, indent=2)
        return path

    def _wait_for_monitor_process(self, process: subprocess.Popen):
        """Wait for the monitor child process without blocking Tkinter."""
        return_code = process.wait()
        try:
            self.root.after(0, lambda: self._on_monitor_process_ended(process, return_code))
        except tk.TclError:
            self._cleanup_monitor_config()

    def _on_monitor_process_ended(self, process: subprocess.Popen, return_code: int):
        """Update UI after the macOS monitor process exits."""
        if self.monitor_process is not process:
            return

        self.monitor_process = None
        self._cleanup_monitor_config()

        if return_code not in (0, -signal.SIGINT) and not self.stop_requested:
            messagebox.showerror(
                "Monitor Error",
                f"Monitoring process exited with code {return_code}. Check the log for details."
            )

        self._on_monitor_ended()

    def _cleanup_monitor_config(self):
        """Remove the temporary monitor config file if it exists."""
        if not self.monitor_config_path:
            return

        try:
            os.remove(self.monitor_config_path)
        except FileNotFoundError:
            pass
        except Exception:
            pass
        finally:
            self.monitor_config_path = None

    def _run_monitor_thread(self, config: MonitoringConfig):
        """Run monitor in a separate thread"""
        try:
            # Import monitor here to avoid circular imports
            from monitor import CrowdMonitor
            from logger_config import get_logger

            logger = get_logger(__name__)
            logger.info("Starting monitoring system from GUI...")

            # Create and initialize monitor
            monitor = CrowdMonitor(config)
            self.current_monitor = monitor  # Store reference for stopping

            # Pass the stop flag function to the monitor
            monitor.should_stop = lambda: self.stop_requested

            # Run the monitor (this will block until quit or error)
            success = monitor.initialize()

            if not success and not self.stop_requested:
                try:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Monitor Error",
                        "Failed to initialize monitoring system. Check the log for details."
                    ))
                except tk.TclError:
                    pass
            
        except Exception as e:
            if not self.stop_requested:
                try:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Monitor Error",
                        f"Error running monitor:\n{str(e)}"
                    ))
                except tk.TclError:
                    pass
        finally:
            # Update UI when monitor ends
            try:
                self.root.after(0, self._on_monitor_ended)
            except tk.TclError:
                pass

    def _on_monitor_ended(self):
        """Called when monitoring ends"""
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Monitoring system stopped")
        self.current_monitor = None

    def _stop_monitor(self):
        """Stop the monitoring system"""
        try:
            if self.monitor_process is not None and self.monitor_process.poll() is None:
                self.stop_requested = True
                self.status_var.set("Stopping monitoring system...")
                self.stop_button.config(state=tk.DISABLED)
                self.monitor_process.send_signal(signal.SIGINT)
                self.root.after(5000, self._terminate_monitor_process_if_needed)
                return

            # Set the stop flag - the monitor thread will check this and exit gracefully
            self.stop_requested = True

            self.status_var.set("Stopping monitoring system...")
            self.stop_button.config(state=tk.DISABLED)

            # Monitor thread will detect the flag and exit
            # UI will be updated by _on_monitor_ended

        except Exception as e:
            messagebox.showerror("Error", f"Error stopping monitor:\n{str(e)}")
            # Force UI update
            self.run_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_var.set("Monitor stopped")

    def _terminate_monitor_process_if_needed(self):
        """Escalate to SIGTERM if the monitor child ignored SIGINT."""
        process = self.monitor_process
        if process is None or process.poll() is not None:
            return

        process.terminate()
        self.root.after(2000, self._kill_monitor_process_if_needed)

    def _kill_monitor_process_if_needed(self):
        """Force-kill the monitor child only after graceful shutdown fails."""
        process = self.monitor_process
        if process is None or process.poll() is not None:
            return

        process.kill()

    def _on_close(self):
        """Close the configuration UI without implicitly stopping monitoring."""
        if self._monitor_is_running():
            if self.monitor_process is not None and self.monitor_process.poll() is None:
                if not messagebox.askyesno(
                        "Exit",
                        "Monitoring is still running. Close the configuration UI and leave it running?\n\nUse Stop Monitor before exiting if you want to close the room."
                ):
                    return
                self.monitor_process = None
                self.root.destroy()
                return

            messagebox.showwarning(
                "Monitor Running",
                "Monitoring is still running inside this UI process. Use Stop Monitor before closing the window."
            )
            return

        self._cleanup_monitor_config()
        self.root.destroy()

    def run(self):
        """Run the GUI application"""
        self.root.mainloop()


def main():
    """Main entry point for GUI"""
    root = tk.Tk()
    app = ConfigurationGUI(root)
    app.run()


if __name__ == "__main__":
    main()
