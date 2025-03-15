import tkinter as tk
from tkinter import ttk
import wifi_ssids  # Reusing the scan function from your existing module

def show_index_page(root, on_connected, on_not_connected):
    """
    Displays the initial index page.

    It checks for an active Wi‑Fi connection. If found, shows "Wi‑Fi Connected" and calls on_connected;
    otherwise, shows "Please connect to a Wi‑Fi network" and calls on_not_connected.

    Args:
        root: The Tkinter root widget.
        on_connected: Callback to route to the recorder page.
        on_not_connected: Callback to route to the Wi‑Fi selection page.
    """
    # Clear any existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Create a container frame
    frame = ttk.Frame(root, padding=20)
    frame.pack(expand=True, fill='both')

    # Scan for Wi‑Fi networks
    networks = wifi_ssids.scan_wifi_networks()
    # Determine if any network is active
    is_connected = any(net.get('active', '').lower() == 'yes' for net in networks)

    # Set status message based on connection status
    label_text = "Wi‑Fi Connected" if is_connected else "Please connect to a Wi‑Fi network"
    status_label = ttk.Label(frame, text=label_text, font=("Arial", 16))
    status_label.pack(pady=20)

    # After a delay, call the appropriate callback (routing is done in main.py)
    delay_ms = 2000  # 2-second delay
    if is_connected:
        root.after(delay_ms, on_connected)
    else:
        root.after(delay_ms, on_not_connected)
