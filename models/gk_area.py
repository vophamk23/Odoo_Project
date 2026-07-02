# pyrefly: ignore [missing-import]
from odoo import api, fields, models, _


AREA_STATUS = [
    ('warning', 'Warning'),
    ('normal', 'Normal'),
]

ALARM_STATE = [
        ("warning", "Warning"),
        ("resolved", "Resolved"),
    ]

class GateKeeperArea(models.Model):

    _name = "t4.gate_keeper.area"
    _description = "Gate Keeper Area"
    _order = "name"

    name = fields.Char(
        string="Area Name",
        required=True,
        help="Name of the area, e.g., lobby, parking lot, warehouse.",
    )

    branch_id = fields.Many2one(
        "t4.gate_keeper.branch",
        string="Branch",
        required=True,
        ondelete="cascade",
        index=True,
        help="Branch where this area is located.",
    )

    device_ids = fields.One2many(
        "t4.gate_keeper.device",
        "area_id",
        string="Devices",
        readonly="1",
    )

    warning_ids = fields.One2many(
        "t4.gate_keeper.area_warning",
        "area_id",
        string="Warnings",
    )

    status = fields.Selection(
        selection=AREA_STATUS,
        string="Status",
        compute="_compute_status",
        store=True,
        default="normal",
        tracking=True,
    )

    warning_count = fields.Integer(
        string="Warning Count",
        compute="_compute_warning_count",
    )

    @api.depends("warning_ids.state")
    def _compute_status(self):
        for area in self:
            active_warnings = area.warning_ids.filtered(lambda w: w.state == "warning")
            area.status = "warning" if active_warnings else "normal"

    @api.depends("warning_ids")
    def _compute_warning_count(self):
        for area in self:
            area.warning_count = len(area.warning_ids)

    # def action_clear_warnings(self):
    #     for area in self:
    #         active_warnings = area.warning_ids.filtered(lambda w: w.state == "active")
    #         active_warnings.action_resolve()

    def action_view_warnings(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Warnings: %s") % self.name,
            "res_model": "t4.gate_keeper.area_warning",
            "view_mode": "list,form",
            "domain": [("area_id", "=", self.id)],
            "context": {
                "default_area_id": self.id,
            },
        }


class GateKeeperAreaWarning(models.Model):

    _name = "t4.gate_keeper.area_warning"
    _description = "Gate Keeper Area Warning"
    _order = "create_date desc"

    area_id = fields.Many2one(
        "t4.gate_keeper.area",
        string="Area",
        required=True,
        ondelete="cascade",
        index=True,
    )
    device_id = fields.Many2one(
        "t4.gate_keeper.device",
        string="Device",
        ondelete="set null",
    )
    employee_id = fields.Many2one(
        "t4.gate_keeper.employee",
        string="Employee",
        ondelete="set null",
    )
    access_log_id = fields.Many2one(
        "t4.gate_keeper.access_log",
        string="Related Access Log",
        ondelete="set null",
    )
    warning_type_id = fields.Many2one(
        "t4.gate_keeper.area_warning_type",
        string="Warning Type",
        required=True,
        ondelete="restrict",
    )
    description = fields.Text(string="Description")

    state = fields.Selection(
        selection=ALARM_STATE, 
        string="State", 
        default="warning", 
        required=True, 
        index=True
    )
    resolved_by_id = fields.Many2one(
        "res.users",
        string="Resolved By",
        readonly=True,
    )
    resolved_at = fields.Datetime(
        string="Resolved At",
        readonly=True,
    )
    resolution_notes = fields.Text(string="Resolution Notes")

    def action_resolve(self):
        for warning in self:
            warning.write({
                "state": "resolved",
                "resolved_by_id": self.env.user.id,
                "resolved_at": fields.Datetime.now(),
            })


class GateKeeperAreaWarningType(models.Model):
    _name = "t4.gate_keeper.area_warning_type"
    _description = "Gate Keeper Area Warning Type"
    _order = "name"

    name = fields.Char(string="Warning Type Name", required=True)
    code = fields.Char(string="Code", required=True, help="Code used in business logic to identify the warning type.")
    description = fields.Text(string="Description")

    _code_uniq = models.Constraint(
        "UNIQUE(code)",
        "Warning type code must be unique!"
    )

