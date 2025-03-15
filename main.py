import tkinter as tk
from index import show_index_page
import wifi_ssids
import wifi_server
import recorder

class MainApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Wiâ€‘Fi & Video Manager")
        self.root.attributes("-fullscreen", True)  # Fullscreen mode
        self.root.bind("<Escape>", lambda e: root.destroy())  # Exit on Esc (optional)
        # self.root.geometry("800x600")
        
        # Start by displaying the index page
        self.show_index_page()

    def show_index_page(self):
        # show_index_page takes two callbacks for routing
        show_index_page(self.root, self.on_connected, self.on_not_connected)

    def on_connected(self):
        """
        Called when Wiâ€‘Fi is detected.
        Routes directly to the recorder page.
        """
        # Clear current widgets and show recorder page
        for widget in self.root.winfo_children():
            widget.destroy()
        self.recorder_app = recorder.VideoRecorderApp(self.root)

    def on_not_connected(self):
        """
        Called when no active Wiâ€‘Fi connection is detected.
        Routes to the Wiâ€‘Fi selection page (wifi_ssids.py).
        """
        # Clear current widgets and show Wiâ€‘Fi SSIDs page
        for widget in self.root.winfo_children():
            widget.destroy()
        wifi_ssids.show_wifi_page(self.root, self.on_wifi_selected)

    def on_wifi_selected(self, ssid):
        """
        Callback when a Wiâ€‘Fi is selected from the Wiâ€‘Fi list.
        Routes to the Wiâ€‘Fi connection page (wifi_server.py).
        """
        for widget in self.root.winfo_children():
            widget.destroy()
        wifi_server.show_wifi_page(self.root, self.on_wifi_connection_success, selected_ssid=ssid)

    def on_wifi_connection_success(self, ssid):
        """
        Callback when Wiâ€‘Fi connection is successful.
        Routes to the recorder page.
        """
        for widget in self.root.winfo_children():
            widget.destroy()
        self.recorder_app = recorder.VideoRecorderApp(self.root)

if __name__ == "__main__":
    app = MainApplication()
    app.root.mainloop()
