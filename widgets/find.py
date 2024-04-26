import tkinter as tk
from tkinter import ttk
import re
from tkinter import filedialog
import tkinter.messagebox as mbox

class Find:
    def __init__(self, master, textbox):
        self.master = master
        self.textbox = textbox
        self.last_match_end = "1.0"
        self.count_replace = 0
        self.count_word_founded = 0
        
        search_replace_frame = ttk.Frame(master)
        search_replace_frame.pack(side="top", fill="x", padx=5)

        self.find_entry_var = tk.StringVar()
        self.find_entry_var.set('Enter text to find')
        self.find_entry = ttk.Entry(search_replace_frame, textvariable=self.find_entry_var, foreground='gray')
        self.find_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        
        self.replace_entry_var = tk.StringVar()
        self.replace_entry_var.set('Enter text to replace')
        self.replace_entry = ttk.Entry(search_replace_frame, textvariable=self.replace_entry_var, foreground='gray')
        self.replace_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        self.find_button = ttk.Button(search_replace_frame, text="Find", command=self.find_text)
        self.find_button.pack(side="left", padx=5, pady=5)
        self.replace_button = ttk.Button(search_replace_frame, text="Find and Replace", command=self.replace_text)
        self.replace_button.pack(side="left", padx=5, pady=5)
        
        self.find_entry.bind("<FocusIn>", self.on_find_entry_focus_in)
        self.find_entry.bind("<FocusOut>", self.on_find_entry_focus_out)

        self.replace_entry.bind("<FocusIn>", self.on_replace_entry_focus_in)
        self.replace_entry.bind("<FocusOut>", self.on_replace_entry_focus_out)

    def on_find_entry_focus_in(self, event):
        if self.find_entry_var.get() == 'Enter text to find':
            self.find_entry_var.set('')
            self.find_entry.config(foreground='black')

    def on_find_entry_focus_out(self, event):
        if not self.find_entry_var.get():
            self.find_entry_var.set('Enter text to find')
            self.find_entry.config(foreground='gray')

    def on_replace_entry_focus_in(self, event):
        if self.replace_entry_var.get() == 'Enter text to replace':
            self.replace_entry_var.set('')
            self.replace_entry.config(foreground='black')

    def on_replace_entry_focus_out(self, event):
        if not self.replace_entry_var.get():
            self.replace_entry_var.set('Enter text to replace')
            self.replace_entry.config(foreground='gray')

    def find_text(self):
        pattern = self.find_entry.get()
        if pattern:
            try:
                regex = re.compile(pattern)
                match = regex.search(self.textbox.get(self.last_match_end, "end"))
                if match:
                    self.count_word_founded += 1
                    start, end = match.start(), match.end()
                    start_index = f"{self.last_match_end}+{start}c"
                    end_index = f"{self.last_match_end}+{end}c"
                    self.textbox.tag_remove("find", "1.0", "end")
                    self.textbox.tag_add("find", start_index, end_index)
                    self.textbox.tag_configure("find", background="light blue")
                    self.textbox.see(start_index)
                    self.last_match_end = end_index
                else:
                    self.last_match_end = "1.0"
                    mbox.showinfo("Tổng số từ được tìm thấy", f"Tìm thấy {self.count_word_founded} từ khớp với '{pattern}'")
                    self.textbox.tag_remove("find", "1.0", "end")
                    self.count_word_founded = 0
            except re.error:
                mbox.showerror("Mẫu không hợp lệ", "Mẫu biểu thức chính quy không hợp lệ")

    def replace_text(self):
        pattern = self.find_entry.get()
        replacement = self.replace_entry.get()
        if pattern and replacement:
            regex = re.compile(pattern)
            match = regex.search(self.textbox.get(self.last_match_end, "end"))
            if match:
                self.count_replace += 1
                start, end = match.start(), match.end()
                start_index = f"{self.last_match_end}+{start}c"
                end_index = f"{self.last_match_end}+{end}c"
                replaced_text = regex.sub(replacement, self.textbox.get(self.last_match_end, "end"), count=1)
                self.textbox.delete(self.last_match_end, "end")
                self.textbox.insert(self.last_match_end, replaced_text)
                self.textbox.tag_add("replace", start_index, end_index)
                self.textbox.tag_configure("replace", background="light green")
                self.last_match_end = end_index
            else:
                mbox.showinfo("Tổng số từ được tìm thấy và thay thế", f"Đã thay thế {self.count_replace} từ khớp với '{pattern}' bằng '{replacement}'")
                self.textbox.tag_remove("replace", "1.0", "end")
                self.count_replace = 0
    