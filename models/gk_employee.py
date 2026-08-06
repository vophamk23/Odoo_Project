# pyrefly: ignore [missing-import]
from odoo import _, api, fields, models
# pyrefly: ignore [missing-import]
from odoo.exceptions import ValidationError
import uuid


class T4GateKeeperEmployee(models.Model):
    _name = "t4.gate_keeper.employee"
    _description = "Employee"

    avatar = fields.Image(
        string="Avatar",
        max_width=400,
        max_height=400,
        attachment = True
    )

    name = fields.Char(
        string="Employee name",
    )
    password = fields.Char(
        string="Employee password"
    )
    card_id = fields.Char(
        string="Employee card serial"
    )
    privilege = fields.Integer(
        string="Privilege"
    )

    emp_id = fields.Integer(
        string="Employee ID",
        readonly=False,
    )

    branch_id = fields.Many2one(
        comodel_name="t4.gate_keeper.branch",
        string="Branch",
        help="If empty, all controllers can sync this employee. If set, only controllers in this branch can sync.",
    )


    biometric_ids = fields.One2many(
        comodel_name="t4.gate_keeper.employee.biometric",
        inverse_name="employee_id",
        string="Biometrics",
    )

    biometric_count = fields.Integer(
        string="Biometric Count",
        compute="_compute_biometric_count",
    )

    _emp_id_constraint = models.Constraint(
        "UNIQUE(emp_id)",
        _("Employee ID must be unique.")
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env["ir.sequence"]
        for vals in vals_list:
            if "emp_id" not in vals:
                vals["emp_id"] = int(sequence.next_by_code("t4.gate_keeper.employee"))
            
        return super().create(vals_list)

    def write(self, vals):
        if 'emp_id' in vals:
            raise ValidationError(
                "Employee codes cannot be changed."
            )
        return super().write(vals)
