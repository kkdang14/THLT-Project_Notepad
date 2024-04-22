import os
import sys
import tkinter as tk
from tkinter import ttk
import re
from tkinter import filedialog
import tkinter.messagebox as mbox
from widgets import Menubar, Textbox, Statusbar
from configparser import ConfigParser

APP_NAME = 'TextPad'
NEW_FILE_NAME = 'Untitled'
ICON_PATH = 'icon.ico'
INI_FILE_PATH = 'config.ini'
FILEDIALOG_FILETYPES = [('Text Documents', '*.txt'), ('All Files', '*.*')]

class App():
    def __init__(self, master):
        # Initialize config parser
        self.config_data = ConfigParser()
        self.config_data.read('config.ini')

        self.opened_file = None
        self.autosave_after_id = None
        self.autosave_interval = int(self.config_data.get('AutoSave', 'interval'))
        self.icon_path = ICON_PATH

        self.master = master
        master.title(f'{NEW_FILE_NAME} - {APP_NAME}')
        master.geometry(self.config_data.get('Window', 'geometry'))

        # Widgets
        self.textbox = Textbox(app=self)
        self.statusbar = Statusbar(master)
        self.menu_bar = Menubar(app=self)

        self.textbox.scrollbar = tk.Scrollbar(self.textbox, command=self.textbox.yview)
        self.textbox.config(yscrollcommand=self.textbox.scrollbar.set)
        self.textbox.h_scrollbar = tk.Scrollbar(self.textbox, command=self.textbox.xview, orient='horizontal')
        self.textbox.config(xscrollcommand=self.textbox.h_scrollbar.set)

        self.context_menu = tk.Menu(master, tearoff=0)
        self.context_menu.add_command(label="Undo", command=self.textbox.edit_undo)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Cut", command=self.textbox.cut_text)
        self.context_menu.add_command(label="Copy", command=self.textbox.copy_text)
        self.context_menu.add_command(label="Paste", command=self.textbox.paste_text)
        self.context_menu.add_command(label="Delete", command=self.textbox.delete_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Select All", command=self.textbox.select_all)
        self.context_menu.add_command(label="Time/Date", command=self.textbox.insert_time)

        # Layout
        self.textbox.pack(expand=True, fill='both')
        self.textbox.scrollbar.pack(side='right', fill='y')
        self.statusbar.pack(side='bottom', fill='x')

        # Key binding & on close command
        self.master.protocol('WM_DELETE_WINDOW', self.on_close)
        self.master.bind('<Control-n>', lambda e: self.new_file())
        self.master.bind('<Control-o>', lambda e: self.open_file())
        self.master.bind('<Control-s>', lambda e: self.save_file())
        self.master.bind('<Control-S>', lambda e: self.save_file_as())
        self.master.bind('<Control-f>', lambda e: self.find_text())
        self.textbox.bind('<F5>', lambda e: self.textbox.insert_time())
        self.textbox.bind('<Button-3>', lambda e: self.show_context_menu(e))
        self.textbox.bind('<Control-Key-x>', lambda e: self.textbox.cut_text())
        self.textbox.bind('<Control-Key-c>', lambda e: self.textbox.copy_text())
        self.textbox.bind('<Control-Key-v>', lambda e: self.textbox.paste_text())
        self.textbox.bind('<Control-Key>-', lambda e: self.textbox.change_size(-2))
        self.textbox.bind('<Control-=>', lambda e: self.textbox.change_size(2))
        self.master.bind('<F1>', lambda e: self.view_shortcuts())

        if self.autosave_var.get():
            self.statusbar.print(f'AUTOSAVE: ON ({int(self.autosave_interval) / 1000}s)')
        self.textbox.focus()
    
        self.master.iconbitmap(self.icon_path)
    
    def new_file(self):
        self.autosave(stop=True)
        if self.save_changes_answer() is None:
            return
        self.opened_file = None
        self.master.title(f'{NEW_FILE_NAME} - {APP_NAME}')
        self.textbox.delete(1.0, 'end')
        self.statusbar.print('NEW FILE')
    
    def open_file(self):
        if self.save_changes_answer() is None:
            return
        
        file = filedialog.askopenfilename(file=FILEDIALOG_FILETYPES)
        try:
            with open(file, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except:
            self.statusbar.print('COULDN\'T READ FILE')
        else:
            # SUCCESS
            self.opened_file = file
            self.master.title(f'{os.path.basename(file)} - {APP_NAME}')
            self.textbox.delete(1.0, 'end')
            self.textbox.insert(1.0, file_content)
            self.statusbar.print('READY')

            self.autosave()
    
    def save_file(self):
        if self.opened_file:
            try:
                with open(self.opened_file, 'w', encoding='utf-8') as f:
                    f.write(self.textbox.get(1.0, 'end')[:-1])
            except:
                self.statusbar.print('COULDN\'T RESAVE FILE')
            else:
                if not self.autosave_after_id:
                    self.statusbar.print('SAVED')
        else:
            self.save_file_as()

    def save_file_as(self):
        file = filedialog.asksaveasfilename(initialfile=NEW_FILE_NAME, defaultextension='.txt', filetypes=FILEDIALOG_FILETYPES)
        if file: # file dialog not closed
            try:
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(self.textbox.get(1.0, 'end')[:-1])
            except:
                self.statusbar.print('COULDN\'T SAVE FILE')
            else:
                # SUCCESS
                self.opened_file = file
                self.master.title(f'{os.path.basename(file)} - {APP_NAME}')
                self.statusbar.print(f'SAVED at {file}')

                self.autosave()

    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)
    
    def view_shortcuts(self):
        lst = [
            '<Ctrl+N> - New File', '<Ctrl+O> - Open file', '<Ctrl-S> - Save file',
            '<Ctrl-Shift-S> - Save As', '', '<Ctrl-Z> - Undo', '<Ctrl-Y> - Redo', '<Ctrl-X> - Cut text',
            '<Ctrl-C> - Copy text', '<Ctrl-V> - Paste text', '<Del> - Delete selected text',
            '<Ctrl-A> - Select all text', '<F5> - Insert Time/Date', '', '<Ctrl-Plus> - Enlarge text font',
            '<Ctrl-Minus> - Reduce text font', '', '<F1> - View shortcuts'
        ]
        mbox.showinfo('Shortcut List', '\n'.join(lst))
    
    def change_autosave(self):
        state = self.autosave_var.get()
        self.autosave(stop=not state)
        self.statusbar.print(f'AUTOSAVE: {f"ON ({int(self.autosave_interval) / 1000}s)" if state else "OFF"}')        
    
    def autosave(self, stop=False):
        if stop is True:
            if self.autosave_after_id:
                self.master.after_cancel(self.autosave_after_id)
        else:
            if self.autosave_var.get() and self.opened_file:
                self.save_file()
                self.autosave_after_id = self.master.after(self.autosave_interval, self.autosave)

    def save_changes_answer(self):
        text = self.textbox.get(1.0, 'end')[:-1]
        answer = False
        # New file and not empty
        if not self.opened_file and text != '':
            answer = mbox.askyesnocancel(APP_NAME, f'Do you want to SAVE CHANGES to {NEW_FILE_NAME}?')
            if answer is True:
                self.save_file_as()
        elif self.opened_file:
            with open(self.opened_file, 'r') as f:
                file_text = f.read()
            if text != file_text:
                answer = mbox.askyesnocancel(APP_NAME, f'Do you want to SAVE CHANGES to {self.opened_file}?')
            if answer is True:
                self.save_file()
        return answer
    
    def on_close(self):
        if self.save_changes_answer() is None:
            return
        # in case the autosave interval is long
        self.autosave()

        self.config_data.set('Window', 'geometry', self.master.geometry())
        self.config_data.set('AutoSave', 'state', str(self.autosave_var.get()))
        # Save CONFIG data
        try:
            with open(INI_FILE_PATH, 'w') as file:
                self.config_data.write(file)
        except:
            print('Config data was NOT written!')
        else:
            print('Config data SAVED!')
        sys.exit()
        
    def find_text(self):
        def bind_enter(event):
            find()
        
        def bind_enter_replace(event):
            replace_next()

        # Create a new Toplevel window for the find dialog
        find_window = tk.Toplevel(self.master)
        find_window.title("Find Text")

        # Set the size of the find window
        find_window.geometry("350x150+950+280")

        # Label and entry for entering the regex pattern to find
        find_label = ttk.Label(find_window, text="Enter regular expression pattern:")
        find_label.pack()
        find_entry = ttk.Entry(find_window)
        find_entry.pack(side="top")
        find_entry.configure(width=50)
        find_entry.bind("<Return>", bind_enter)
        
        #Label and entry for replace
        
        replace_label = ttk.Label(find_window, text="Enter replacement:")
        replace_label.pack()
        replace_entry = ttk.Entry(find_window)
        replace_entry.pack(side="top")
        replace_entry.configure(width=50)
        replace_entry.bind("<Return>", bind_enter_replace)
        
        # Keep track of the end position of the previous match
        last_match_end = "1.0"
        
        # Đếm số lượng từ tìm thấy
        count_word_founded = 0
        # Đếm số lượng thay thế
        count_replace = 0

        # Định nghĩa một hàm có tên là find_next với đối số tùy chọn là event
        def find(event=None):
            # Khai báo last_match_end là biến không cục bộ
            nonlocal last_match_end
            # Lấy mẫu regex từ đầu vào 
            pattern = find_entry.get()
            nonlocal count_word_founded
            if pattern:
                try:
                    # Biên dịch mẫu regex, có phân biệt chữ hoa và thường
                    regex = re.compile(pattern)
                    # Tìm kiếm lần xuất hiện tiếp theo bắt đầu từ cuối của lần xuất hiện trước đó
                    match = regex.search(self.textbox.get(last_match_end, "end"))
                    # Nếu tìm thấy kết quả
                    if match:
                        count_word_founded+=1
                        # Lấy chỉ số bắt đầu và kết thúc của kết quả
                        start, end = match.start(), match.end()
                        # Tính toán chỉ số bắt đầu và kết thúc trong textbox
                        start_index = f"{last_match_end}+{start}c"
                        end_index = f"{last_match_end}+{end}c"
                        # Xóa bỏ các thẻ 'find' trước đó (nếu có)
                        self.textbox.tag_remove("find", "1.0", "end")

                        # Thêm thẻ 'find' vào phần được khớp
                        self.textbox.tag_add("find", start_index, end_index)

                        # Cấu hình thẻ 'find' để có nền màu xanh nhạt
                        self.textbox.tag_configure("find", background="light blue")

                        # Đảm bảo phần được khớp hiển thị trên màn hình
                        self.textbox.see(start_index)

                        # Cập nhật last_match_end đến cuối của kết quả hiện tại
                        last_match_end = end_index
            
                    else:
                        # Nếu không tìm thấy kết quả nào khác, bắt đầu tìm kiếm từ đầu
                        last_match_end = "1.0"
                        # Hiển thị hộp thoại thông báo không tìm thấy kết quả nào khác
                        mbox.showinfo("Tổng số từ", f"Tìm thấy {count_word_founded} từ khớp với '{pattern}'")
                        # Xóa bỏ các thẻ 'find' trước đó (nếu có)
                        self.textbox.tag_remove("find", "1.0", "end")

                        count_word_founded = 0
                except re.error:
                    # Hiển thị hộp thoại thông báo lỗi cho mẫu regex không hợp lệ
                    mbox.showerror("Mẫu không hợp lệ", "Mẫu biểu thức chính quy không hợp lệ")
        def on_close():
            # Bỏ highlight tag khi mà cửa sổ tìm kiếm đóng
            self.textbox.tag_remove("find", "1.0", "end")
            self.textbox.tag_remove("replace", "1.0", "end")
            find_window.destroy()

        find_button = ttk.Button(find_window, text="Find", command=find)
        find_button.pack(side="top")
        find_button.config(width=15, padding=3)
        
        def replace_next():
            nonlocal last_match_end
            pattern = find_entry.get()
            replacement = replace_entry.get()
            nonlocal count_replace
            
            if pattern and replacement:
                # Compile the regex pattern
                regex = re.compile(pattern)

                # Search for the next occurrence of the regex pattern
                match = regex.search(self.textbox.get(last_match_end, "end"))
                
                if match:
                    count_replace += 1
                    # Get the start and end indices of the match
                    start, end = match.start(), match.end()
                    start_index = f"{last_match_end}+{start}c"
                    end_index = f"{last_match_end}+{end}c"
                    
                    # Perform the replacement using the sub function
                    replaced_text = regex.sub(replacement, self.textbox.get(last_match_end, "end"), count=1)

                    # Update the text in the textbox
                    self.textbox.delete(last_match_end, "end")
                    self.textbox.insert(last_match_end, replaced_text)

                    # Highlight the replaced text
                    self.textbox.tag_add("replace", start_index, end_index)
                    self.textbox.tag_configure("replace", background="light blue")

                    # Update last_match_end to the end of the replaced text
                    last_match_end = end_index

                else:
                    mbox.showinfo("Tổng số từ", f"Tìm thấy {count_replace} từ khớp với '{pattern}'")
                    self.textbox.tag_remove("replace", "1.0", "end")
                    count_replace = 0
                    
        replace_button = ttk.Button(find_window, text="Find and Replace", command=replace_next)
        replace_button.pack(side="bottom")
        replace_button.config(width=15, padding=3)

        # Close the find window when the main window is closed
        find_window.protocol("WM_DELETE_WINDOW", on_close)
        
def main():
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == '__main__':
    main()