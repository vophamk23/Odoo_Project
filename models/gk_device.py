# pyrefly: ignore [missing-import]
from odoo import api, _, fields, models
from odoo.addons.t4_coreapi.utils import endpoint, get_params, get_body
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

DEVICE_STATUS = [
    ("online", "Online"),
    ("offline", "Offline"),
    ("controller_offline", "Controller Offline"),
]

ALLOWED_CREATE_FIELDS = [
    # REQUIRE
    "controller_id",
    "serial_number",
    
    # OPTIONAL
    "name",
    "area_id",
    "vendor",
    "device_model_id",
    "port_or_channel",
    "firmware_version",
    "system_version",
    "status",
    "last_seen_at",
    "installed_at",
    "last_sync_at",
    "employee_sync_status"
]


class GateKeeperDevice(models.Model):
    _name = "t4.gate_keeper.device"
    _description = "Gate Keeper Device"
    _order = "controller_id, id"

    name = fields.Char(
        string="Device Name",
        required=True,
        help="Human-readable name used to identify this device.",
    )

    controller_id = fields.Many2one(
        comodel_name="t4.gate_keeper.controller",
        string="Controller",
        required=True,
        ondelete="cascade",
        index=True,
        help="Controller that manages this device.",
    )

    serial_number = fields.Char(
        string="Serial Number",
        copy=False,
        index=True,
        required=True,
        help="Physical serial number of the device.",
    )

    branch_id = fields.Many2one(
        comodel_name="t4.gate_keeper.branch",
        related="controller_id.branch_id",
        string="Branch",
        store=True,
        readonly=True,
    )

    timezone = fields.Selection(
        related="controller_id.branch_id.timezone",
        string="Timezone",
        readonly=True,
        store=True,
    )

    area_id = fields.Many2one(
        comodel_name="t4.gate_keeper.area",
        string="Area",
        domain="[('branch_id', '=', branch_id)]",
        help="Area within the branch where this device is located.",
    )

    vendor = fields.Char(
        string="Vendor",
        help="Device manufacturer, for example ZKTeco, Hikvision, or Suprema.",
    )

    device_model_id = fields.Many2one(
        comodel_name="t4.gate_keeper.device_model",
        string="Device Model",
        help="Specific model name or number of the hardware device.",
    )

    port_or_channel = fields.Char(
        string="Port / Channel",
        help="Physical port or channel on the controller, for example relay 1 or input 2.",
    )

    firmware_version = fields.Char(
        string="Firmware Version",
        help="Firmware version installed on the device.",
    )

    system_version = fields.Char(
        string="System Version",
        help="Operating system or embedded application version installed on the device.",
    )

    algorithm_ids = fields.Many2many(
        related="device_model_id.algorithm_ids",
        readonly=True,
        string="Supported Algorithms",
        help="Face, fingerprint, or other recognition algorithms supported by this device.",
    )

    status = fields.Selection(
        selection=DEVICE_STATUS,
        string="Status",
        default="offline",
        tracking=True,
    )

    last_seen_at = fields.Datetime(
        string="Last Seen",
        readonly=True,
        help="Last time the controller received a response from this device.",
    )

    installed_at = fields.Date(
        string="Installed On",
    )

    last_sync_at = fields.Datetime(
        string="Last Sync",
        readonly=True,
        help="Last successful permission or template synchronization.",
    )

    employee_sync_status = fields.Selection(
        selection=[
            ("synced", "Synced"),
            ("out_of_sync", "Out of Sync"),
        ],
        string="Employee Sync Status",
        compute="_compute_employee_sync_status",
        help="Indicates whether the device has synchronized the latest employee updates.",
    )

    def _compute_employee_sync_status(self):
        # Placeholder logic: Currently unhandled API, just return out_of_sync if not set
        for device in self:
            if device.last_sync_at:
                device.employee_sync_status = "synced"
            else:
                device.employee_sync_status = "out_of_sync"

    @api.model_create_multi
    def create(self, vals_list):
        records = super(GateKeeperDevice, self).create(vals_list)
        for record in records:
            if record.status in ('offline', 'controller_offline'):
                record._handle_device_issue_warning()
        return records

    def write(self, vals):
        res = super(GateKeeperDevice, self).write(vals)
        if 'status' in vals or 'area_id' in vals:
            for record in self:
                if record.status in ('offline', 'controller_offline'):
                    record._handle_device_issue_warning()
                elif record.status == 'online':
                    record._resolve_device_issue_warnings()
        return res

    def _handle_device_issue_warning(self):
        self.ensure_one()
        if not self.area_id:
            self._resolve_device_issue_warnings()
            return

        warning_type = self.env["t4.gate_keeper.area_warning_type"].search([("code", "=", "device_issue")], limit=1)
        if not warning_type:
            return

        active_warning = self.env["t4.gate_keeper.area_warning"].search([
            ("device_id", "=", self.id),
            ("warning_type_id", "=", warning_type.id),
            ("state", "=", "warning"),
        ], limit=1)

        if active_warning:
            if active_warning.area_id != self.area_id:
                active_warning.write({"area_id": self.area_id.id})
        else:
            status_label = dict(self._fields['status'].selection).get(self.status, self.status)
            self.env["t4.gate_keeper.area_warning"].create({
                "area_id": self.area_id.id,
                "device_id": self.id,
                "warning_type_id": warning_type.id,
                "description": _("Device %s is offline. Status: %s") % (self.name, status_label),
            })

    def _resolve_device_issue_warnings(self):
        self.ensure_one()
        warning_type = self.env["t4.gate_keeper.area_warning_type"].search([("code", "=", "device_issue")], limit=1)
        if not warning_type:
            return

        active_warnings = self.env["t4.gate_keeper.area_warning"].search([
            ("device_id", "=", self.id),
            ("warning_type_id", "=", warning_type.id),
            ("state", "=", "warning"),
        ])
        if active_warnings:
            active_warnings.action_resolve()

    _device_serial_number_unique = models.Constraint(
        "UNIQUE(serial_number)",
        _("Device Serial Number must be unique!")
    )

    # REGISTER
    @api.model
    def _filter_vals_for_create (self, vals):
        return {
            key:value 
            for key, value in vals.items()
            if key in ALLOWED_CREATE_FIELDS
        }

    @api.model
    def _find_controller_by_sn(self, controller_sn):
        return self.env['t4.gate_keeper.controller'].sudo().search([
            ('serial_number', '=', controller_sn)
        ], limit=1)

    @api.model
    def _device_register(self, vals_list):
        vals_list = [vals_list] if isinstance(vals_list, dict) else vals_list

        filtered_vals_list = []
        for vals in vals_list:
            if 'controller_sn' in vals:
                controller = self._find_controller_by_sn(vals["controller_sn"])
                if not controller:
                    raise ValidationError("Can not find controller serial number")
                vals["controller_id"] = controller.id

            if not vals.get("serial_number") or not vals.get("controller_id") or not vals.get("name"):
                raise ValidationError("Device Register must contain (name,controller_id,serial_number)")

            filtered_vals_list.append(self._filter_vals_for_create(vals))
     
        return self.create(filtered_vals_list)

