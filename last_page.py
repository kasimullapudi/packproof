import os
import requests
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkbs
from threading import Thread

# Server URL (replace with your actual server IP)
SERVER_URL = "http://192.168.31.204:5000/upload"

class VideoActions:
    def __init__(self, root):
        self.root = root
        self.videos_folder = "videos"
        self.latest_video = self.get_latest_video()
        if not self.latest_video:
            NoVideoPopup(self.root)
        else:
            self.create_widgets()

    def get_latest_video(self):
        """Find the most recently recorded video"""
        if not os.path.exists(self.videos_folder):
            return None
        videos = [os.path.join(self.videos_folder, f)
                  for f in os.listdir(self.videos_folder)
                  if f.endswith(".mp4")]
        return max(videos, key=os.path.getctime) if videos else None

    def create_widgets(self):
        """Create interface with video name and buttons"""
        main_container = ttk.Frame(self.root)
        main_container.pack(expand=True, fill="both", pady=20)

        # Show video name
        if self.latest_video:
            video_name = os.path.basename(self.latest_video)
            video_label = ttk.Label(
                main_container,
                text=f"Video: {video_name}",
                font=("Arial", 16, "bold")
            )
            video_label.pack(pady=10)

        # Bottom button container
        btn_container = ttk.Frame(main_container)
        btn_container.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        center_frame = ttk.Frame(btn_container)
        center_frame.pack(expand=True, anchor='center')

        btn_style = ttkbs.Style()
        btn_style.configure('TButton', font=('Helvetica', 14), padding=15)

        self.send_btn = ttk.Button(
            center_frame,
            text="Send to Server",
            command=self.send_to_server,
            bootstyle="success",
            width=20
        )
        self.send_btn.pack(side=tk.LEFT, padx=15)

        self.delete_btn = ttk.Button(
            center_frame,
            text="Delete",
            command=self.delete_video,
            bootstyle="danger",
            width=20
        )
        self.delete_btn.pack(side=tk.LEFT, padx=15)

        self.update_buttons()

    def update_buttons(self):
        """Update button states based on latest video"""
        self.latest_video = self.get_latest_video()
        state = "normal" if self.latest_video else "disabled"
        self.send_btn.config(state=state)
        self.delete_btn.config(state=state)

    def send_to_server(self):
        """Handle video upload"""
        print(f"Starting upload: {os.path.basename(self.latest_video)}")
        SendPopup(self.root, self.latest_video, self.update_buttons)

    def delete_video(self):
        """Handle video deletion"""
        print(f"Starting deletion: {os.path.basename(self.latest_video)}")
        DeletePopup(self.root, self.latest_video, self.update_buttons)

class BasePopup(ttkbs.Toplevel):
    """Base popup with centered positioning and a Record Again button"""
    def __init__(self, parent, video_path, callback):
        super().__init__(parent)
        self.video_path = video_path
        self.callback = callback
        self.center_popup()
        self.create_widgets()

    def center_popup(self):
        """Center the popup on screen"""
        self.update_idletasks()
        width, height = 400, 150
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """Create progress components and prepare Record Again button (hidden by default)"""
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300)
        self.progress.pack(pady=20)
        self.status = ttk.Label(self, text="", font=('Helvetica', 12))
        self.status.pack()
        self.resend_btn = ttk.Button(
            self, 
            text="Error, Resend",
            command=self.resend,
            bootstyle="danger",
            state="disabled"
        )
        # Record Again button (will be shown after operation completes)
        self.record_again_btn = ttk.Button(
            self,
            text="Record Again",
            command=self.record_again,
            bootstyle="primary"
        )

    def resend(self):
        """Resend the video"""
        self.destroy()
        SendPopup(self.master, self.video_path, self.callback)

    def record_again(self):
        """Route to recorder page"""
        import recorder
        if hasattr(self.master, 'picam2'):
            self.master.picam2.stop()
            self.master.picam2.close()
        for widget in self.master.winfo_children():
            widget.destroy()
        recorder.VideoRecorderApp(self.master)
        self.destroy()

    def add_record_again_button(self):
        self.record_again_btn.pack(pady=5)

class SendPopup(BasePopup):
    """Handle actual file upload with progress"""
    def __init__(self, parent, video_path, callback):
        super().__init__(parent, video_path, callback)
        self.title("Upload Progress")
        self.start_upload()

    def start_upload(self):
        """Initiate threaded upload"""
        self.status.config(text="Initializing upload...")
        Thread(target=self.upload_file, daemon=True).start()

    def upload_file(self):
        """Perform actual file upload with progress tracking"""
        try:
            with open(self.video_path, 'rb') as f:
                total_size = os.path.getsize(self.video_path)
                self.progress["maximum"] = total_size

                response = requests.post(
                    SERVER_URL,
                    files={'file': (os.path.basename(self.video_path), f)},
                    stream=True,
                    headers={'Content-Length': str(total_size)},
                    timeout=60
                )

                if response.status_code != 200:
                    raise Exception(f"HTTP Error: {response.status_code} - {response.text}")

                uploaded = 0
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        uploaded += len(chunk)
                        self.progress["value"] = uploaded
                        self.status.config(
                            text=f"Uploading: {uploaded/total_size:.0%}"
                        )
                        self.update_idletasks()

                self.complete_operation("Upload complete!", True)

        except Exception as e:
            print(f"Upload Error: {str(e)}")
            self.complete_operation(f"Error: {str(e)}", False)

    def complete_operation(self, message, success):
        """Finalize upload operation"""
        video_name = os.path.basename(self.video_path)
        self.status.config(text=f"{message}\n{video_name}")
        self.progress["value"] = self.progress["maximum"] if success else 0
        if not success:
            self.resend_btn.pack(pady=10)
            self.resend_btn.config(state="normal")
        self.add_record_again_button()
        self.callback()

class DeletePopup(BasePopup):
    """Handle immediate file deletion"""
    def __init__(self, parent, video_path, callback):
        super().__init__(parent, video_path, callback)
        self.title("Deletion Progress")
        self.start_deletion()

    def start_deletion(self):
        """Perform immediate file deletion"""
        try:
            video_name = os.path.basename(self.video_path)
            if os.path.exists(self.video_path):
                os.remove(self.video_path)
                self.status.config(text=f"Deletion successful!\n{video_name}")
                self.progress["value"] = 100
            else:
                self.status.config(text=f"File not found!\n{video_name}")
                self.progress["value"] = 0
        except Exception as e:
            self.status.config(text=f"Error: {str(e)}")
            self.progress["value"] = 0

        self.resend_btn.pack_forget()  # No resend option for deletion
        self.add_record_again_button()
        self.callback()

class NoVideoPopup(ttkbs.Toplevel):
    """Popup shown when no video is found, with a Record Again button"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("No Videos Found")
        self.center_popup()
        label = ttk.Label(self, text="No videos found, record again", font=('Helvetica', 12))
        label.pack(pady=20)
        record_btn = ttk.Button(self, text="Record Again", command=self.record_again, bootstyle="primary")
        record_btn.pack(pady=10)

    def center_popup(self):
        """Center the popup on screen"""
        self.update_idletasks()
        width, height = 400, 150
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def record_again(self):
        import recorder
        if hasattr(self.master, 'picam2'):
            self.master.picam2.stop()
            self.master.picam2.close()
        for widget in self.master.winfo_children():
            widget.destroy()
        recorder.VideoRecorderApp(self.master)
        self.destroy()
if __name__ == "__main__":
    root = ttkbs.Window(themename="darkly")
    root.attributes("-fullscreen", True)
    VideoActions(root)
    root.mainloop()
