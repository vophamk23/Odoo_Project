from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_read_by_customer = fields.Boolean(string='Read by Customer', default=False)
