import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import Listbox, Scrollbar, Button, Frame, Label, Tk
import os
import threading
import time
import psutil
from PIL import Image, ImageTk
import requests
from io import BytesIO

class AppBlockerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("App Blocker")
        self.root.geometry("640x630")
        self.root.config(bg="#f0f0f0")
        
        self.blocked_apps = {}
        self.blocking_threads = {}
        self.is_blocking = False
        
        self.create_widgets()
    
    def create_widgets(self):
        title_label = Label(self.root, text="App Blocker", font=("Helvetica", 30, "bold"), bg="#f0f0f0", fg="#333333")
        title_label.pack(pady=(20, 10))

        self.app_frame = Frame(self.root, bg="#f0f0f0")
        self.app_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.app_listbox = Listbox(self.app_frame, width=50, height=10, font=("Helvetica", 12), bg="#ffffff", selectbackground="#e0e0e0", selectforeground="#333333")
        self.app_listbox.pack(side="left", fill="both", expand=True, padx=(0, 10))

        list_scroll = Scrollbar(self.app_frame)
        list_scroll.pack(side="right", fill="y")

        self.app_listbox.config(yscrollcommand=list_scroll.set)
        list_scroll.config(command=self.app_listbox.yview)

        button_frame = Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=(10, 20))

        add_button = Button(button_frame, text="Add App", command=self.add_app, font=("Helvetica", 12), bg="#4CAF50", fg="#ffffff", padx=10)
        add_button.grid(row=0, column=0, padx=5)

        remove_button = Button(button_frame, text="Remove App", command=self.remove_app, font=("Helvetica", 12), bg="#FF5733", fg="#ffffff", padx=10)
        remove_button.grid(row=0, column=1, padx=5)

        start_button = Button(button_frame, text="Start Blocking", command=self.start_blocking, font=("Helvetica", 12), bg="#3498DB", fg="#ffffff", padx=10)
        start_button.grid(row=0, column=2, padx=5)

        stop_button = Button(button_frame, text="Stop Blocking", command=self.stop_blocking, font=("Helvetica", 12), bg="#E74C3C", fg="#ffffff", padx=10)
        stop_button.grid(row=0, column=3, padx=5)

        clear_button = Button(button_frame, text="Clear List", command=self.clear_list, font=("Helvetica", 12), bg="#F39C12", fg="#ffffff", padx=10)
        clear_button.grid(row=0, column=4, padx=5)

        # Load and display the gif
        self.gif_frames = []
        gif_url = "https://media1.tenor.com/m/2Rb1vsrgV0IAAAAC/padh-le-padhai.gif"  # Example GIF URL
        self.load_gif_frames(gif_url)
        self.current_frame_index = 0
        self.gif_label = Label(self.root, bg="#f0f0f0")
        self.animate_gif()

    def add_app(self):
        selected_apps = filedialog.askopenfilenames(title="Select Applications to Block", filetypes=[("Executable files", "*.exe")])
        if selected_apps:
            for app_path in selected_apps:
                replacement_app = filedialog.askopenfilename(title=f"Select Replacement Application for {os.path.basename(app_path)}", filetypes=[("Executable files", "*.exe")])
                if replacement_app:
                    self.blocked_apps[app_path] = replacement_app
            self.refresh_listbox()
    
    def remove_app(self):
        selected_index = self.app_listbox.curselection()
        if selected_index:
            app_path = self.app_listbox.get(selected_index)
            del self.blocked_apps[app_path]
            self.refresh_listbox()
        else:
            messagebox.showinfo("Info", "Please select an app to remove.")
    
    def start_blocking(self):
        if not self.is_blocking:
            self.is_blocking = True
            for app_path, replacement_app in self.blocked_apps.items():
                thread = threading.Thread(target=self.block_apps, args=(app_path, replacement_app))
                self.blocking_threads[app_path] = thread
                thread.start()
            messagebox.showinfo("Info", "Blocking started.")
    
    def stop_blocking(self):
        if self.is_blocking:
            self.is_blocking = False
            for app_path, thread in self.blocking_threads.items():
                thread.join()
            messagebox.showinfo("Info", "Blocking stopped.")
    
    def clear_list(self):
        self.blocked_apps.clear()
        self.refresh_listbox()

    def block_apps(self, app_path, replacement_app):
        while self.is_blocking:
            if self.is_process_running(os.path.basename(app_path)):
                # Kill the blocked app process
                for process in psutil.process_iter():
                    if process.name() == os.path.basename(app_path):
                        process.kill()
                # Open the replacement app
                os.startfile(replacement_app)
            # Delay between checks to prevent high CPU usage
            time.sleep(1)
    
    def is_process_running(self, process_name):
        for process in psutil.process_iter(['name']):
            if process.info['name'] == process_name:
                return True
        return False
    
    def refresh_listbox(self):
        self.app_listbox.delete(0, tk.END)
        for app, replacement in self.blocked_apps.items():
            self.app_listbox.insert(tk.END, f"{os.path.basename(app)} -> {os.path.basename(replacement)}")

    def load_gif_frames(self, gif_url):
        response = requests.get(gif_url)
        if response.status_code == 200:
            gif_data = response.content
            gif = Image.open(BytesIO(gif_data))
            try:
                while True:
                    self.gif_frames.append(ImageTk.PhotoImage(gif.copy()))
                    gif.seek(len(self.gif_frames))  # Move to next frame
            except EOFError:
                pass  # End of gif
        else:
            print("Failed to download GIF from URL")

    def animate_gif(self):
        if self.gif_frames:
            self.gif_label.config(image=self.gif_frames[self.current_frame_index])
            self.gif_label.pack(pady=(20, 10))
            self.current_frame_index = (self.current_frame_index + 1) % len(self.gif_frames)
            self.root.after(100, self.animate_gif)
        else:
            print("No gif frames found")

if __name__ == "__main__":
    root = Tk()
    app = AppBlockerApp(root)
   
    

    root.mainloop()
