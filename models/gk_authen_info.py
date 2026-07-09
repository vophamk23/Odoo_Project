from odoo import models, api, fields, _

class T4GateKeeperAuthInfo (models.Model):
    _name = "t4.gate_keeper.auth_info"
    _description = "Gate Keeper Auth Info"

    emp_id = fields.Many2one(
        "t4.gate_keeper.employee",
        string="Employee"
    )

    # emp_code = fields.Char(string="Employee Code", required=True, copy=True)
    # emp_status = fields.Boolean(string="Employee Status", default=True)
    # description = fields.Text(string="Description")

    # _sql_constraints = [
    #     ('emp_code_unique', 'unique(emp_code)', 'Employee Code must be unique!'),
    # ]
