# pyrefly: ignore [missing-import]
from odoo import api, models, fields, _
from odoo.addons.t4_gate_keeper.utils import check_outside_working_hours

SYNC_STATUS = [
    ('success', 'Success'),
    ('fail', 'Failed'),
    ('updating', 'Updating'),
]

VERIFICATION_TYPE = [
    ('face', 'Face'),
    ('fingerprint', 'Fingerprint'),
    ('card', 'Card'),
    ('password', 'Password'),
    ('other', 'Other'),
]

DIRECTION = [
    ('in', 'Check-in'),
    ('out', 'Check-out'),
]

class GateKeeperAccessLog(models.Model):
    _name = "t4.gate_keeper.access_log"
    _description = "Gate Keeper Access Log"
    _order = "access_time desc"

    controller_id = fields.Many2one(
        comodel_name="t4.gate_keeper.controller",
        string="Controller",
        required=True,
        index=True,
    )

    device_id = fields.Many2one(
        comodel_name="t4.gate_keeper.device",
        string="Device",
        index=True,
    )

    employee_id = fields.Many2one(
        comodel_name="t4.gate_keeper.employee",
        string="Employee",
        index=True,
    )

    access_time = fields.Datetime(
        string="Access Time",
        required=True,
        default=fields.Datetime.now,
    )

    direction = fields.Selection(
        selection=DIRECTION,
        string="Direction",
    )

    verification_type = fields.Selection(
        selection=VERIFICATION_TYPE,
        string="Verification Type",
    )

    sync_status = fields.Selection(
        selection=SYNC_STATUS,
        string="Sync Status",
        default="updating",
        tracking=True,
    )

    branch_id = fields.Many2one(
        comodel_name="t4.gate_keeper.branch",
        related="controller_id.branch_id",
        string="Branch",
        store=True,
        readonly=True,
    )


    area_id = fields.Many2one(
        comodel_name="t4.gate_keeper.area",
        related="device_id.area_id",
        string="Area",
        store=True,
        index=True,
        readonly=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super(GateKeeperAccessLog, self).create(vals_list)
        for record in records:
            if record.area_id:
                record._check_access_security_rules()
        return records

    def _check_access_security_rules(self):
        """
        Check if access is outside normal working hours (e.g. before 08:00 or after 17:00, or weekend).
        If so, create an active t4.gate_keeper.area_warning record.
        """
        self.ensure_one()
        if not self.access_time:
            return

        tz_name = self.branch_id.timezone or self.env.user.tz or 'UTC'
        is_warning, reason_en = check_outside_working_hours(self.access_time, self.env, tz_name=tz_name)


        if is_warning:
            # Translate the reason if needed
            reason = _("Access on weekend (%s)") if "weekend" in reason_en else _("Access outside working hours (%s)")
            # Extract day/time info from reason_en
            param = reason_en.split('(')[-1].split(')')[0]
            reason = reason % param

            warning_type = self.env["t4.gate_keeper.area_warning_type"].search([("code", "=", "invalid_access")], limit=1)
            if warning_type:
                self.env["t4.gate_keeper.area_warning"].create({
                    "area_id": self.area_id.id,
                    "device_id": self.device_id.id,
                    "employee_id": self.employee_id.id,
                    "access_log_id": self.id,
                    "warning_type_id": warning_type.id,
                    "description": _("Employee %s accessed via %s at %s. Reason: %s") % (
                        self.employee_id.name or _("Unknown Employee"),
                        self.device_id.name or _("Unknown Device"),
                        fields.Datetime.to_string(self.access_time),
                        reason
                    )
                })

