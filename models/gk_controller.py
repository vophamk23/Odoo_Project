import logging

# pyrefly: ignore [missing-import]
from odoo import api, _, fields, models
# pyrefly: ignore [missing-import]
from odoo.addons.t4_coreapi.utils import endpoint, get_body
# pyrefly: ignore [missing-import]
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


CONTROLLER_STATUS = [
    ("online", "Online"),
    ("offline", "Offline"),
    ("maintenance", "Maintenance"),
    ("disabled", "Disabled"),
]


ALLOWED_FIELDS = [  # fields of t4 gatekeeper controller if you add or delete pls change this list
    'name', 
    'serial_number', 
    'branch_id', 
    'hardware_model', 
    'firmware_version', 
    'ip_address', 
    'mac_address', 
    'connection_type', 
    'status', 
    'installed_at'
]

class T4GateKeeperController(models.Model):
    _name = "t4.gate_keeper.controller"
    _description = "Gate Keeper Controller"
    _order = "last_heartbeat_at desc, id desc"

    name = fields.Char(
        string="Controller Name",
        required=True,
        help="Human-readable name used to identify this controller.",
    )

    serial_number = fields.Char(
        string="Serial Number",
        required=True,
        copy=False,
        index=True,
        help="Physical serial number used for maintenance and hardware replacement checks.",
    )

    branch_id = fields.Many2one(
        "t4.gate_keeper.branch",
        string="Branch",
        required=True,
        index=True,
    )

    timezone = fields.Selection(
        related="branch_id.timezone",
        string="Timezone",
        readonly=True,
        store=True,
    )


    device_ids = fields.One2many(
        "t4.gate_keeper.device",
        "controller_id",
        string="Devices",
    )

    hardware_model = fields.Char(
        string="Hardware Model",
        help="Controller model or product line.",
    )

    firmware_version = fields.Char(
        string="Firmware Version",
        help="Firmware version installed on the controller.",
    )

    ip_address = fields.Char(
        string="IP Address",
        help="Connection address when the controller uses TCP/IP.",
    )

    mac_address = fields.Char(
        string="MAC Address",
        help="Hardware identifier useful when DHCP changes the IP address.",
    )

    connection_type = fields.Selection(
        selection=[
            ("tcp_ip", "TCP/IP"),
            ("rs485", "RS485"),
            ("wiegand", "Wiegand"),
        ],
        string="Connection Type",
        required=True,
        default="tcp_ip",
        help="Communication method used by this controller.",
    )

    status = fields.Selection(
        selection=CONTROLLER_STATUS,
        string="Status",
        default="offline",
        tracking=True,
    )

    last_heartbeat_at = fields.Datetime(
        string="Last Heartbeat",
        readonly=True,
        help="Last time this controller reported that it was online.",
    )

    last_sync_at = fields.Datetime(
        string="Last Sync",
        readonly=True,
        help="Last successful permission or template synchronization.",
    )

    installed_at = fields.Date(
        string="Installed On",
        help="Installation date used for maintenance planning.",
    )

    employee_sync_status = fields.Selection(
        selection=[
            ("synced", "Synced"),
            ("out_of_sync", "Out of Sync"),
        ],
        string="Employee Sync Status",
        compute="_compute_employee_sync_status",
        help="Indicates whether the controller has synchronized the latest employee updates.",
    )

    def _compute_employee_sync_status(self):
        for controller in self:
            domain = controller._get_employee_sync_domain(controller)
            unsynced_count = self.env["t4.gate_keeper.employee"].search_count(domain)
            if unsynced_count == 0:
                controller.employee_sync_status = "synced"
            else:
                controller.employee_sync_status = "out_of_sync"

    _controller_serial_number_unique = models.Constraint(
        "UNIQUE(serial_number)",
        _("Controller serial number must be unique.")
    )

    ################################## ENDPOINT ###############################################
    def _find_controller(self, controller_id):
        return self.search([
            ("serial_number", "=", controller_id),
        ], limit=1)
    
    def _find_device(self, controller_id, device_id):
        return self.env["t4.gate_keeper.device"].search([
            ("serial_number", "=", device_id),
            ("controller_id", "=", controller_id),
        ], limit=1)
    

    @endpoint(name="ControllerHeartbeat")
    def controller_heartbeat(self):
        body = get_body(self.env)
        controller_id = body.get("controller_sn", False)

        controller = self._find_controller(controller_id)
        if not controller:
            raise ValidationError(f"Can not find controller with id {controller_id}")
        devices = body.get("devices", [])
        # if not devices:
        #     raise ValidationError("Devices list is required.")
        for device in devices:
            device_id = device.get("device_sn")
            device_status = device.get("status")
            if not device_id:
                raise ValidationError("Device serial number is required.")

            if not device_status:
                raise ValidationError(f"Device status is required for device {device_id}")
            
            allowed_status = dict(self.env["t4.gate_keeper.device"]._fields["status"].selection).keys()
            if device_status not in allowed_status:
                raise ValidationError(f"Invalid device status for device {device_id}")

            if not device_id or not device_status:
               continue
            
            device_record = self._find_device(controller.id, device_id)
            if device_record:
                device_record.write({"status": device_status})



        heartbeat_at = fields.Datetime.now()
        controller.write({
            "last_heartbeat_at": heartbeat_at,
            "status": "online",
        })


    @endpoint(name="ControllerEmployeeSync")
    def controller_employee_sync(self):
        body = get_body()
        serial_number = body.get("controller_sn", False)

        if not serial_number:
            raise ValidationError(_("Controller ID is required."))

        controller = self._find_controller(serial_number)
        if not controller:
            raise ValidationError(_("Can not find controller with ID %s") % serial_number)
        
        #Paging
        page = body.get("page", 1)
        page_size = 15
        offset = (page - 1) * page_size

        domain = self._get_employee_sync_domain(controller)
        employees = self._get_employees_to_sync(domain, offset=offset, limit=page_size)

        if employees:
            sync_time = max(employees.mapped("write_date"))
        else:
            sync_time = controller.last_sync_at

        if not employees:
            return {
                "message": _("Employee sync completed"),
                "data": {
                    "sync_timestamp": sync_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "new": [],
                    "update": [],
                    "deleted": [],
                }
            }
            
        new = []
        update = []
        deleted = []
        for emp in employees:
            if not emp.active:
                deleted.append(emp)
            elif not controller.last_sync_at:
                new.append(emp)
            elif emp.create_date > controller.last_sync_at:
                new.append(emp)
            else:
                update.append(emp)

        
        return {
            "message": _("Employee sync completed"),
            "data": {
                "sync_timestamp": sync_time.strftime("%Y-%m-%d %H:%M:%S"),
                "page": page,
                "page_size": page_size,
                "new": [
                        {
                        "id": emp.emp_id,
                        "name": emp.name,
                        "branch_id": emp.branch_id.id if emp.branch_id else None,
                    }
                    for emp in new
                ],
                "update": [
                    {
                        "id": emp.emp_id,
                        "name": emp.name,
                        "branch_id": emp.branch_id.id if emp.branch_id else None,
                    }
                    for emp in update
                ],
                "deleted": [
                    {
                        "id": emp.emp_id,
                        "name": emp.name,
                        "branch_id": emp.branch_id.id if emp.branch_id else None,
                    }
                    for emp in deleted
                ],
            }
        }
    
    @endpoint(name="ControllerEmployeeSyncStatus")
    def controller_employee_sync_status(self):
        body = get_body()
        serial_number = body.get("controller_sn", False)

        if not serial_number:
            raise ValidationError(_("Controller ID is required."))

        controller = self._find_controller(serial_number)
        if not controller:
            raise ValidationError(_("Can not find controller with ID %s") % serial_number)

        domain = self._get_employee_sync_domain(controller)
        update = bool(self._get_employees_to_sync(domain, limit=1))

        return {
            "message": _("Success"),
            "data": {
                "update": update,
            }
        }

    def write(self, vals):
        res = super(T4GateKeeperController, self).write(vals)
        if 'status' in vals:
            for controller in self:
                if controller.status == 'online':
                    devices_to_update = controller.device_ids.filtered(lambda d: d.status == 'controller_offline')
                    if devices_to_update:
                        devices_to_update.write({'status': 'online'})
                else:
                    devices_to_update = controller.device_ids.filtered(lambda d: d.status != 'controller_offline')
                    if devices_to_update:
                        devices_to_update.write({'status': 'controller_offline'})
        return res

    def _get_employee_sync_domain(self, controller):
        domain = [
            '|', 
            ('branch_id', '=', False), 
            ('branch_id', '=', controller.branch_id.id)
        ]
        
        if controller.last_sync_at:
            domain.append(('write_date', '>', controller.last_sync_at))
            
        return domain

    def _get_employees_to_sync(self, domain, offset=0, limit=None):
        return self.env["t4.gate_keeper.employee"].search(domain,
                                                          order="write_date, id",
                                                          offset=offset,
                                                          limit=limit)

    #### Register 

    @endpoint("ControllerStatus")
    def _controller_status(self):
        body = get_body()
        serial_number = body.get("serial_number")

        if not serial_number:
            raise ValidationError(_("Serial number is required."))

        controller = self.sudo().search_read(
            [("serial_number", "=", serial_number)],
            ["id", "serial_number"],
            limit=1
        )

        if not controller:
            return {
                "message": "Controller not found.",
                "data": {
                    "is_registered": False,
                }
            }

        controller_id = controller[0]["id"]
        
        devices = self.env["t4.gate_keeper.device"].sudo().search_read(
            [("controller_id", "=", controller_id)],
            ["serial_number"]
        )

        return {
            "message": "Success.",
            "data": {
                "is_registered": True,
                "controller_sn": controller[0]["serial_number"],
                "devices": [d["serial_number"] for d in devices if d.get("serial_number")]
            }
        }

    def _find_branch_by_code(self, branch_code):
        return self.env['t4.gate_keeper.branch'].sudo().search([
            ("code", "=", branch_code)
        ], limit=1)

    @endpoint("ControllerRegister")
    def _controller_register(self):
        body = get_body()

        if "branch_code" in body:
            branch_code = body.pop("branch_code")
            body["branch_id"] = self._find_branch_by_code(branch_code).id

        vals = {key: body[key] for key in ALLOWED_FIELDS if key in body}    

        if 'serial_number' not in vals or 'branch_id' not in vals:
            raise ValidationError("Missing required fields (serial_number, branch_id)")

        if not vals['branch_id']:
            raise ValidationError("Invalid branch_code provided")   

        new_controller = self.env['t4.gate_keeper.controller'].sudo().create(vals)

        return {
            "message": "Controller registered successfully",
            "data": {
                "id": new_controller.id
            }
        }

    @endpoint('DeviceRegister')
    def _device_register(self):
        body = get_body()
        vals_list = body['devices']

        self.env['t4.gate_keeper.device']._device_register(vals_list)

        return {
            "message": "Devices register successfully"
        }

    ##### Biometric
    @endpoint(name="EmployeeBiometricGet")
    def employee_biometric_get(self):
        body = get_body()
        serial_number = body.get("controller_sn", False)

        if not serial_number:
            raise ValidationError(_("Controller ID is required."))

        controller = self._find_controller(serial_number)
        if not controller:
            raise ValidationError(_("Can not find controller with ID %s") % serial_number)
        
        employee_id = body.get("employee_id", False)
        if not employee_id:
            raise ValidationError(_("Employee ID is required."))

        employee = self.env["t4.gate_keeper.employee"].search([
            ("emp_id", "=", employee_id),
            "|", 
            ("branch_id", "=", False), 
            ("branch_id", "=", controller.branch_id.id)
        ], limit=1)

        biometric_data = []
        if employee:
            for biometric in employee.biometric_ids:
                biometric_data.append({
                    "algorithm": biometric.algorithm_id.name,
                    "biometric_type": biometric.biometric_type,
                    "finger_index": biometric.finger_index,
                    "template": biometric.template.decode or None,
                })

        return {
            "message": _("Success"),
            "data": biometric_data
        }
    
    # @endpoint(name="EmployeeBiometricUpdate")
    # def employee_biometric_update(self):
    #     body = get_body()
    #     serial_number = body.get("controller_sn", False)

    #     if not serial_number:
    #         raise ValidationError(_("Controller ID is required."))

    #     controller = self._find_controller(serial_number)
    #     if not controller:
    #         raise ValidationError(_("Can not find controller with ID %s") % serial_number)
        
    #     employee_id = body.get("employee_id", False)
    #     if not employee_id:
    #         raise ValidationError(_("Employee ID is required."))
        
    #     biometric_data = body.get("biometric_data", [])
        
    #     allowed_biometric_types = dict(self.env["t4.gate_keeper.employee.biometric"]._fields["biometric_type"].selection).keys()
        

    
    #### Config
    @endpoint(name="ControllerGetConfig")
    def controller_get_config(self):
        body = get_body()
        serial_number = body.get("controller_sn", False)

        if not serial_number:
            raise ValidationError(_("Controller ID is required."))

        controller = self._find_controller(serial_number)
        if not controller:
            raise ValidationError(_("Can not find controller with ID %s") % serial_number)
        
        device_list = controller.device_ids
        device_data = []

        for device in device_list:
            device_data.append({
                "device_sn": device.serial_number,
                "device_model": device.device_model_id.name if device.device_model_id else "N/A",
                "assigned_area": device.area_id.name if device.area_id else "N/A",
                "status": device.status,
                "connection_type": device.connection_type,
                "port/channel": device.port_or_channel,
                "supported_biometric_types": [biometric.name for biometric in device.algorithm_ids],
            })

        return {
            "message": _("Success"),
            "timezone": controller.timezone,
            "data": {
                "devices": device_data
            }
        }
    
    @endpoint(name="ControllerSyncAck")
    def controller_sync_ack(self):
        body = get_body()
        serial_number = body.get("controller_sn", False)

        if not serial_number:
            raise ValidationError(_("Controller ID is required."))
        
        controller = self._find_controller(serial_number)
        if not controller:
            raise ValidationError(_("Can not find controller with ID %s") % serial_number)
        
        timestamp = body.get("timestamp", False)
        if not timestamp:
            raise ValidationError(_("Timestamp is required."))
        
        try:
            fields.Datetime.to_datetime(timestamp)
        except ValueError:
            raise ValidationError(_("Invalid timestamp format. Expected format: YYYY-MM-DD HH:MM:SS"))
        
        if not controller.last_sync_at or fields.Datetime.to_datetime(timestamp) > controller.last_sync_at:
            controller.write({"last_sync_at": fields.Datetime.to_datetime(timestamp)})

        return {
            "message": _("Success")
        }



