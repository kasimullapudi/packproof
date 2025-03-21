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

    # Configure the frame to center its contents
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    # Scan for Wi‑Fi networks
    networks = wifi_ssids.scan_wifi_networks()
    active_network = next((net for net in networks if net.get('active', '').lower() == 'yes'), None)
    is_connected = active_network is not None
    ssid = active_network.get('ssid', 'Unknown') if is_connected else ''

    # Set status message based on connection status
    label_text = f"Wi‑Fi Connected:\n {ssid}" if is_connected else "Please connect to a Wi‑Fi network"
    status_label = ttk.Label(frame, text=label_text, font=("Arial", 16), anchor="center", justify="center")
    status_label.grid(row=0, column=0, pady=20)

    # After a delay, call the appropriate callback (routing is done in main.py)
    delay_ms = 2000  # 2-second delay
    if is_connected:
        root.after(delay_ms, on_connected)
    else:
        root.after(delay_ms, on_not_connected)
