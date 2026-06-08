from odoo import http
from odoo.http import request

class GameController(http.Controller):

    # @http.route: Khai báo đường link URL cho trang web
    # auth='public': Ai cũng xem được, không cần đăng nhập
    # website=True: Sử dụng giao diện có sẵn Header/Footer của Odoo
    @http.route('/games', type='http', auth='public', website=True)
    def game_list(self, **kwargs):
        # Lấy TẤT CẢ bản ghi từ bảng tutorial.game trong Database
        games = request.env['tutorial.game'].sudo().search([])
        
        # Gọi file giao diện (Template XML) và truyền dữ liệu 'games' qua cho nó vẽ
        return request.render('tutorial.game_list_template', {
            'games': games
        })
