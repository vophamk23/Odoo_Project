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
            ('last_heartbeat_at', '=', False),
            ('last_heartbeat_at', '<', timeout)
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
            ('last_seen_at', '=', False),
            ('last_seen_at', '<', timeout)
        ])
        if device_offline:
            device_offline.write({'status': 'offline'})

    @api.model
    def cron_sync_missing_employees(self):
        # Find all hr_employee_ids that already have a t4.gate_keeper.employee
        existing_hr_employee_ids = self.env['t4.gate_keeper.employee'].sudo().search([]).mapped('hr_employee_id').ids

        # Search for hr.employee records whose ID is not in the existing list
        missing_employees = self.env['hr.employee'].sudo().search([('id', 'not in', existing_hr_employee_ids)])

        if missing_employees:
            vals_list = []
            for emp in missing_employees:
                vals_list.append({
                    "name": emp.name,
                    "emp_id": emp.emp_id,
                    "hr_employee_id": emp.id,
                })
            self.env["t4.gate_keeper.employee"].sudo().create(vals_list)

