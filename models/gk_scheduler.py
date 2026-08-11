# pyrefly: ignore [missing-import]
from odoo import models, fields, api
from datetime import timedelta

WAITING_TIME = 5

class T4GateKeeperScheduler(models.Model):
    _name = 't4.gate_keeper.scheduler'
    _description = 'Gate Keeper Scheduler'

    @api.model
    def cron_update_hardware_status(self):
        timeout = fields.Datetime.now() - timedelta(minutes=5)

        controllers = self.env['t4.gate_keeper.controller']

        offline = controllers.search([
            ('status', '!=', 'offline'),
            '|',
            ('last_heartbeat', '=', False),
            ('last_heartbeat', '<', timeout)
        ])
        if offline:
            offline.write({'status': 'offline'})

        # Update Device Statuses
        devices = self.env['t4.gate_keeper.device']

        # 1. Devices belonging to offline controllers
        controller_offline_devices = devices.search([
            ('controller_id.status', '!=', 'online'),
            ('status', '!=', 'controller_offline')
        ])
        if controller_offline_devices:
            controller_offline_devices.write({'status': 'controller_offline'})

        # 2. Devices belonging to online controllers but haven't been seen recently
        device_offline = devices.search([
            ('controller_id.status', '=', 'online'),
            ('status', '!=', 'offline'),
            '|',
            ('last_heartbeat', '=', False),
            ('last_heartbeat', '<', timeout)
        ])
        if device_offline:
            device_offline.write({'status': 'offline'})


