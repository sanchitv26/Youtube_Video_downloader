import os
import threading
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import yt_dlp

class YouTubeDownloader:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("YouTube Downloader PRO")
        self.app.geometry("750x550")
        self.break_flag = False
        self.download_thread = None
        self.create_widgets()

    def create_widgets(self):
        frame = ctk.CTkFrame(self.app)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="YouTube Video Downloader", font=("Arial", 22, "bold")).pack(pady=15)

        frame = ctk.CTkFrame(self.app)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        image_path = "ytlogo.png"  # Replace with actual logo file name
        logo_image = ctk.CTkImage(light_image=Image.open(image_path), size=(120, 80))
        ctk.CTkLabel(frame, image=logo_image, text="").pack(pady=(10, 0))

        url_frame = ctk.CTkFrame(frame)
        url_frame.pack(pady=10, fill="x", padx=10)
        ctk.CTkLabel(url_frame, text="YouTube URL:").pack(side="left", padx=5)
        self.url_entry = ctk.CTkEntry(url_frame, width=500, placeholder_text="Paste video link here")
        self.url_entry.pack(side="left", fill="x", expand=True)

        self.quality_var = ctk.StringVar(value="best")
        quality_options = [
            ("Best Available", "best"),
            ("1080p", "bestvideo[height<=1080]+bestaudio/best"),
            ("720p", "bestvideo[height<=720]+bestaudio/best"),
            ("480p", "bestvideo[height<=480]+bestaudio/best"),
            ("360p", "bestvideo[height<=360]+bestaudio/best"),
            ("Audio Only (MP3)", "audio"),
        ]

        for text, value in quality_options:
            ctk.CTkRadioButton(frame, text=text, variable=self.quality_var, value=value).pack(anchor="w", padx=20, pady=2)

        self.progress = ctk.CTkProgressBar(frame, width=500)
        self.progress.pack(pady=15)
        self.progress.set(0)

        self.status = ctk.CTkLabel(frame, text="Ready", text_color="lightblue")
        self.status.pack()

        self.download_btn = ctk.CTkButton(frame, text="Download", command=self.start_download)
        self.download_btn.pack(pady=10)

        self.pause_btn = ctk.CTkButton(frame, text="Pause", command=self.pause_download, fg_color="gray", state="disabled")
        self.pause_btn.pack(pady=5)

        ctk.CTkLabel(frame, text="v1.1 | Quality selector + Pause/Resume").pack(side="bottom", pady=10)

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return

        self.break_flag = False
        self.download_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal", text="Pause")
        self.status.configure(text="Starting download...")
        self.progress.set(0)

        self.download_thread = threading.Thread(target=self.download_video, args=(url,), daemon=True)
        self.download_thread.start()

    def pause_download(self):
        if self.download_thread and self.download_thread.is_alive():
            if not self.break_flag:
                self.break_flag = True
                self.pause_btn.configure(text="Resume")
                self.status.configure(text="Paused", text_color="orange")
            else:
                self.break_flag = False
                self.status.configure(text="Resuming...", text_color="lightblue")
                self.download_btn.configure(state="disabled")
                self.pause_btn.configure(text="Pause")
                threading.Thread(target=self.download_video, args=(self.url_entry.get().strip(),), daemon=True).start()

    def download_video(self, url):
        quality = self.quality_var.get()
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads")

        ydl_opts = {
            'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [self.ydl_hook],
            'noplaylist': True,
        }

        if quality == "audio":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            ydl_opts.update({'format': quality})

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            if not self.break_flag:
                self.status.configure(text="Download complete!", text_color="green")
                messagebox.showinfo("Success", f"File saved to:\n{download_dir}")
        except Exception as e:
            if not self.break_flag:
                self.status.configure(text=f"Error: {str(e)}", text_color="red")
        finally:
            if not self.break_flag:
                self.download_btn.configure(state="normal")
                self.pause_btn.configure(state="disabled")
            self.progress.set(0)

    def ydl_hook(self, d):
        if self.break_flag:
            raise Exception("Download paused by user.")

        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                percentage = downloaded / total
                self.progress.set(percentage)
                self.status.configure(text=f"Downloaded: {int(percentage * 100)}%", text_color="lightblue")
        elif d['status'] == 'finished':
            self.status.configure(text="Finalizing download...")

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.app.mainloop()
