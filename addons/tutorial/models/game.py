from odoo import models, fields

class Game(models.Model):
    # Tên định danh của bảng trong Database (thành tutorial_game)
    _name = 'tutorial.game'
    _description = 'Game'

    # Các trường dữ liệu (Cột trong Database)
    name = fields.Char('Tên Game', required=True) # Char: Chuỗi ngắn
    price = fields.Float('Giá')                   # Float: Số thực
    release_date = fields.Date('Ngày Phát Hành')  # Date: Ngày tháng
    image = fields.Image('Ảnh Bìa')               # Image: Lưu hình ảnh
    description = fields.Html('Mô Tả Chi Tiết')   # Html: Văn bản định dạng (in đậm, nghiêng...)
    
    # Selection: Danh sách chọn (Dropdown)
    state = fields.Selection([
        ('draft', 'Bản Nháp'),
        ('upcoming', 'Sắp Ra Mắt'),
        ('released', 'Đã Phát Hành'),
        ('discontinued', 'Ngừng Bán')
    ], string='Trạng Thái', default='draft')
    
    rating = fields.Selection([
        ('1', '1 Sao'),
        ('2', '2 Sao'),
        ('3', '3 Sao'),
        ('4', '4 Sao'),
        ('5', '5 Sao')
    ], string='Đánh Giá')
    
    is_multiplayer = fields.Boolean('Hỗ trợ Multiplayer') # Boolean: Checkbox True/False
    
    # Many2one: Liên kết (N-1) tới bảng Danh bạ (res.partner) của Odoo
    developer_id = fields.Many2one('res.partner', string='Nhà Phát Triển')
