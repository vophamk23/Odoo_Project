from odoo import models, _
from odoo.exceptions import UserError
import unicodedata
import re

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        def remove_accents(input_str):
            nfkd_form = unicodedata.normalize('NFKD', input_str)
            return nfkd_form.encode('ASCII', 'ignore').decode('utf-8')

        for picking in self:
            for move in picking.move_ids:
                product = move.product_id
                if product.tracking == 'serial':
                    has_serial = any(ml.lot_id or ml.lot_name for ml in move.move_line_ids)
                    if not has_serial:
                        if picking.picking_type_id.code == 'incoming':
                            qty_needed = int(move.product_uom_qty)
                            move.move_line_ids.filtered(lambda ml: not ml.lot_id and not ml.lot_name).unlink()
                            
                            clean_name = remove_accents(product.name)
                            words = [re.sub(r'[^A-Za-z0-9]', '', w) for w in clean_name.split()]
                            words = [w for w in words if w]
                            prefix = "-".join(words[:2]) if len(words) >= 2 else "-".join(words)
                            if not prefix:
                                prefix = "SN"
                                
                            existing_lots = self.env['stock.lot'].search([
                                ('product_id', '=', product.id),
                                ('name', '=like', f'{prefix}-%')
                            ])
                            max_seq = 0
                            for lot in existing_lots:
                                try:
                                    seq_str = lot.name.split('-')[-1]
                                    seq = int(seq_str)
                                    if seq > max_seq:
                                        max_seq = seq
                                except ValueError:
                                    pass
                                    
                            next_seq = max_seq + 1
                            for i in range(qty_needed):
                                lot_name = f"{prefix}-{next_seq:04d}"
                                self.env['stock.move.line'].create({
                                    'move_id': move.id,
                                    'picking_id': picking.id,
                                    'product_id': product.id,
                                    'location_id': move.location_id.id,
                                    'location_dest_id': move.location_dest_id.id,
                                    'quantity': 1,
                                    'lot_name': lot_name,
                                })
                                next_seq += 1
                        else:
                            raise UserError(
                                _('Sản phẩm "%s" yêu cầu nhập Serial Number trước khi xác nhận phiếu kho.') % product.name
                            )
        return super().button_validate()
