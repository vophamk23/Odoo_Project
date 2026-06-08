from odoo import http

class Books(http.Controller):
    # Khai báo đường dẫn URL cho trang web
    # Khi người dùng truy cập http://localhost:8069/tutorial/library/books thì hàm này sẽ chạy
    @http.route("/tutorial/library/books")
    def list(self, **kwargs):
        # Kết nối tới bảng (model) tutorial.library.book trong Database
        Book = http.request.env["tutorial.library.book"]
        # Lấy toàn bộ danh sách Sách (Không có điều kiện lọc [])
        books = Book.search([])
        
        # Trả về và hiển thị kết quả thông qua Template HTML có ID là book_list_template
        # Truyền biến 'books' sang giao diện HTML để vòng lặp for có thể in ra danh sách
        return http.request.render(
            "tutorial.book_list_template",
            {"books": books},
        )
