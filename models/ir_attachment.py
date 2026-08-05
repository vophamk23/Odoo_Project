from odoo import models, fields, api

class IrAttachment(models.Model):
    _inherit = "ir.attachment"
    photo_type = fields.Selection([
        ("jpg", "JPEG"),
        ("png", "PNG"),
        ("other", "Other"),
    ])