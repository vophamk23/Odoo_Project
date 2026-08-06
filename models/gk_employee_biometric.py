# pyrefly: ignore [missing-import]
from odoo import models, fields, api, _

BIOMETRIC_TYPE = [
    ("character", "Character"),
    ("base64", "Binary")
]

class GateKeeperEmployeeBiometric(models.Model):
    _name = "t4.gate_keeper.employee.biometric"
    _description = "Employee Biometric"
    _order = "employee_id, biometric_type, finger_index"

    employee_id = fields.Many2one(
        comodel_name="t4.gate_keeper.employee",
        string="Employee",
        required=True,
        ondelete="cascade",
        index=True,
    )

    device_model_id = fields.Many2one(
        comodel_name="t4.gate_keeper.device_model",
        string="Device Model",
        required=True,
        ondelete="cascade",
        index=True,
    )

    algorithm_id = fields.Many2one(
        comodel_name="t4.gate_keeper.algorithm",
        string="Algorithm",
        ondelete="restrict",
        index=True,
    )

    biometric_type = fields.Selection(
        selection=BIOMETRIC_TYPE,
        string="Biometric Type",
    )

    binary_template = fields.Binary(
        string="Biometric Template",
        help="Biometric template data (e.g., face template or fingerprint template).",
    )

    char_template = fields.Char(
        string="Biometric Template",
        help="Biometric template data (e.g., face template or fingerprint template).",
    )

    finger_index = fields.Integer(
        string="Finger/Slot Index",
        default=0,
        help="Index of the finger (usually 0-9) or slot number for the biometric template.",
    )

    _biometric_template_not_null = models.Constraint(
        "binary_template IS NOT NULL OR char_template IS NOT NULL",
        "Atleast 1 field not null"
    )

    _employee_biometric_unique = models.Constraint(
        "UNIQUE(employee_id, algorithm_id, finger_index)",
        _("A biometric template already exists for this employee, algorithm, and finger/slot index.")
    )
