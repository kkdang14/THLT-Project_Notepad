from tkinter import Text
from datetime import datetime

class Textbox(Text):
    def __init__(self, app, **kwargs):
        # Khởi tạo widget Textbox với các tham số truyền vào
        self.app = app

        # Lấy các cài đặt font từ ứng dụng
        self.font_family = app.config_data.get('Font', 'family')
        self.font_size = app.config_data.get('Font', 'size')
        self.font_weight = app.config_data.get('Font', 'weight')
        self.font_slant = app.config_data.get('Font', 'slant')

        # Thiết lập các thuộc tính mặc định cho widget Textbox
        kwargs['bg'] = app.config_data.get('Colors', 'background')
        kwargs['fg'] = app.config_data.get('Colors', 'foreground')
        kwargs['selectbackground'] = app.config_data.get('Colors', 'selectbackground')
        kwargs['selectforeground'] = app.config_data.get('Colors', 'selectforeground')
        kwargs['bd'] = 0
        kwargs['undo'] = True
        kwargs['wrap'] = 'word'
        kwargs['tabs'] = '0.85c'

        # Gọi phương thức khởi tạo của lớp cơ sở Text và truyền các tham số vào
        super().__init__(app.master, **kwargs)

        # Cập nhật font của Textbox
        self.update_font()

    # Phương thức cắt văn bản
    def cut_text(self):
        if self.tag_ranges('sel'): # Nếu có văn bản được chọn
            self.event_generate('<<Cut>>') # Tạo sự kiện cắt văn bản
            self.app.statusbar.print('CUT') # In thông báo trạng thái
    
    # Phương thức sao chép văn bản
    def copy_text(self):
        if self.tag_ranges('sel'): # Nếu có văn bản được chọn
            self.event_generate('<<Copy>>') # Tạo sự kiện sao chép văn bản
            self.app.statusbar.print('COPIED') # In thông báo trạng thái
    
    # Phương thức dán văn bản
    def paste_text(self):
        self.event_generate('<<Paste>>') # Tạo sự kiện dán văn bản
        self.app.statusbar.print('PASTED') # In thông báo trạng thái
    
    # Phương thức xóa văn bản
    def delete_text(self):
        if self.tag_ranges('sel'): # Nếu có văn bản được chọn
            self.delete('sel.first', 'sel.last') # Xóa văn bản được chọn
            self.app.statusbar.print('DELETED') # In thông báo trạng thái
    
    # Phương thức undo
    def edit_undo(self) -> None:
        if self.tag_ranges('sel'): # Nếu có văn bản được chọn
            self.event_generate('<<Undo>>') # Tạo sự kiện undo
            self.app.statusbar.print('Undo') # In thông báo trạng thái
    
    # Phương thức chọn toàn bộ văn bản
    def select_all(self):
        self.tag_add('sel', 1.0, 'end') # Thêm tag 'sel' cho toàn bộ văn bản
    
    # Phương thức chèn thời gian hiện tại
    def insert_time(self):
        local_time = datetime.now().strftime('%X %b %d %Y') # Lấy thời gian hiện tại
        
        # Xóa văn bản được chọn (nếu có)
        if self.tag_ranges('sel'):
            self.delete('sel.first', 'sel.last')
        
        # Chèn thời gian hiện tại vào vị trí con trỏ
        cursor_pos = self.index('insert')
        self.insert(cursor_pos, local_time)
        self.app.statusbar.print('LOCAL TIME') # In thông báo trạng thái

    # Phương thức chuyển đổi chế độ wrap
    def toggle_wrap(self):
        if self.cget('wrap') == 'word': # Nếu chế độ wrap là 'word'
            self.config(wrap='none') # Chuyển sang chế độ 'none'
            self.app.statusbar.print('WRAP: NONE') # In thông báo trạng thái
            # Thêm thanh cuộn ngang
            self.h_scrollbar.pack(side='bottom', fill='x')
        else:
            self.config(wrap='word') # Nếu chế độ wrap không phải là 'word', chuyển sang chế độ 'word'
            self.app.statusbar.print('WRAP: WORD') # In thông báo trạng thái
            # Xóa thanh cuộn ngang
            self.h_scrollbar.pack_forget()
    
    # Phương thức cập nhật font
    def update_font(self):
        self.config(font=(self.font_family, self.font_size, self.font_weight, self.font_slant))
    
    # Phương thức thay đổi kích thước font
    def change_size(self, by_num):
        self.font_size = str(int(self.font_size) + by_num) # Tăng/giảm kích thước font
        self.update_font() # Cập nhật font
        self.app.config_data.set('Font', 'size', self.font_size) # Lưu cài đặt kích thước font
        
    # Phương thức cấu hình thẻ
    def tag_configure(self, tagName, cnf=None, **kw):
        return self._configure(('tag', 'configure', tagName), cnf, kw)

    # Phương thức thêm thẻ
    def tag_add(self, tagName, index1, *args):
        self.tk.call(
            (self._w, 'tag', 'add', tagName, index1) + args)
        