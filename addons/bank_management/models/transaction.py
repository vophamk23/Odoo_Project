from odoo import models, fields, api, exceptions

class BankTransaction(models.Model):
    _name = 'bank.transaction'
    _description = 'Giao dịch Ngân hàng'
    _order = 'date desc, id desc'

    name = fields.Char(string='Mã Giao dịch', required=True, copy=False, readonly=True, default='Mới')
    account_id = fields.Many2one('bank.account', string='Tài khoản', required=True)
    currency_id = fields.Many2one(related='account_id.currency_id', store=True)
    
    type = fields.Selection([
        ('deposit', 'Nạp tiền'),
        ('withdraw', 'Rút tiền')
    ], string='Loại giao dịch', required=True, default='deposit')
    
    amount = fields.Monetary(string='Số tiền', required=True, currency_field='currency_id')
    date = fields.Datetime(string='Ngày giao dịch', default=fields.Datetime.now, required=True)
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('done', 'Hoàn thành'),
        ('cancelled', 'Đã hủy')
    ], string='Trạng thái', default='draft', required=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Mới') == 'Mới':
                vals['name'] = self.env['ir.sequence'].next_by_code('bank.transaction') or 'GD-MỚI'
        return super().create(vals_list)

    def action_done(self):
        for record in self:
            if record.type == 'withdraw' and record.account_id.balance < record.amount:
                raise exceptions.UserError("Số dư tài khoản không đủ để thực hiện giao dịch rút tiền này!")
            record.state = 'done'

    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
