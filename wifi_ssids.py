import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import subprocess
import tkinter as tk

def scan_wifi_networks():
    """Scans available Wi-Fi networks using nmcli and returns a sorted list."""
    command = ['nmcli', '-t', '-f', 'SSID,SIGNAL,ACTIVE', 'dev', 'wifi']
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    lines = result.stdout.strip().split("\n")
    wifi_networks = []
    for line in lines:
        if not line.strip():
            continue
        # Split only twice so that SSIDs containing colons are preserved
        parts = line.split(":", 2)
        ssid = parts[0] if len(parts) > 0 else ''
        signal = parts[1] if len(parts) > 1 else '0'
        active = parts[2] if len(parts) > 2 else ''
        try:
            signal_int = int(signal)
        except ValueError:
            signal_int = 0
        wifi_networks.append({
            'ssid': ssid,
            'signal': signal_int,
            'active': active
        })
    # Sort networks by signal strength (descending)
    wifi_networks_sorted = sorted(wifi_networks, key=lambda x: x['signal'], reverse=True)
    return wifi_networks_sorted

def show_wifi_page(parent, on_wifi_selected):
    """
    Builds the Wi-Fi selection page inside the provided parent widget.
    When a Wi-Fi is clicked, on_wifi_selected(ssid) is called.
    """
    # Clear parent's content
    for widget in parent.winfo_children():
        widget.destroy()

    # Header
    header_frame = ttk.Frame(parent)
    header_frame.pack(side=TOP, fill="x", pady=(10,0))
    title_label = ttk.Label(header_frame, text="Select Wi-Fi", font=("Arial", 16, "bold"))
    title_label.pack()

    # Scrollable content area
    content_frame = ttk.Frame(parent)
    content_frame.pack(side=TOP, fill="both", expand=True, padx=10, pady=10)
    canvas = tk.Canvas(content_frame, bg="white", highlightthickness=0)
    canvas.pack(side=LEFT, fill="both", expand=True)
    scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side=RIGHT, fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)
    wifi_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=wifi_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    wifi_frame.bind("<Configure>", on_frame_configure)

    # List Wi-Fi networks
    wifi_list = scan_wifi_networks()
    if not wifi_list:
        no_wifi_label = ttk.Label(wifi_frame, text="No Wi-Fi networks found", font=("Arial", 12), foreground="danger")
        no_wifi_label.pack(pady=10)
    else:
        for wifi in wifi_list:
            display_text = f"{wifi['ssid']} (Signal: {wifi['signal']}%)"
            if wifi['active'].lower() == 'yes':
                display_text += " (Connected)"
            wifi_button = ttk.Button(
                wifi_frame,
                text=display_text,
                command=lambda ssid=wifi['ssid']: on_wifi_selected(ssid),
                bootstyle="primary",
                style="Left.TButton"  # Custom style for left-aligned text
            )
            wifi_button.pack(pady=5, fill="x", padx=5)

    # Custom style for left-aligned button text
    style_obj = ttk.Style()
    style_obj.layout(
        "Left.TButton",
        [
            ("TButton.border", {"sticky": "nswe", "children": [
                ("TButton.focus", {"sticky": "nswe", "children": [
                    ("TButton.label", {"sticky": "w", "expand": 1})
                ]})
            ]})
        ]
    )

    # Fixed Refresh Button (green success style)
    refresh_button = ttk.Button(parent, text="Refresh", command=lambda: show_wifi_page(parent, on_wifi_selected), bootstyle="success")
    refresh_button.pack(side="bottom", fill="x", padx=10, pady=10)
