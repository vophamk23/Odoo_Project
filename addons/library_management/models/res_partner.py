from odoo import models, fields

class Partner(models.Model):
    # Dùng _inherit để Kế thừa (Mở rộng) bảng Đối tác (res.partner) có sẵn của Odoo
    _inherit = "res.partner"
    
    # Thêm trường One2many để xem được toàn bộ danh sách các Cuốn sách do Đối tác này Xuất bản
    # Nó liên kết ngược lại với trường publisher_id bên bảng Sách
    published_book_ids = fields.One2many(
        "tutorial.library.book", "publisher_id", "Published Books"
    )

    # Thêm trường Many2many để xem danh sách các Cuốn sách do Đối tác này Sáng tác (Là Tác giả)
    # Bắt buộc phải khai báo tên bảng trung gian "author_rel" cho khớp với bên bảng Sách
    book_ids = fields.Many2many(
        "tutorial.library.book",
        relation="author_rel",
    )
