from odoo import models, fields, api

class BookCategory(models.Model):
    # Tên của model quản lý Thể loại sách
    _name = "tutorial.library.book.category"
    _description = "Book Category"
    
    # Bật tính năng lưu trữ Parent-Child (Mô hình Cây / Phân cấp)
    _parent_store = True

    # translate=True: Hỗ trợ dịch tên danh mục sang nhiều ngôn ngữ
    name = fields.Char(translate=True, required=True)
    
    # ---------- CÁC TRƯỜNG PHÂN CẤP (HIERARCHY) ----------
    # Many2one trỏ về chính bảng Category để xác định Thể loại Cha
    # ondelete="restrict": Không cho phép xóa Thể loại Cha nếu nó đang có Thể loại Con
    parent_id = fields.Many2one(
        "tutorial.library.book.category",
        "Parent Category",
        ondelete="restrict",
    )
    # Đường dẫn phân cấp (Ví dụ: Sách Giáo Khoa / Lớp 1)
    parent_path = fields.Char(index=True)

    # ---------- CÁC TRƯỜNG TÙY CHỌN (OPTIONAL) ----------
    # One2many trỏ về chính bảng Category để lấy danh sách các Thể loại Con
    child_ids = fields.One2many(
        "tutorial.library.book.category",
        "parent_id",
        "Subcategories",
    )

    # Trường Reference: Cho phép liên kết linh hoạt tới các model khác nhau
    # Trong trường hợp này là liên kết tới 1 Sách cụ thể HOẶC 1 Tác giả cụ thể
    highlighted_id = fields.Reference(
        [("library.book", "Book"), ("res.partner", "Author")],
        "Category Highlight",
    )
