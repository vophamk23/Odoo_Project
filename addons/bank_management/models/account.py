from odoo import models, fields, api

class BankAccount(models.Model):
    _name = 'bank.account'
    _description = 'Tài khoản Ngân hàng'
    _rec_name = 'account_number'

    account_number = fields.Char(string='Số tài khoản', required=True, copy=False)
    customer_name = fields.Char(string='Tên Chủ thẻ', required=True)
    account_type = fields.Selection([
        ('checking', 'Thanh toán (Checking)'),
        ('savings', 'Tiết kiệm (Savings)')
    ], string='Loại tài khoản', default='checking', required=True)
    
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', default=lambda self: self.env.company.currency_id)
    balance = fields.Monetary(string='Số dư', compute='_compute_balance', store=True, currency_field='currency_id')
    
    transaction_ids = fields.One2many('bank.transaction', 'account_id', string='Lịch sử Giao dịch')
    transaction_count = fields.Integer(string='Số giao dịch', compute='_compute_transaction_count')

    @api.depends('transaction_ids.amount', 'transaction_ids.state', 'transaction_ids.type')
    def _compute_balance(self):
        for account in self:
            balance = 0.0
            for trans in account.transaction_ids.filtered(lambda t: t.state == 'done'):
                if trans.type == 'deposit':
                    balance += trans.amount
                elif trans.type == 'withdraw':
                    balance -= trans.amount
            account.balance = balance

    @api.depends('transaction_ids')
    def _compute_transaction_count(self):
        for account in self:
            account.transaction_count = len(account.transaction_ids)
