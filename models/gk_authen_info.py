from odoo import models, api, fields, _

class T4GateKeeperAuthInfo (models.Model):
    _name = "t4.gate_keeper.auth_info"
    _description = "Gate Keeper Auth Info"

    emp_id = fields.Many2one(
        "t4.gate_keeper.employee",
        string="Employee"
    )

