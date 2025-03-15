import os
import datetime
import time
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkbs
from PIL import Image, ImageTk
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

if 'DISPLAY' not in os.environ:
    os.environ['DISPLAY'] = ':0'

class VideoRecorderApp:
    def __init__(self, master):
        self.root = master
        self.root.title("Pi Camera Recorder")
        self.style = ttkbs.Style(theme="darkly")
        
        # Camera configuration optimized for Pi Zero 2 W
        self.picam2 = Picamera2()
        self.preview_config = self.picam2.create_video_configuration(
            main={"size": (640, 360)},  # Low-res preview
            controls={"FrameRate": 24}  # Reduced FPS for performance
        )
        self.recording_config = self.picam2.create_video_configuration(
            main={"size": (1920, 1080)},  # Full HD recording
            controls={"FrameRate": 24}  # Match preview FPS
        )
        
        # Encoder settings for stable recording
        self.encoder = H264Encoder(
            bitrate=4000000,  # 4Mbps for SD card compatibility
            repeat=True,       # Better keyframe handling
            iperiod=15         # Keyframe interval
        )
        self.recording = False
        self.start_time = None
        
        # Initialize GUI
        self.create_widgets()
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    def create_widgets(self):
        """Create and layout all GUI elements"""
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Centered content frame
        self.center_frame = ttk.Frame(self.main_frame)
        self.center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Order ID input (new field above READY)
        order_id_frame = ttk.Frame(self.center_frame)
        order_id_frame.pack(pady=10)
        order_id_label = ttk.Label(order_id_frame, text="Order ID:", font=("Arial", 14))
        order_id_label.pack(side=tk.LEFT, padx=(0,5))
        self.order_id_entry = ttk.Entry(order_id_frame, font=("Arial", 14), width=20)
        self.order_id_entry.pack(side=tk.LEFT)
        
        # READY button (initial state)
        self.ready_btn = ttk.Button(
            self.center_frame,
            text="READY",
            command=self.start_preview,
            bootstyle="primary",
            width=20
        )
        self.ready_btn.pack(pady=20)
        
        # Preview label (hidden initially)
        self.preview_label = ttk.Label(self.center_frame)
        
        # Control buttons frame (hidden initially)
        self.btn_frame = ttk.Frame(self.center_frame)
        self.start_btn = ttk.Button(
            self.btn_frame,
            text="Start Recording",
            command=self.start_recording,
            bootstyle="success",
            width=15
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)
        self.stop_btn = ttk.Button(
            self.btn_frame,
            text="Stop Recording",
            command=self.stop_recording,
            bootstyle="danger",
            state=tk.DISABLED,
            width=15
        )
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        # Timer label (hidden initially)
        self.timer_label = ttk.Label(
            self.center_frame,
            font=('Helvetica', 24),
            anchor=tk.CENTER
        )
        
        # Status label (hidden initially)
        self.status_label = ttk.Label(
            self.center_frame,
            anchor=tk.CENTER,
            font=('Helvetica', 12)
        )

    def start_preview(self):
        """Show preview when READY is clicked"""
        try:
            self.ready_btn.pack_forget()
            self.preview_label.pack(pady=10)
            self.btn_frame.pack(pady=20)
            self.picam2.configure(self.preview_config)
            self.picam2.start()
            self.update_preview()
        except Exception as e:
            self.show_error(f"Camera Error: {str(e)}")

    def update_preview(self):
        """Update preview image"""
        if not self.recording and self.picam2.started:
            try:
                image = self.picam2.capture_array("main")
                image = Image.fromarray(image)
                image.thumbnail((640, 360))  # Force resize for performance
                photo = ImageTk.PhotoImage(image)
                self.preview_label.config(image=photo)
                self.preview_label.image = photo
            except Exception as e:
                print(f"Preview error: {e}")
        
        # Update at 15fps (66ms interval)
        self.root.after(66, self.update_preview)

    def start_recording(self):
        """Start recording with proper synchronization"""
        self.recording = True
        self.preview_label.pack_forget()
        self.btn_frame.pack_forget()
        
        try:
            # Stop preview and reconfigure for recording
            self.picam2.stop()
            self.picam2.configure(self.recording_config)
            self.picam2.start()
            
            # Create output file using the order id from the input field
            os.makedirs("videos", exist_ok=True)
            order_id = self.order_id_entry.get().strip()
            if order_id:
                filename = f"videos/{order_id}.mp4"
            else:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"videos/video_{timestamp}.mp4"
            
            # Initialize FfmpegOutput without 'sync' parameter
            self.output = FfmpegOutput(filename, audio=False)
            self.picam2.start_encoder(self.encoder, self.output)
            
            # Show timer and update UI
            self.timer_label.pack(pady=20)
            self.start_time = time.time()
            self.update_timer()
            
            # Update button states
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            self.show_error(f"Recording Error: {str(e)}")
            self.recording = False

    def stop_recording(self):
        """Stop recording and clean up"""
        self.recording = False
        try:
            # Allow time for final frames to write
            time.sleep(0.5)
            self.picam2.stop_encoder()
            self.picam2.stop()
            
            # Update UI
            self.timer_label.pack_forget()
            self.status_label.config(text="Recording Stopped")
            self.status_label.pack(pady=20)
            
            # Reset UI after delay
            self.root.after(2000, self.reset_ui)
            
        except Exception as e:
            self.show_error(f"Stop Error: {str(e)}")

    def update_timer(self):
        """Update recording timer"""
        if self.recording:
            elapsed = time.time() - self.start_time
            mins, secs = divmod(int(elapsed), 60)
            self.timer_label.config(text=f"{mins:02}:{secs:02}")
            self.root.after(1000, self.update_timer)

    def reset_ui(self):
        """Reset UI to initial state"""
        self.status_label.pack_forget()
        self.ready_btn.pack(pady=20)
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def show_error(self, message):
        """Display error messages"""
        self.status_label.config(text=message)
        self.status_label.pack(pady=20)
        self.root.after(3000, lambda: self.status_label.pack_forget())

    def on_close(self):
        """Clean shutdown procedure"""
        if self.picam2.started:
            self.picam2.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = ttkbs.Window(themename="darkly")
    root.geometry("800x600")
    app = VideoRecorderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
