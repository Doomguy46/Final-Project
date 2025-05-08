import tkinter as tk
from tkinter import filedialog, font, messagebox
import sounddevice as sd
from scipy.io.wavfile import write
import os
import datetime
import numpy as np
import threading

class WordProcessor:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Basic Word Processor")
        self.root.geometry("1920x1080")
        self.fs = 44100  # Sample rate
        self.recording = None
        self.recordingAmount = 0
        self.is_recording = False
        self.text_area = tk.Text(self.root, wrap='word', undo=True)
        self.text_area.pack(fill='both', expand=1)

        self.scroll = tk.Scrollbar(self.text_area)
        self.scroll.pack(side='right', fill='y')
        self.scroll.config(command=self.text_area.yview)
        self.text_area.config(yscrollcommand=self.scroll.set)
        drive = tk.simpledialog.askstring("Drive Letter?", "Drive letter?")
        clas = tk.simpledialog.askstring("Class?", "Enter Class Name")
        if drive:
            drive = drive.upper()
            if clas:
                self.default_path = f"{drive}:/Notes/{datetime.datetime.now().strftime("%Y-%m-%d")}_Notes/{clas}/default_note.txt"
            else:
                self.default_path = f"{drive}:/Notes/{datetime.datetime.now().strftime("%Y-%m-%d")}_Notes/default_note.txt"
            os.makedirs(os.path.dirname(self.default_path), exist_ok=True)
        else:
            self.default_path = None

        self._create_menu()
        self._create_toolbar()

    def _create_menu(self):
        menu_bar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self._new_file)
        file_menu.add_command(label="Open", command=self._open_file)
        file_menu.add_command(label="Save", command=self._save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        record_menu = tk.Menu(menu_bar, tearoff=0)
        record_menu.add_command(label="Record Audio", command = self._start_record)
        record_menu.add_command(label ="End Recording", command = self._end_record)
        menu_bar.add_cascade(label = "Record", menu = record_menu)
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"))
        menu_bar.add_command(label= "Settings", command = self._open_settings)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        self.root.config(menu=menu_bar)
    def _start_record(self):
        if not self.is_recording:
            self.is_recording = True
            self.recording = []

        def callback(indata, frames, time, status):
            if self.is_recording:
                self.recording.append(indata.copy())

        self.stream = sd.InputStream(samplerate=self.fs, channels=2, callback=callback)
        self.stream.start()
        messagebox.showinfo("Recording", "Recording started...")

    def _end_record(self):
        if self.is_recording:
          self.is_recording = False
          self.stream.stop()
          self.stream.close()

        
        audio_data = np.concatenate(self.recording, axis=0)

        if self.default_path:
            base_path = os.path.dirname(self.default_path)
            audio_path = os.path.join(base_path, f"recording{self.recordingAmount}.wav")
            self.recordingAmount = self.recordingAmount + 1
        else:
            audio_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])

        try:
            write(audio_path, self.fs, audio_data)
            messagebox.showinfo("Saved", f"Audio saved at:\n{audio_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save recording: {e}")
    def _open_settings(self):
            settings_window = tk.Toplevel()
            settings_window.title("Settings")

            # Example settings options
            audio_label = tk.Label(settings_window, text="Audio Input Device:")
            audio_label.pack()
            indeviceNames = []
            indevices = []
            outdevicename = []
            outdevices = []
            for device in sd.query_devices():
                if device["max_input_channels"] > 0:
                    indeviceNames.append(device["name"])
                    indevices.append(device)
                elif device["max_output_channels"] > 0:
                    outdevicename.append(device["name"])
                    outdevices.append(device)
            audio_options = indeviceNames
            audio_var = tk.StringVar(settings_window)
            audio_var.set(audio_options[0]) # Default value
            audio_dropdown = tk.OptionMenu(settings_window, audio_var, *audio_options)
            audio_dropdown.pack()
            save_button = tk.Button(settings_window, text="Save", command=lambda: self.save_settings(audio_var.get(),indevices))
            save_button.pack()

    def save_settings(selectedDevice):
        sd.default.device = selectedDevice
               


    def _create_toolbar(self):
        toolbar = tk.Frame(self.root)

        font_families = list(font.families())
        self.font_var = tk.StringVar(value="Arial")
        self.font_menu = tk.OptionMenu(toolbar, self.font_var, *font_families, command=self._change_font)
        self.font_menu.pack(side='left')

        self.size_var = tk.IntVar(value=12)
        self.size_menu = tk.Spinbox(toolbar, from_=8, to=72, textvariable=self.size_var, command=self._change_font)
        self.size_menu.pack(side='left')

        toolbar.pack(fill='x')

        self._change_font()  # Set initial font

    def _change_font(self, *args):
        selected_font = self.font_var.get()
        selected_size = self.size_var.get()
        try:
            self.text_area.config(font=(selected_font, selected_size))
        except:
            pass  # Invalid font or size

    def _new_file(self):
        self.text_area.delete(1.0, tk.END)

    def _open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if path:
            try:
                with open(path, "r") as file:
                    content = file.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, content)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

    def _save_file(self):
        if self.default_path:
            path = filedialog.asksaveasfilename(initialfile=os.path.basename(self.default_path),initialdir=os.path.dirname(self.default_path), defaultextension=".txt",filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        else:
            path = filedialog.asksaveasfilename(defaultextension=".txt",filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if path:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(path, "w") as file:
                    file.write(content)
                    self.default_path = path  # Update default path
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
def main():
    root = tk.Tk()
    app = WordProcessor(root)
    root.mainloop()

if __name__ == "__main__":
    main()