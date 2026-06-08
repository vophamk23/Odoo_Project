from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TutorialLibraryBook(models.Model):
    # Tên của model (sẽ tương ứng với tên bảng trong cơ sở dữ liệu: tutorial_library_book)
    _name = "tutorial.library.book"
    # Mô tả ngắn gọn về model này
    _description = "Model of tutorial App"
    # Tự động ghi lại log truy cập/tạo/sửa
    _log_access = True
    # Odoo sẽ tự động tạo bảng trong DB nếu _auto = True
    _auto = True

    # ---------- CÁC TRƯỜNG DỮ LIỆU CƠ BẢN ----------
    # required=True: Bắt buộc phải nhập
    name = fields.Char("Title", required=True)
    # Mã số sách quốc tế
    isbn = fields.Char("ISBN")

    # Trường lựa chọn (Dropdown list)
    book_type = fields.Selection(
        [
            ("paper", "Paperback"),
            ("hard", "Hardcover"),
            ("electronic", "Electronic"),
            ("other", "Other"),
        ],
        "Type",
    )
    # Ghi chú nội bộ (văn bản nhiều dòng)
    notes = fields.Text("Internal Notes")
    # Mô tả sách (văn bản có định dạng HTML)
    description = fields.Html("Description")

    # ---------- CÁC TRƯỜNG SỐ HỌC ----------
    # Số lượng bản sao, mặc định là 1
    copies = fields.Integer(default=1)
    # Điểm đánh giá trung bình
    avg_rating = fields.Float("Average Rating", (3, 2))
    # Giá tiền (sử dụng đơn vị tiền tệ được cấu hình ở trường currency_id)
    price = fields.Monetary("Price", "currency_id")
    # Link tới bảng tiền tệ để xác định giá trị của trường price
    currency_id = fields.Many2one("res.currency")  # price helper

    # ---------- CÁC TRƯỜNG THỜI GIAN VÀ TRẠNG THÁI ----------
    date_published = fields.Date()
    # Thời gian cho mượn lần cuối (Mặc định là thời gian hiện tại)
    last_borrow_date = fields.Datetime(
        "Last Borrowed On",
        default=lambda self: fields.Datetime.now(),
    )
    # Trạng thái (Nếu False sẽ bị ẩn khỏi các danh sách mặc định)
    active = fields.Boolean("Active?", default=True)
    # Ảnh bìa (Lưu dưới dạng nhị phân - binary)
    image = fields.Binary("Cover")

    # ---------- CÁC TRƯỜNG LIÊN KẾT (RELATIONAL FIELDS) ----------
    # Many2one (N-1): Nhiều cuốn sách có thể cùng 1 Nhà xuất bản
    publisher_id = fields.Many2one("res.partner", string="Publisher")
    # Many2many (N-N): Nhiều sách có thể do Nhiều tác giả viết chung (bảng trung gian là author_rel)
    author_ids = fields.Many2many(
        "res.partner", relation="author_rel", string="Authors"
    )

    # ---------- CÁC TRƯỜNG COMPUTE (TÍNH TOÁN TỰ ĐỘNG) ----------
    # Field tính toán tự động: Khi publisher thay đổi thì sẽ tự tính lại country của publisher
    @api.depends("publisher_id.country_id")
    def _compute_publisher_country(self):
        for book in self:
            book.publisher_country_id = book.publisher_id.country_id  # type:ignore

    # Cập nhật ngược lại: Nếu người dùng đổi Country ngay trên Form Sách, 
    # nó sẽ tự động lưu country đó về lại cho Publisher gốc.
    def _inverse_publisher_country(self):
        for book in self:
            book.publisher_id.country_id = book.publisher_country_id  # type: ignore

    # Hàm hỗ trợ tìm kiếm trên trường compute
    def _search_publisher_country(self, operator, value):
        return [("publisher_id.country_id", operator, value)]

    # Định nghĩa trường compute dựa vào 3 hàm đã viết ở trên
    publisher_country_id = fields.Many2one(
        "res.country",
        string="Publisher Country",
        compute="_compute_publisher_country",
        inverse="_inverse_publisher_country",
        search="_search_publisher_country",
    )

    # ---------- CÁC HÀM XỬ LÝ NGHIỆP VỤ ----------
    def _check_isbn(self):
        """Hàm nội bộ kiểm tra tính hợp lệ của mã ISBN"""
        self.ensure_one()
        digits = [int(x) for x in self.isbn if x.isdigit()]
        if len(digits) == 13:
            return True
        return False

    def button_check_isbn(self):
        """Hàm được gọi khi người dùng bấm nút Check ISBN trên giao diện"""
        for book in self:
            if not book.isbn:
                # Bắn lỗi nếu bỏ trống
                raise ValidationError("Please provide an ISBN for %s" % book.name)
            if book.isbn and not book._check_isbn():
                # Bắn lỗi nếu ISBN sai định dạng
                raise ValidationError("%s ISBN is invalid" % book.isbn)
        return True
