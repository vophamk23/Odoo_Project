# pyrefly: ignore [missing-import]
from odoo import models, fields

class GateKeeperDeviceModel(models.Model):
    _name = "t4.gate_keeper.device_model"
    _description = "Gate Keeper Device Model"
    _order = "name"

    name = fields.Char(
        string="Model Name",
        required=True,
        help="Specific model name or number of the hardware device, e.g., SpeedFace V5L.",
    )

    version = fields.Char(
        string="Version",
        help="Version of model"
    )