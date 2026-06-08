# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models


class ResPartner(models.Model):
    # Tạo mà _name
    # Kế thừa từ model có sẵn là _inherit
    _inherit = 'res.partner'
