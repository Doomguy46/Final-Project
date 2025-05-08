import tkinter as tk
from tkinter import filedialog, font, messagebox
import sounddevice as sd
from scipy.io.wavfile import write
import os
import datetime

class WordProcessor:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Basic Word Processor")
        self.root.geometry("1920x1080")

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
                self.default_path = f"{drive}:/{datetime.datetime.now().strftime("%Y-%m-%d")}_Notes/{clas}/default_note.txt"
            else:
                self.default_path = f"{drive}:/{datetime.datetime.now().strftime("%Y-%m-%d")}_Notes/default_note.txt"
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
        menu_bar.add_cascade(label = "Record", menu = record_menu)
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"))
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        self.root.config(menu=menu_bar)
    def _start_record(self):
        exit
    def _end_record(self):
        exit

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