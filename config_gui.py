"""
GUI application for managing crowd monitoring system configuration.
Allows users to easily configure all parameters and run the system.
With MAC-based license protection.
"""

import json
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Any, Optional

from auth.license_manager import LicenseManager
from config import MonitoringConfig

sys.path.insert(0, 'auth')


class LicenseDialog:
    """Dialog for entering and activating license"""

    def __init__(self, parent):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("License Activation Required")
        self.dialog.geometry("500x300")
        self.dialog.resizable(False, False)

        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"500x300+{x}+{y}")

        self._setup_ui()

    def _setup_ui(self):
        """Setup the license dialog UI"""
        # Title
        title_frame = ttk.Frame(self.dialog)
        title_frame.pack(fill=tk.X, padx=20, pady=20)

        ttk.Label(title_frame,
                  text="License Activation Required",
                  font=("", 14, "bold")).pack()

        ttk.Label(title_frame,
                  text="Please enter your license key to activate the application",
                  font=("", 9)).pack(pady=(5, 0))

        # Machine info
        info_frame = ttk.LabelFrame(self.dialog, text="Machine Information", padding=10)
        info_frame.pack(fill=tk.X, padx=20, pady=10)

        import os
        license_path = os.path.join('auth', 'license.dat')
        manager = LicenseManager(license_file=license_path)

        info_text = f"MAC Address: {manager.get_mac_address()}\n"
        info_text += f"Machine ID: {manager.get_machine_id()[:16]}..."

        ttk.Label(info_frame, text=info_text, font=("Courier", 8)).pack()

        # License key entry
        key_frame = ttk.Frame(self.dialog)
        key_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(key_frame, text="License Key:").pack(anchor=tk.W)

        self.license_text = tk.Text(key_frame, height=4, wrap=tk.WORD)
        self.license_text.pack(fill=tk.X, pady=(5, 0))

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=20)

        ttk.Button(button_frame, text="Activate",
                   command=self._activate).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel",
                   command=self._cancel).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Request License",
                   command=self._request_license).pack(side=tk.LEFT)

    def _request_license(self):
        """Show information for requesting a license"""
        import os
        license_path = os.path.join('auth', 'license.dat')
        manager = LicenseManager(license_file=license_path)

        info = f"""To request a license, please send the following information to support:

Machine ID: {manager.get_machine_id()}
MAC Address: {manager.get_mac_address()}

Email: support@yourcompany.com
"""
        messagebox.showinfo("Request License", info)

    def _activate(self):
        """Activate the license"""
        license_key = self.license_text.get("1.0", tk.END).strip()

        if not license_key:
            messagebox.showerror("Error", "Please enter a license key")
            return

        import os
        license_path = os.path.join('auth', 'license.dat')
        manager = LicenseManager(license_file=license_path)

        # Try to save and validate the license
        if manager.save_license(license_key):
            is_valid, message = manager.validate_license()

            if is_valid:
                self.result = True
                messagebox.showinfo("Success", "License activated successfully!")
                self.dialog.destroy()
            else:
                messagebox.showerror("Invalid License", message)
                self.result = False
        else:
            messagebox.showerror("Error", "Failed to save license file")
            self.result = False

    def _cancel(self):
        """Cancel activation"""
        self.result = False
        self.dialog.destroy()

    def show(self):
        """Show the dialog and return result"""
        self.dialog.wait_window()
        return self.result


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
        self.root.geometry("1000x800")

        # Initialize license manager with correct path
        import os
        license_path = os.path.join('auth', 'license.dat')
        self.license_manager = LicenseManager(license_file=license_path)

        # Check license before showing UI
        if not self._check_license():
            self.root.destroy()
            return

        # Configuration storage
        self.config = MonitoringConfig()
        self.config_widgets: Dict[str, tk.Widget] = {}
        self.process: Optional[subprocess.Popen] = None
        self.output_thread: Optional[threading.Thread] = None

        # Setup UI
        self._setup_ui()

        # Load default values
        self._load_config_to_ui()

        # Start periodic license check
        self._schedule_license_check()

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

            dialog = LicenseDialog(self.root)
            result = dialog.show()

            if not result:
                messagebox.showerror(
                    "License Required",
                    "A valid license is required to use this application."
                )
                return False

            return True

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

        # Run button (prominent)
        self.run_button = ttk.Button(button_frame, text="▶ Run Monitor",
                                     command=self._run_monitor, style="Accent.TButton")
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
        canvas = tk.Canvas(frame)
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
        self.config_widgets['source'] = ttk.Entry(source_frame, width=30)
        self.config_widgets['source'].pack(side=tk.LEFT, padx=5)
        ttk.Button(source_frame, text="Browse", command=self._browse_video_source).pack(side=tk.LEFT)
        ttk.Label(scrollable_frame, text="Camera index (0, 1, 2) or video file path").grid(row=row, column=2,
                                                                                           sticky=tk.W, padx=10)

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

        canvas = tk.Canvas(frame)
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

        canvas = tk.Canvas(frame)
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

        canvas = tk.Canvas(frame)
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

        canvas = tk.Canvas(frame)
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

        canvas = tk.Canvas(frame)
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

        canvas = tk.Canvas(frame)
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

        canvas = tk.Canvas(frame)
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

    def _browse_video_source(self):
        """Browse for video source file"""
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        )
        if filename:
            self.config_widgets['source'].delete(0, tk.END)
            self.config_widgets['source'].insert(0, filename)

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
        # Video source
        self._set_widget_value('source', self.config.source)
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
        elif isinstance(widget, (ttk.Entry, ttk.Spinbox, ttk.Combobox)):
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

        source = self._get_widget_value('source')

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
            calibration_line_thickness=to_int(self._get_widget_value('calibration_line_thickness'))
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
                'calibration_line_thickness': config.calibration_line_thickness
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

            # Update UI
            self._load_config_to_ui()

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
        # Validate license before running
        is_valid, message = self.license_manager.validate_license()
        if not is_valid:
            messagebox.showerror("License Error", f"Cannot run: {message}")
            return

        try:
            # Collect configuration
            config = self._collect_config_from_ui()

            # Build command line arguments
            args = [
                sys.executable, "main.py",
                "--source", str(config.source),
                "--model", config.model_path,
                "--cell-width", str(config.cell_width),
                "--cell-height", str(config.cell_height),
                "--person-radius", str(config.person_radius),
                "--detect-every", str(config.detect_every),
                "--conf", str(config.confidence_threshold),
                "--min-bbox-area", str(config.min_bbox_area),
                "--max-age", str(config.max_age),
                "--n-init", str(config.n_init),
                "--ema-alpha", str(config.ema_alpha),
                "--fps", str(config.fps),
                "--hysteresis", str(config.hysteresis_time)
            ]

            if config.use_deepsort:
                args.append("--use-deepsort")
            if not config.enable_screenshots:
                args.append("--disable-screenshots")
            if not config.enable_grid_adjustment:
                args.append("--disable-grid-adjustment")

            # Add calibration parameters
            args.extend([
                "--calibration-width", str(config.calibration_area_width),
                "--calibration-height", str(config.calibration_area_height)
            ])
            if config.auto_calibration:
                args.append("--auto-calibration")

            # Start process
            self.process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Update UI
            self.run_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_var.set("Monitoring system running...")

            # Start output monitoring thread
            self.output_thread = threading.Thread(target=self._monitor_process_output, daemon=True)
            self.output_thread.start()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start monitoring system:\n{str(e)}")

    def _monitor_process_output(self):
        """Monitor process output in background thread"""
        try:
            if self.process:
                for line in self.process.stdout:
                    print(line, end='')

                self.process.wait()

                # Update UI when process ends
                self.root.after(0, self._on_process_ended)

        except Exception as e:
            print(f"Error monitoring process: {e}")

    def _on_process_ended(self):
        """Called when monitoring process ends"""
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Monitoring system stopped")
        self.process = None

    def _stop_monitor(self):
        """Stop the monitoring system"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()

            self.process = None
            self.run_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_var.set("Monitoring system stopped")

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
