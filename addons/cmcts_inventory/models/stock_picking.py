from odoo import models, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for picking in self:
            # Duyệt qua các dòng sản phẩm (stock.move)
            for move in picking.move_ids:
                product = move.product_id
                if product.tracking == 'serial':
                    # Kiểm tra xem đã nhập chi tiết serial (move_line_ids) chưa
                    has_serial = any(ml.lot_id or ml.lot_name for ml in move.move_line_ids)
                    if not has_serial:
                        raise UserError(
                            _('Sản phẩm "%s" yêu cầu nhập Serial Number trước khi xác nhận phiếu kho.') % product.name
                        )
        # Nếu hợp lệ thì tiếp tục validate bình thường
        return super().button_validate()
