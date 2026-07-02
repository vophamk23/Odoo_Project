# pyrefly: ignore [missing-import]
import pytz
from odoo import fields, models

class GateKeeperBranch(models.Model):
    _name = "t4.gate_keeper.branch"
    _description = "Gate Keeper Branch"
    _order = "name"

    name = fields.Char(
        string="Branch Name",
        required=True,
        help="Name of the branch.",
    )

    timezone = fields.Selection(
        selection=lambda self: [(tz, tz) for tz in pytz.common_timezones],
        string="Timezone",
        default="Asia/Ho_Chi_Minh",
        required=True,
        help="Timezone of this branch, used to evaluate local time of device logs.",
    )

    address = fields.Text(
        string="Address",
    )
    
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    
    controller_ids = fields.One2many(
        "t4.gate_keeper.controller",
        "branch_id",
        string="Controllers",
    )

    area_ids = fields.One2many(
        "t4.gate_keeper.area",
        "branch_id",
        string="Areas",
    )

    device_ids = fields.Many2many(
        "t4.gate_keeper.device",
        compute="_compute_device_ids",
        string="Devices",
        store=False,
    )

    def _compute_device_ids(self):
        for branch in self:
            branch.device_ids = branch.controller_ids.mapped("device_ids")
