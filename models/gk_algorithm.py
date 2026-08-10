# pyrefly: ignore [missing-import]
from odoo import models, fields, api, _


class GateKeeperAlgorithm(models.Model):
    _name = "t4.gate_keeper.algorithm"
    _description = "Gate Keeper Algorithm"
    _order = "name, version"

    name = fields.Char(
        string="Algorithm Name",
        required=True,
        help="Commercial or technical name of the recognition algorithm.",
    )

    code = fields.Char(
        string="Algorithm Code",
        required=True,
    )

    version = fields.Char(
        string="Algorithm Version",
        help="Version of this recognition algorithm.",
    )
    
    _algorithm_version_unique = models.Constraint(
        "UNIQUE(name, version)",
        _("Algorithm version must be unique per name and version.")
    )

    _algorithm_code_unique = models.Constraint(
        "UNIQUE(code)",
        _("Algorithm code must be unique.")
    )
