import os
import datetime
import time
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkbs
from PIL import Image, ImageTk
recStart=0
recActStart=0

# =================== Raspberry Pi (uncomment these lines when using on Raspberry Pi) ===================
# from picamera2 import Picamera2
# from picamera2.encoders import H264Encoder
# from picamera2.outputs import FfmpegOutput

# =================== Laptop (uncomment these lines when using on your laptop) ===================
import cv2  # OpenCV for webcam capture on laptop

class VideoRecorderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Camera Recorder")
        self.style = ttkbs.Style(theme="darkly")
        
        # ------------------ Raspberry Pi Setup ------------------
        # self.picam2 = Picamera2()
        # self.preview_config = self.picam2.create_video_configuration(
        #     main={"size": (640, 360)},
        #     controls={"FrameRate": 24}
        # )
        # self.recording_config = self.picam2.create_video_configuration(
        #     main={"size": (1920, 1080)},
        #     controls={"FrameRate": 24}
        # )
        # self.encoder = H264Encoder(bitrate=4000000, repeat=True, iperiod=15)
        
        # ------------------ Laptop Setup ------------------
        self.cap = None   # VideoCapture for laptop webcam
        self.out = None   # VideoWriter for saving the recording
        
        self.recording = False
        self.start_time = None
        self.order_id = ""
        
        # Create two frames: one for the Order ID input and one for preview/recording.
        self.start_frame = ttk.Frame(master)
        self.record_frame = ttk.Frame(master)
        self.create_start_frame()
        self.create_record_frame()
        
        # Show the start frame first.
        self.start_frame.pack(expand=True, fill=tk.BOTH)
    
    def create_start_frame(self):
        """Create the first page: Order ID input and READY button."""
        order_id_label = ttk.Label(self.start_frame, text="Order ID:", font=("Arial", 14))
        order_id_label.pack(pady=10)
        self.order_id_entry = ttk.Entry(self.start_frame, font=("Arial", 14), width=20)
        self.order_id_entry.pack(pady=10)
        self.ready_btn = ttk.Button(
            self.start_frame,
            text="READY",
            command=self.ready_pressed,
            bootstyle="primary",
            width=20
        )
        self.ready_btn.pack(pady=20)
    
    def create_record_frame(self):
        """Create the second page: Video preview, timer, and recording controls."""
        # Video preview area
        self.preview_label = ttk.Label(self.record_frame)
        self.preview_label.pack(pady=10)
        
        # Timer label (hidden until recording starts)
        self.timer_label = ttk.Label(self.record_frame, font=('Helvetica', 24), anchor=tk.CENTER)
        self.timer_label.pack(pady=10)
        self.timer_label.pack_forget()
        
        # Control buttons frame
        self.control_frame = ttk.Frame(self.record_frame)
        self.control_frame.pack(pady=10)
        self.start_btn = ttk.Button(
            self.control_frame,
            text="Start Recording",
            command=self.start_recording,
            bootstyle="success",
            width=15
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)
        self.stop_btn = ttk.Button(
            self.control_frame,
            text="Stop Recording",
            command=self.stop_recording,
            bootstyle="danger",
            state=tk.DISABLED,
            width=15
        )
        self.stop_btn.pack(side=tk.LEFT, padx=10)
    
    def ready_pressed(self):
        """Handle READY button: save and print Order ID, then switch pages."""
        self.order_id = self.order_id_entry.get().strip()
        print("Order ID:", self.order_id)
        # Switch to record frame
        self.start_frame.pack_forget()
        self.record_frame.pack(expand=True, fill=tk.BOTH)
        self.start_preview()
    
    def start_preview(self):
        """Start video preview."""
        # ------------------ Raspberry Pi Preview ------------------
        # self.picam2.configure(self.preview_config)
        # self.picam2.start()
        # self.update_preview()
        
        # ------------------ Laptop Preview ------------------
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(0)
        # Force a lower resolution for preview
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
        self.update_preview()
    
    def update_preview(self):
        """Continuously update the preview image."""
        # ------------------ Raspberry Pi Preview ------------------
        # if not self.recording and self.picam2.started:
        #     try:
        #         image = self.picam2.capture_array("main")
        #         image = Image.fromarray(image)
        #         image.thumbnail((640, 360))
        #         photo = ImageTk.PhotoImage(image)
        #         self.preview_label.config(image=photo)
        #         self.preview_label.image = photo
        #     except Exception as e:
        #         print(f"Preview error: {e}")
        
        # ------------------ Laptop Preview ------------------
        if not self.recording and self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame)
                image.thumbnail((640, 360))
                photo = ImageTk.PhotoImage(image)
                self.preview_label.config(image=photo)
                self.preview_label.image = photo
        self.master.after(66, self.update_preview)
    
    def start_recording(self):
        """Begin recording: show timer, disable Start button, enable Stop."""
        self.recording = True
        print("clicked start recording")
        recStart=datetime.datetime.now().strftime("%H:%M:%S")
        print(recStart)
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.timer_label.pack(pady=10)
        self.start_time = time.time()
        self.update_timer()
        
        # ------------------ Raspberry Pi Recording ------------------
        # self.picam2.stop()
        # self.picam2.configure(self.recording_config)
        # self.picam2.start()
        # filename = f"videos/{self.order_id}.mp4" if self.order_id else f"videos/video_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        # os.makedirs("videos", exist_ok=True)
        # self.output = FfmpegOutput(filename, audio=False)
        # self.picam2.start_encoder(self.encoder, self.output)
        
        # ------------------ Laptop Recording ------------------
        os.makedirs("videos", exist_ok=True)
        filename = f"videos/{self.order_id}.mp4" if self.order_id else f"videos/video_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(0)
        # Optionally, try to set a higher resolution (if supported by your webcam)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        # Allow the camera to initialize
        time.sleep(0.5)
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to capture frame for recording.")
            return
        recActStart=datetime.datetime.now().strftime("%H:%M:%S")
        print("actual record time is: ",recActStart)
        print(datetime.datetime.strptime(recActStart,"%H:%M:%S")-datetime.datetime.strptime(recStart,"%H:%M:%S"))
        # Use the actual resolution from the captured frame
        height, width = frame.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(filename, fourcc, 24.0, (width, height))
        
        self.update_recording()
    
    def update_recording(self):
        """Capture frames and write them to the video file."""
        if self.recording and self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                self.out.write(frame)
            else:
                print("Recording error: Unable to read frame")
            self.master.after(41, self.update_recording)
    
    def stop_recording(self):
        """Stop recording, release resources, hide timer, and update UI."""
        self.recording = False
        time.sleep(0.5)
        
        # ------------------ Raspberry Pi Stop Recording ------------------
        # self.picam2.stop_encoder()
        # self.picam2.stop()
        
        # ------------------ Laptop Stop Recording ------------------
        if self.cap is not None:
            self.cap.release()
        if self.out is not None:
            self.out.release()
        
        self.timer_label.pack_forget()
        status = ttk.Label(self.record_frame, text="Recording Stopped", font=('Helvetica', 12))
        status.pack(pady=10)
        self.master.after(2000, lambda: status.destroy())
        
        # Reset button states: enable Start, disable Stop.
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def update_timer(self):
        """Update and display the elapsed recording time."""
        if self.recording:
            elapsed = time.time() - self.start_time
            mins, secs = divmod(int(elapsed), 60)
            self.timer_label.config(text=f"{mins:02}:{secs:02}")
            self.master.after(1000, self.update_timer)
    
    def on_close(self):
        if self.cap is not None:
            self.cap.release()
        self.master.destroy()

if __name__ == "__main__":
    root = ttkbs.Window(themename="darkly")
    root.geometry("800x600")
    app = VideoRecorderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
