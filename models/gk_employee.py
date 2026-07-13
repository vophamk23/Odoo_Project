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
        max_width=1920,
        max_height=1920,
    )

    name = fields.Char(
        string="Employee name",
    )

    emp_id = fields.Integer(
        string="Employee ID",
        readonly=True,
    )

    branch_id = fields.Many2one(
        comodel_name="t4.gate_keeper.branch",
        string="Branch",
        help="If empty, all controllers can sync this employee. If set, only controllers in this branch can sync.",
    )

    hr_employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="HR Employee",
        ondelete="cascade",
        index=True,
        help="Linked HR Employee. Used to sync name updates.",
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

    # @api.depends("biometric_ids")
    # def _compute_biometric_count(self):
    #     for rec in self:
    #         rec.biometric_count = len(rec.biometric_ids)

    # def action_view_biometrics(self):
    #     self.ensure_one()
    #     return {
    #         "type": "ir.actions.act_window",
    #         "name": "Biometrics",
    #         "res_model": "t4.gate_keeper.employee.biometric",
    #         "view_mode": "list,form",
    #         "domain": [("employee_id", "=", self.id)],
    #         "context": {"default_employee_id": self.id},
    #     }

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
                "Không được phép thay đổi mã nhân viên."
            )
        return super().write(vals)
