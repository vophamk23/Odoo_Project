from odoo import models, fields

class Tag(models.Model):
    # Tên bảng trong Database (thành tutorial_game_tag)
    _name = 'tutorial.game.tag'
    _description = 'Game Tag'

    # Tên của Thể loại (ví dụ: Hành động, Kinh dị)
    name = fields.Char('Tag Name', required=True)
    
    # Mã màu sắc để hiển thị trên giao diện
    color = fields.Integer('Màu sắc')

# Kế thừa bảng tutorial.game đã có từ trước
class Game(models.Model):
    _inherit = 'tutorial.game'

    # Bổ sung thêm cột tag_ids (Many2many: N-N) vào bảng Game gốc
    tag_ids = fields.Many2many('tutorial.game.tag', string='Tags')
