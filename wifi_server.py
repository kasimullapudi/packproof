import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import subprocess
import wifi_ssids

def show_wifi_page(root, on_success, selected_ssid="", back_callback=None):
    # If no back_callback provided, default to on_success (for backwards compatibility)
    if back_callback is None:
        back_callback = on_success

    print("Received SSID:", selected_ssid)  # Print the passed SSID to console
    root.geometry("480x320")
    for widget in root.winfo_children():
        widget.destroy()

    # Main container
    main_frame = tb.Frame(root)
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)
    # Back Button (Positioned at Top-Left Corner)
    back_button = tb.Button(
        main_frame,
        text="← Back",
        command=lambda: wifi_ssids.show_wifi_page(root, back_callback),  # Go back to Wi-Fi list
        bootstyle="danger",
        width=10
    )
    back_button.pack(anchor="w", padx=5, pady=5)  # Align left
    # Title Label
    title_label = tb.Label(main_frame, text="Wi-Fi Connector", font=("Arial", 18, "bold"))
    title_label.pack(pady=15)
    
    # Display SSID at the top instead of asking for input
    ssid_label = tb.Label(main_frame, text=f"Connected to: {selected_ssid}", font=("Arial", 14, "bold"))
    ssid_label.pack(pady=10)

    # Password Entry
    password_frame = tb.Frame(main_frame)
    password_frame.pack(fill="x", pady=5)
    tb.Label(password_frame, text="Password:", font=("Arial", 12)).pack(side=tk.LEFT)
    entry_frame = tb.Frame(password_frame)
    entry_frame.pack(side=tk.RIGHT)

    password_entry = tb.Entry(entry_frame, width=20, show="*")
    password_entry.pack(side=tk.LEFT)

    # Toggle button for password
    def toggle_password():
        if password_entry.cget("show") == "*":
            password_entry.config(show="")
            toggle_button.config(text="Hide")
        else:
            password_entry.config(show="*")
            toggle_button.config(text="Show")

    toggle_button = tb.Button(
        entry_frame, 
        text="Show", 
        command=toggle_password,
        width=6,
        bootstyle="outline"
    )
    toggle_button.pack(side=tk.LEFT, padx=5)

    # Function to connect to Wi-Fi
    def connect_wifi():
        ssid = selected_ssid  # Use the SSID received from wifi_ssids.py
        password = password_entry.get().strip()
        if not ssid or not password:
            tb.dialogs.Messagebox.show_error("SSID and Password cannot be empty!", title="Error")
            return
        command = ['pkexec', 'nmcli', 'device', 'wifi', 'connect', ssid, 'password', password]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            tb.dialogs.Messagebox.show_info(f"Connected to {ssid}!", title="Success")
            # Pass the ssid to the on_success callback to redirect to recorder.py
            on_success(ssid)
        else:
            tb.dialogs.Messagebox.show_error(f"Failed to connect:\n{result.stderr.strip()}", title="Error")

    # Connect Button
    connect_button = tb.Button(
        main_frame, 
        text="Connect", 
        command=connect_wifi,
        bootstyle="success",
        width=15
    )
    connect_button.pack(pady=20)
