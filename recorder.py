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

class VideoRecorderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Camera Recorder")
        self.style = ttkbs.Style(theme="darkly")
        
        # Camera setup
        self.picam2 = Picamera2()
        self.preview_config = self.picam2.create_video_configuration(
            main={"size": (640, 360)},
            controls={"FrameRate": 24}
        )
        self.recording_config = self.picam2.create_video_configuration(
            main={"size": (1920, 1080)},
            controls={"FrameRate": 24}
        )
        self.encoder = H264Encoder(bitrate=4000000, repeat=True, iperiod=15)
        
        # Timing variables
        self.recStart = None
        self.recActStart = None
        self.recording = False
        self.start_time = None
        
        # GUI components
        self.order_id = ""
        self.create_widgets()
        self.start_preview()

    def create_widgets(self):
        self.start_frame = ttk.Frame(self.master)
        ttk.Label(self.start_frame, text="Order ID:", font=("Arial", 14)).pack(pady=10)
        self.order_id_entry = ttk.Entry(self.start_frame, font=("Arial", 14), width=20)
        self.order_id_entry.pack(pady=10)
        ttk.Button(
            self.start_frame,
            text="READY",
            command=self.ready_pressed,
            bootstyle="primary",
            width=20
        ).pack(pady=20)
        
        self.record_frame = ttk.Frame(self.master)
        self.preview_label = ttk.Label(self.record_frame)
        self.timer_label = ttk.Label(
            self.record_frame,
            font=('Helvetica', 48, 'bold'),
            foreground='red',
            anchor='center'
        )
        
        control_frame = ttk.Frame(self.record_frame)
        control_frame.pack(pady=20)
        self.start_btn = ttk.Button(
            control_frame,
            text="Start Recording",
            command=self.start_recording,
            bootstyle="success",
            width=15
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)
        self.stop_btn = ttk.Button(
            control_frame,
            text="Stop Recording",
            command=self.stop_recording,
            bootstyle="danger",
            state=tk.DISABLED,
            width=15
        )
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        self.start_frame.pack(expand=True, fill=tk.BOTH)

    def ready_pressed(self):
        self.order_id = self.order_id_entry.get().strip()
        print(f"Order ID set: {self.order_id}")
        self.start_frame.pack_forget()
        self.record_frame.pack(expand=True, fill=tk.BOTH)
        self.preview_label.pack(pady=10)
        # Warm up the encoder: switch to recording mode and start encoder with a dummy output
        if self.picam2.started:
            self.picam2.stop()
        self.picam2.configure(self.recording_config)
        self.picam2.start()
        dummy_output = FfmpegOutput("dummy.mp4", audio=False)
        self.picam2.start_encoder(self.encoder, dummy_output)
        #time.sleep(8)
        self.picam2.stop_encoder()
        # Revert to preview configuration for display
        self.picam2.stop()
        self.picam2.configure(self.preview_config)
        self.picam2.start()
        self.update_preview()

    def start_preview(self):
        if self.picam2.started:
            self.picam2.stop()
        self.picam2.configure(self.preview_config)
        self.picam2.start()
        self.update_preview()

    def update_preview(self):
        if not self.recording and self.picam2.started:
            try:
                image = self.picam2.capture_array("main")
                image = Image.fromarray(image).resize((640, 360))
                self.preview_label.imgtk = ImageTk.PhotoImage(image)
                self.preview_label.config(image=self.preview_label.imgtk)
            except Exception as e:
                print(f"Preview error: {e}")
        self.master.after(66, self.update_preview)

    def start_recording(self):
        # Stop preview and clear the image
        self.preview_label.config(image='')
        self.picam2.stop()
        
        # Sleep for 2 seconds before starting the recording
        #time.sleep(2)

        self.preview_label.pack_forget()
        self.timer_label.pack(pady=50, fill=tk.BOTH, expand=True)
        
        self.picam2.configure(self.recording_config)
        self.picam2.start()

        filename = f"videos/{self.order_id}.mp4" if self.order_id else \
            f"videos/recording_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        os.makedirs("videos", exist_ok=True)
        
        # Validate output format
        try:
            self.output = FfmpegOutput(filename, audio=False)
            self.picam2.start_encoder(self.encoder, self.output)
        except Exception as e:
            print(f"Error starting encoder: {e}")
            return  # Stop function if encoder fails

        self.recStart = datetime.datetime.now()
        
        self.recording = True
        self.recActStart = self.recStart

        

        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        time.sleep(8)
        self.start_time = time.time()
        print(f"\n=== Recording Started ===")
        print(f"Button press time: {self.recStart.strftime('%H:%M:%S.%f')}")
        print(f"Actual start time: {self.recActStart.strftime('%H:%M:%S.%f')}")
        print(f"Start delay: 2.000 seconds")
        self.update_timer()

    def stop_recording(self):
        self.recording = False
        self.timer_label.pack_forget()
        self.preview_label.pack(pady=10)
        self.picam2.stop_encoder()
        self.picam2.stop()
        rec_end = datetime.datetime.now()
        total_duration = (rec_end - self.recActStart).total_seconds()
        print(f"\n=== Recording Stopped ===")
        print(f"Total duration: {total_duration:.2f} seconds")
        print(f"File saved to: videos/")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.start_preview()

    def update_timer(self):
        if self.recording:
            elapsed = time.time() - self.start_time
            self.timer_label.config(text=time.strftime("%H:%M:%S", time.gmtime(elapsed)))
            self.master.after(1000, self.update_timer)

    def on_close(self):
        if self.picam2.started:
            self.picam2.stop()
        self.master.destroy()

if __name__ == "__main__":
    root = ttkbs.Window(themename="darkly")
    root.geometry("800x600")
    app = VideoRecorderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
